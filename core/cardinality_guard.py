from typing import Optional

import pandas as pd

CARDINALITY_LIMITS = {
    "bar": {"warn": 30, "hard_cap": 50, "default_top_n": 20},
    "pie": {"warn": 5, "hard_cap": 10, "default_top_n": 7},
    "box": {"warn": 20, "hard_cap": 40, "default_top_n": 15},
    "violin": {"warn": 12, "hard_cap": 20, "default_top_n": 10},
    "heatmap_crosstab": {"warn": 30, "hard_cap": 50, "default_top_n": 25},
    "scatter_color": {"warn": 12, "hard_cap": 20, "default_top_n": 10},
}


def enforce_cardinality_limit(
    series: pd.Series,
    chart_type: str,
    value_series: Optional[pd.Series] = None,
    top_n_override: Optional[int] = None,
    agg_func: str = "count",
) -> tuple[pd.Series, dict]:
    limits = CARDINALITY_LIMITS.get(
        chart_type, {"warn": 30, "hard_cap": 50, "default_top_n": 20}
    )
    n_unique = series.nunique()
    action_report = {
        "original_unique": n_unique,
        "action_taken": None,
        "final_unique": n_unique,
        "truncated": False,
    }
    if n_unique <= limits["warn"]:
        return series, action_report

    top_n = top_n_override or limits["default_top_n"] or limits["hard_cap"]
    top_n = min(top_n, limits["hard_cap"])

    if value_series is not None and agg_func != "count":
        agg_map = {
            "mean": "mean",
            "sum": "sum",
            "median": "median",
            "max": "max",
            "min": "min",
        }
        agg_fn = agg_map.get(agg_func, "mean")
        top_cats = (
            pd.DataFrame({"cat": series, "val": value_series})
            .groupby("cat")["val"]
            .agg(agg_fn)
            .nlargest(top_n)
            .index
        )
    else:
        top_cats = series.value_counts().nlargest(top_n).index

    filtered = series.copy()
    if isinstance(filtered.dtype, pd.CategoricalDtype) and "Other" not in filtered.cat.categories:
        filtered = filtered.cat.add_categories(["Other"])
    filtered = filtered.where(filtered.isin(top_cats), other="Other")
    action_report.update(
        {
            "action_taken": f"Truncated to top {top_n} by {agg_func}",
            "final_unique": top_n + 1,
            "truncated": True,
            "top_n": top_n,
        }
    )
    return filtered, action_report


def enforce_scatter_density_limit(
    df: pd.DataFrame, x_col: str, y_col: str
) -> tuple[pd.DataFrame, dict]:
    from config.limits import LIMITS

    n = len(df)
    report = {"original_n": n, "render_mode": "svg", "sampled": False}
    if n > LIMITS["SCATTER_SAMPLE_THRESHOLD"]:
        df = df.sample(n=LIMITS["SCATTER_SAMPLE_SIZE"], random_state=42)
        report["sampled"] = True
        report["sample_n"] = LIMITS["SCATTER_SAMPLE_SIZE"]
    if n > LIMITS["SCATTER_WEBGL_THRESHOLD"]:
        report["render_mode"] = "webgl"
    report["final_n"] = len(df)
    return df, report
