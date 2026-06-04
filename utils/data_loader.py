import numpy as np
import pandas as pd

from config.limits import LIMITS


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
            if unique_ratio < LIMITS["CATEGORY_CONVERSION_THRESHOLD"]:
                dtype_map[col] = "category"
        elif col_sample.dtype == np.int64:
            col_min, col_max = col_sample.min(), col_sample.max()
            if col_min >= 0 and col_max <= 255:
                dtype_map[col] = np.uint8
            elif col_min >= -128 and col_max <= 127:
                dtype_map[col] = np.int8
            elif col_min >= -32768 and col_max <= 32767:
                dtype_map[col] = np.int16
            elif col_min >= -2_147_483_648 and col_max <= 2_147_483_647:
                dtype_map[col] = np.int32
        elif col_sample.dtype == np.float64:
            if col_sample.abs().max() < 3.4e38:
                dtype_map[col] = np.float32
    return dtype_map


def _optimize_dataframe_memory(df: pd.DataFrame) -> pd.DataFrame:
    for col in df.select_dtypes(include="object").columns:
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
    encoding = getattr(uploaded_file, "_encoding", None)

    if file_type == "parquet":
        df = pd.read_parquet(uploaded_file)
    elif file_type in ("csv", "tsv"):
        sep = "\t" if file_type == "tsv" else ","
        sample = pd.read_csv(uploaded_file, nrows=10_000, sep=sep, **read_kwargs)
        dtype_map = _build_optimized_dtype_map(sample)
        uploaded_file.seek(0)
        df = pd.read_csv(
            uploaded_file, sep=sep, dtype=dtype_map, **read_kwargs
        )
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
