from dataclasses import dataclass, field
from typing import Optional
import pandas as pd
from config.limits import LIMITS


@dataclass
class ValidationResult:
    is_valid: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    inferred_metadata: dict = field(default_factory=dict)


def _detect_encoding(raw_bytes: bytes) -> Optional[str]:
    try:
        import chardet

        result = chardet.detect(raw_bytes)
        return result.get("encoding")
    except ImportError:
        return "utf-8"


def _detect_mixed_type_columns(df: pd.DataFrame) -> list[str]:
    mixed = []
    for col in df.select_dtypes(include="object").columns:
        non_null = df[col].dropna()
        if len(non_null) < 2:
            continue
        numeric_count = pd.to_numeric(non_null, errors="coerce").notna().sum()
        ratio = numeric_count / len(non_null)
        if 0.1 < ratio < 0.9:
            mixed.append(col)
    return mixed


def validate_uploaded_file(uploaded_file) -> ValidationResult:
    result = ValidationResult(is_valid=True)
    if uploaded_file.size == 0:
        result.is_valid = False
        result.errors.append("The uploaded file is empty (0 bytes).")
        return result

    ext = uploaded_file.name.split(".")[-1].lower()
    if ext not in ("csv", "xlsx", "xls", "tsv", "parquet"):
        result.is_valid = False
        result.errors.append(
            f"Unsupported file type '.{ext}'. Supported: CSV, Excel, TSV, Parquet."
        )
        return result

    if ext in ("csv", "tsv"):
        raw_bytes = uploaded_file.read(4096)
        uploaded_file.seek(0)
        encoding = _detect_encoding(raw_bytes)
        result.inferred_metadata["encoding"] = encoding or "utf-8"
        if encoding is None:
            result.warnings.append(
                "Could not detect encoding. Defaulting to UTF-8."
            )

    try:
        uploaded_file.seek(0)
        if ext == "parquet":
            header_df = pd.read_parquet(uploaded_file).head(5)
            uploaded_file.seek(0)
        elif ext in ("csv", "tsv"):
            sep = "\t" if ext == "tsv" else ","
            header_df = pd.read_csv(
                uploaded_file,
                nrows=5,
                sep=sep,
                encoding=result.inferred_metadata.get("encoding", "utf-8"),
                on_bad_lines="warn",
            )
        else:
            header_df = pd.read_excel(uploaded_file, nrows=5)
        uploaded_file.seek(0)
    except pd.errors.EmptyDataError:
        result.is_valid = False
        result.errors.append("The file contains no readable data.")
        return result
    except Exception as e:
        result.is_valid = False
        result.errors.append(
            f"Failed to read file header: {type(e).__name__}. "
            "The file may be corrupted."
        )
        return result

    if len(header_df.columns) == 0:
        result.is_valid = False
        result.errors.append("No columns detected.")
        return result

    if len(header_df.columns) > LIMITS["MAX_COLUMNS"]:
        result.is_valid = False
        result.errors.append(
            f"File has {len(header_df.columns)} columns, exceeding "
            f"{LIMITS['MAX_COLUMNS']} limit."
        )
        return result

    unnamed = sum(1 for c in header_df.columns if str(c).startswith("Unnamed:"))
    if unnamed > len(header_df.columns) * 0.5:
        result.warnings.append(
            f"{unnamed} columns appear unnamed. Check header row."
        )

    dupes = [c for c in header_df.columns if list(header_df.columns).count(c) > 1]
    if dupes:
        result.warnings.append(
            f"Duplicate column names: {list(set(dupes))}. Will auto-rename."
        )

    mixed = _detect_mixed_type_columns(header_df)
    if mixed:
        result.warnings.append(
            f"Potentially mixed-type columns: {mixed}."
        )

    result.inferred_metadata["n_cols"] = len(header_df.columns)
    result.inferred_metadata["columns"] = list(header_df.columns)
    return result
