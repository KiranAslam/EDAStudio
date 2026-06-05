from dataclasses import dataclass, field

import numpy as np
import pandas as pd

@dataclass
class SanitizationReport:
    original_rows: int
    final_rows: int
    rows_dropped: int
    inf_values_replaced: int
    nan_values_in_key_cols: int
    warnings: list[str] = field(default_factory=list)
MIN_ROWS = {
    "scatter": 2,
    "line": 2,
    "histogram": 5,
    "box": 5,
    "violin": 10,
    "bar": 1,
    "pie": 1,
    "timeseries": 2,
}

def sanitize_for_plot(
    df: pd.DataFrame,
    x_col: str | None,
    y_col: str | None,
    color_col: str | None = None,
    size_col: str | None = None,
    chart_type: str = "scatter",
    trendline: bool = False,
) -> tuple[pd.DataFrame, SanitizationReport]:
    report = SanitizationReport(
        original_rows=len(df),
        final_rows=len(df),
        rows_dropped=0,
        inf_values_replaced=0,
        nan_values_in_key_cols=0,
    )
    key_cols = [c for c in [x_col, y_col, color_col, size_col] if c and c in df.columns]
    if not key_cols:
        return df.copy(), report
    working = df[key_cols].copy()
    report.nan_values_in_key_cols = int(working.isna().sum().sum())
    if report.nan_values_in_key_cols > 0:
        pct = report.nan_values_in_key_cols / (len(working) * len(key_cols)) * 100
        report.warnings.append(
            f"{report.nan_values_in_key_cols} null values ({pct:.1f}%) in selected columns."
        )

    for col in key_cols:
        if pd.api.types.is_numeric_dtype(df[col]):
            numeric = pd.to_numeric(df[col], errors="coerce")
            n_inf = int(np.isinf(numeric).sum())
            if n_inf > 0:
                report.inf_values_replaced += n_inf
                report.warnings.append(
                    f"Column '{col}': {n_inf} infinite values replaced with NaN."
                )
            working[col] = numeric.replace([np.inf, -np.inf], np.nan)

    mask = pd.Series(True, index=working.index)
    if chart_type in ("scatter",) and trendline and x_col and y_col:
        mask = mask & working[x_col].notna() & working[y_col].notna()
    elif chart_type in ("scatter",) and x_col and y_col:
        mask = mask & working[x_col].notna() & working[y_col].notna()
    elif chart_type in ("line", "timeseries"):
        if x_col:
            mask = mask & working[x_col].notna()
        if y_col:
            mask = mask & working[y_col].notna()
    elif chart_type == "histogram" and x_col:
        mask = mask & working[x_col].notna()
    elif chart_type in ("box", "violin") and y_col:
        mask = mask & working[y_col].notna()
    elif chart_type in ("bar", "pie") and x_col:
        mask = mask & working[x_col].notna()

    result_df = df.loc[working[mask].index].copy()
    report.final_rows = len(result_df)
    report.rows_dropped = report.original_rows - report.final_rows
    if report.rows_dropped > 0:
        pct = report.rows_dropped / report.original_rows * 100
        report.warnings.append(
            f"{report.rows_dropped} rows ({pct:.1f}%) excluded due to null/inf values."
        )

    min_required = MIN_ROWS.get(chart_type, 1)
    if report.final_rows < min_required:
        raise ValueError(
            f"Only {report.final_rows} valid rows remain. "
            f"{chart_type} requires at least {min_required}."
        )
    return result_df, report
