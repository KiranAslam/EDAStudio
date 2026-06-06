import chardet
import pandas as pd
from pandas.api import types as pdt
from config.limits import LIMITS


def _looks_like_date_values(series: pd.Series) -> bool:
    if series.dtype != object:
        return False
    sample = series.dropna().head(100)
    if len(sample) == 0:
        return False
    parsed = pd.to_datetime(sample, errors="coerce")
    return parsed.notna().sum() / len(sample) > 0.8


def _build_optimized_dtype_map(sample_df: pd.DataFrame) -> dict:
    dtype_map = {}
    for col in sample_df.columns:
        col_sample = sample_df[col]
        n_unique = col_sample.nunique()
        n_total = len(col_sample.dropna())
        if n_total == 0:
            continue
        unique_ratio = n_unique / n_total
        if col_sample.dtype == object:
            if _looks_like_date_values(col_sample):
                continue
            if unique_ratio < LIMITS["CATEGORY_CONVERSION_THRESHOLD"]:
                dtype_map[col] = "category"
        elif pdt.is_integer_dtype(col_sample.dtype):
            col_min, col_max = col_sample.min(), col_sample.max()
            # Use pandas nullable integer dtypes so NA values are allowed
            if col_min >= 0 and col_max <= 255:
                dtype_map[col] = "UInt8"
            elif col_min >= 0 and col_max <= 65535:
                dtype_map[col] = "UInt16"
            elif col_min >= 0 and col_max <= 4_294_967_295:
                dtype_map[col] = "UInt32"
            elif col_min >= -128 and col_max <= 127:
                dtype_map[col] = "Int8"
            elif col_min >= -32768 and col_max <= 32767:
                dtype_map[col] = "Int16"
            elif col_min >= -2_147_483_648 and col_max <= 2_147_483_647:
                dtype_map[col] = "Int32"
            else:
                dtype_map[col] = "Int64"
        elif pdt.is_float_dtype(col_sample.dtype):
            if col_sample.abs().max() < 3.4e38:
                dtype_map[col] = "float32"
    return dtype_map


def _optimize_dataframe_memory(df: pd.DataFrame) -> pd.DataFrame:
    for col in df.select_dtypes(include="object").columns:
        if _looks_like_date_values(df[col]):
            continue
        n_unique_ratio = df[col].nunique() / max(len(df[col].dropna()), 1)
        if n_unique_ratio < LIMITS["CATEGORY_CONVERSION_THRESHOLD"]:
            df[col] = df[col].astype("category")
    if df.columns.duplicated().any():
        cols = list(df.columns)
        seen: dict[str, int] = {}
        new_cols = []
        for c in cols:
            if c in seen:
                seen[c] += 1
                new_cols.append(f"{c}_{seen[c]}")
            else:
                seen[c] = 0
                new_cols.append(c)
        df.columns = new_cols
    return df


def load_with_memory_optimization(uploaded_file, file_type: str) -> pd.DataFrame:
    read_kwargs = {"low_memory": False, "on_bad_lines": "warn"}

    if file_type == "parquet":
        df = pd.read_parquet(uploaded_file)
    elif file_type in ("csv", "tsv"):
        sep = "\t" if file_type == "tsv" else ","
        # Attempt to detect file encoding to avoid UnicodeDecodeError on upload
        def _detect_encoding(f) -> str | None:
            try:
                head = f.read(32_768)
                if isinstance(head, str):
                    # io.TextIOBase may return str; encode for detector
                    head = head.encode("utf-8", errors="ignore")
                result = chardet.detect(head)
                return result.get("encoding")
            except Exception:
                return None

        # sniff encoding
        uploaded_file.seek(0)
        detected_enc = _detect_encoding(uploaded_file)
        encodings_to_try = [e for e in (detected_enc, "utf-8", "latin-1", "cp1252") if e]
        sample = None
        for enc in encodings_to_try:
            try:
                uploaded_file.seek(0)
                sample = pd.read_csv(
                    uploaded_file,
                    nrows=10_000,
                    sep=sep,
                    encoding=enc,
                    **read_kwargs,
                )
                used_encoding = enc
                break
            except UnicodeDecodeError:
                continue
        if sample is None:
            uploaded_file.seek(0)
            sample = pd.read_csv(
                uploaded_file,
                nrows=10_000,
                sep=sep,
                encoding="latin-1",
                **read_kwargs,
            )
            used_encoding = "latin-1"
        dtype_map = _build_optimized_dtype_map(sample)
        uploaded_file.seek(0)
        read_success = False
        for enc in (used_encoding, "utf-8", "latin-1"):
            try:
                uploaded_file.seek(0)
                df = pd.read_csv(
                    uploaded_file,
                    sep=sep,
                    dtype=dtype_map,
                    encoding=enc,
                    **read_kwargs,
                )
                read_success = True
                break
            except (ValueError, TypeError):
                try:
                    uploaded_file.seek(0)
                    df = pd.read_csv(
                        uploaded_file,
                        nrows=None,
                        sep=sep,
                        encoding=enc,
                        **read_kwargs,
                    )
                    read_success = True
                    break
                except UnicodeDecodeError:
                    continue
            except UnicodeDecodeError:
                continue
        if not read_success:
            uploaded_file.seek(0)
            df = pd.read_csv(uploaded_file, sep=sep, encoding="latin-1", **read_kwargs)
    elif file_type in ("xlsx", "xls"):
        df = pd.read_excel(uploaded_file)
    else:
        raise ValueError(f"Unsupported file type: {file_type}")

    return _optimize_dataframe_memory(df)


def apply_sampling_if_needed(
    df: pd.DataFrame, target_col: str | None = None
) -> tuple[pd.DataFrame, dict]:
    n_rows = len(df)
    if n_rows <= LIMITS["SAMPLE_THRESHOLD_ROWS"]:
        return df, {"sampled": False, "original_rows": n_rows}

    target_n = LIMITS["SAMPLE_TARGET_ROWS"]
    if (
        target_col
        and target_col in df.columns
        and str(df[target_col].dtype) in ("category", "object")
    ):
        sampled = (
            df.groupby(target_col, observed=True)
            .apply(
                lambda g: g.sample(
                    n=max(1, int(len(g) * target_n / n_rows)),
                    random_state=42,
                ),
                include_groups=False,
            )
            .reset_index(drop=True)
        )
        if len(sampled) > target_n:
            sampled = sampled.sample(n=target_n, random_state=42)
    else:
        sampled = df.sample(n=target_n, random_state=42)

    return sampled, {
        "sampled": True,
        "original_rows": n_rows,
        "sampled_rows": len(sampled),
        "sampling_ratio": len(sampled) / n_rows,
    }
