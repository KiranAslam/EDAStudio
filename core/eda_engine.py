from typing import Optional
import pandas as pd

from core.profiler import DataProfiler
from core.plot_sanitizer import sanitize_for_chart


def orchestrate_eda(df: pd.DataFrame, sample: Optional[int] = 100) -> dict:

    profiler = DataProfiler()
    sample_df = df.head(sample) if sample is not None else df
    profiles = profiler.profile_dataframe(sample_df)
    sanitized_sample, sanitization_report = sanitize_for_chart(sample_df, None, None, chart_type="scatter")

    return {
        "profiles": profiles,
        "sanitized_sample": sanitized_sample,
        "sanitization_report": sanitization_report,
    }
