from dataclasses import dataclass, field

import pandas as pd


@dataclass
class CoercionReport:
    column: str
    original_dtype: str
    coerced_dtype: str
    analytical_type: str
    parse_rate: float = 1.0
    converted: bool = False
    warnings: list[str] = field(default_factory=list)


def build_column_metadata(df: pd.DataFrame, profiles: dict) -> dict[str, dict]:
    metadata: dict[str, dict] = {}
    for col, profile in profiles.items():
        metadata[col] = {
            "analytical_type": profile.analytical_type,
            "dtype_raw": profile.dtype_raw,
            "coerced_dtype": profile.dtype_raw,
            "coercion_applied": False,
            "n_unique": profile.n_unique,
            "null_pct": profile.null_pct,
        }
    return metadata


def _looks_like_dates(series: pd.Series) -> bool:
    if pd.api.types.is_datetime64_any_dtype(series):
        return True
    if series.dtype != object:
        return False
    sample = series.dropna().head(50)
    if len(sample) == 0:
        return False
    parsed = pd.to_datetime(sample, errors="coerce")
    return parsed.notna().sum() / len(sample) > 0.8


def _coerce_datetime(series: pd.Series) -> tuple[pd.Series, float, str | None]:
    if pd.api.types.is_datetime64_any_dtype(series):
        return series, 1.0, None
    coerced = pd.to_datetime(series, errors="coerce", utc=False)
    n_valid = coerced.notna().sum()
    n_total = max(len(series.dropna()), 1)
    rate = n_valid / n_total
    warn = None
    if rate < 0.8:
        warn = "Low date parse rate - axis ordering may be incorrect."
    return coerced, float(rate), warn


def _coerce_numeric_if_confident(series: pd.Series) -> tuple[pd.Series | None, float]:
    numeric = pd.to_numeric(series, errors="coerce")
    non_null = series.dropna()
    denominator = max(len(non_null), 1)
    rate = numeric.notna().sum() / denominator
    if rate > 0.9:
        return numeric, float(rate)
    return None, float(rate)


def prepare_column(
    df: pd.DataFrame,
    col: str,
    chart_type: str | None = None,
) -> tuple[pd.Series, CoercionReport]:
    import streamlit as st

    if col not in df.columns:
        raise KeyError(f"Column '{col}' not found in dataframe.")

    series = df[col].copy()
    profiles = st.session_state.get("column_profiles", {})
    profile = profiles.get(col)
    override = st.session_state.get("column_overrides", {}).get(col)
    analytical = override or (profile.analytical_type if profile else "CATEGORICAL")

    report = CoercionReport(
        column=col,
        original_dtype=str(series.dtype),
        coerced_dtype=str(series.dtype),
        analytical_type=analytical,
    )

    if col in st.session_state.get("ordered_columns", set()) and analytical == "CONTINUOUS":
        analytical = "CONTINUOUS_ORDERED"
        report.analytical_type = analytical

    if analytical == "TEMPORAL" or (profile and profile.analytical_type == "TEMPORAL") or _looks_like_dates(series):
        coerced, rate, warn = _coerce_datetime(series)
        report.coerced_dtype = str(coerced.dtype)
        report.parse_rate = rate
        report.converted = rate >= 0.8
        report.analytical_type = "TEMPORAL"
        if warn:
            report.warnings.append(warn)
        if rate < 0.8:
            report.warnings.append(
                f"Only {rate * 100:.0f}% of values parsed as dates. Check column format."
            )
        return coerced, report

    if analytical == "CONTINUOUS" and series.dtype == object:
        numeric, rate = _coerce_numeric_if_confident(series)
        if numeric is not None:
            report.coerced_dtype = str(numeric.dtype)
            report.parse_rate = rate
            report.converted = True
            report.warnings.append(
                f"Converted text column to numeric ({rate * 100:.0f}% parsed)."
            )
            return numeric, report

    if analytical == "CATEGORICAL" and series.dtype == object:
        converted = series.astype("category")
        report.coerced_dtype = str(converted.dtype)
        report.converted = True
        report.warnings.append("Converted text column to category for efficient plotting.")
        return converted, report

    return series, report


def apply_coercions_to_dataframe(
    df: pd.DataFrame, columns: list[str]
) -> tuple[pd.DataFrame, list[CoercionReport]]:
    result = df.copy()
    reports: list[CoercionReport] = []
    for col in columns:
        if col and col in result.columns:
            coerced, report = prepare_column(result, col)
            result[col] = coerced
            reports.append(report)
    return result, reports


def detect_ohlc_columns(df: pd.DataFrame) -> dict | None:
    cols_lower = {c.lower(): c for c in df.columns}
    mapping: dict[str, str] = {}
    for key, patterns in [
        ("open", ("open", "o")),
        ("high", ("high", "h")),
        ("low", ("low", "l")),
        ("close", ("close", "c", "adj close", "adj_close")),
    ]:
        for c_lower, c_orig in cols_lower.items():
            if any(
                c_lower == p
                or c_lower.startswith(f"{p}_")
                or c_lower.endswith(f"_{p}")
                for p in patterns
            ):
                mapping[key] = c_orig
                break

    date_col = None
    for c in df.columns:
        cl = c.lower()
        if any(token in cl for token in ("date", "time", "timestamp", "datetime", "period")):
            date_col = c
            break

    if len(mapping) == 4 and date_col:
        return {"date": date_col, **mapping}
    return None


def get_eligible_columns(
    profiles: dict, allowed_types: list[str], include_none: bool = False
) -> list[str]:
    if not allowed_types:
        return []
    result = []
    for col, profile in profiles.items():
        analytical_type = profile.analytical_type
        if analytical_type in allowed_types or (include_none and "NONE" in allowed_types):
            result.append(col)
    return sorted(result)
