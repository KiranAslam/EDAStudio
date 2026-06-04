from dataclasses import dataclass, field
from typing import Optional

import numpy as np
import pandas as pd

from utils.logging_config import logger

GEO_NAME_PATTERNS = ("country", "iso", "state", "fips", "region_code", "geo", "nation")


@dataclass
class ColumnProfile:
    name: str
    analytical_type: str
    dtype_raw: str
    n_total: int
    n_null: int
    null_pct: float
    n_unique: int
    unique_ratio: float
    mean: Optional[float] = None
    median: Optional[float] = None
    std: Optional[float] = None
    min_val: Optional[float] = None
    max_val: Optional[float] = None
    skewness: Optional[float] = None
    has_inf: bool = False
    is_all_null: bool = False
    is_constant: bool = False
    is_geo_candidate: bool = False
    profile_errors: list[str] = field(default_factory=list)
    eligible_for_histogram: bool = False
    eligible_for_boxplot: bool = False
    eligible_for_correlation: bool = False
    eligible_for_bar: bool = False


class DataProfiler:
    def profile_dataframe(self, df: pd.DataFrame) -> dict[str, ColumnProfile]:
        profiles = {}
        for col in df.columns:
            try:
                profiles[col] = self._profile_column(df[col], col)
            except Exception as e:
                logger.warning("Profiler failed on '%s': %s", col, e)
                profiles[col] = self._create_fallback_profile(col, df[col], str(e))
        return profiles

    def _safe_stat(self, series: pd.Series, stat: str) -> Optional[float]:
        try:
            val = getattr(series, stat)()
            return float(val) if np.isfinite(val) else None
        except Exception:
            return None

    def _is_geo_candidate(self, name: str, series: pd.Series) -> bool:
        lower = name.lower()
        if not any(p in lower for p in GEO_NAME_PATTERNS):
            return False
        sample = series.dropna().astype(str).head(100)
        if len(sample) == 0:
            return False
        iso_like = sample.str.match(r"^[A-Z]{2,3}$").mean()
        return iso_like > 0.3

    def _classify_type(
        self, series: pd.Series, n_unique: int, override: str | None = None
    ) -> str:
        if override:
            return override

        if pd.api.types.is_datetime64_any_dtype(series):
            return "TEMPORAL"

        if series.dtype == object and n_unique > 0:
            try:
                sample = series.dropna().head(50)
                parsed = pd.to_datetime(sample, errors="coerce")
                if parsed.notna().sum() / max(len(sample), 1) > 0.8:
                    return "TEMPORAL"
            except Exception:
                pass

        if pd.api.types.is_bool_dtype(series) or pd.api.types.is_categorical_dtype(
            series
        ):
            return "CATEGORICAL"

        if pd.api.types.is_object_dtype(series):
            return "CATEGORICAL"

        if pd.api.types.is_numeric_dtype(series):
            if n_unique <= 0:
                return "UNUSABLE"
            if n_unique <= 20:
                return "CATEGORICAL"
            if n_unique <= 50:
                return "AMBIGUOUS"
            return "CONTINUOUS"

        return "UNUSABLE"

    def _get_overrides(self) -> dict:
        try:
            import streamlit as st

            return st.session_state.get("column_overrides", {})
        except Exception:
            return {}

    def _get_ordered_columns(self) -> set:
        try:
            import streamlit as st

            return st.session_state.get("ordered_columns", set())
        except Exception:
            return set()

    def _profile_column(self, series: pd.Series, name: str) -> ColumnProfile:
        override = self._get_overrides().get(name)
        n_total = len(series)
        n_null = int(series.isna().sum())
        n_non_null = n_total - n_null

        if n_non_null == 0:
            return ColumnProfile(
                name=name,
                analytical_type="UNUSABLE",
                dtype_raw=str(series.dtype),
                n_total=n_total,
                n_null=n_null,
                null_pct=100.0,
                n_unique=0,
                unique_ratio=0.0,
                is_all_null=True,
                profile_errors=["Column is 100% null."],
            )

        working = series.dropna()
        try:
            n_unique = int(working.nunique())
        except TypeError:
            n_unique = -1

        unique_ratio = n_unique / n_non_null if n_non_null > 0 else 0.0
        analytical_type = self._classify_type(series, n_unique, override)

        if name in self._get_ordered_columns():
            if analytical_type == "CONTINUOUS":
                analytical_type = "CONTINUOUS_ORDERED"

        is_geo = self._is_geo_candidate(name, series)
        if is_geo:
            analytical_type = "GEO"

        profile = ColumnProfile(
            name=name,
            analytical_type=analytical_type,
            dtype_raw=str(series.dtype),
            n_total=n_total,
            n_null=n_null,
            null_pct=round(n_null / n_total * 100, 2),
            n_unique=n_unique,
            unique_ratio=round(unique_ratio, 4),
            is_constant=(n_unique == 1),
            is_geo_candidate=is_geo,
        )

        if profile.analytical_type == "CONTINUOUS":
            numeric_clean = pd.to_numeric(working, errors="coerce")
            profile.has_inf = bool(
                np.isposinf(numeric_clean).any() or np.isneginf(numeric_clean).any()
            )
            numeric_finite = numeric_clean.replace(
                [np.inf, -np.inf], np.nan
            ).dropna()
            if len(numeric_finite) > 0:
                profile.mean = self._safe_stat(numeric_finite, "mean")
                profile.median = self._safe_stat(numeric_finite, "median")
                profile.std = self._safe_stat(numeric_finite, "std")
                profile.min_val = self._safe_stat(numeric_finite, "min")
                profile.max_val = self._safe_stat(numeric_finite, "max")
                try:
                    skew = float(numeric_finite.skew())
                    profile.skewness = skew if np.isfinite(skew) else None
                except Exception:
                    pass

        profile.eligible_for_histogram = (
            profile.analytical_type == "CONTINUOUS"
            and not profile.is_all_null
            and not profile.is_constant
        )
        profile.eligible_for_correlation = (
            profile.analytical_type == "CONTINUOUS"
            and not profile.is_all_null
            and not profile.is_constant
            and n_non_null >= 10
        )
        profile.eligible_for_bar = (
            profile.analytical_type == "CATEGORICAL"
            and not profile.is_all_null
            and 1 < n_unique <= 200
        )
        profile.eligible_for_boxplot = (
            profile.analytical_type == "CONTINUOUS"
            and not profile.is_all_null
            and n_non_null >= 5
        )
        return profile

    def _create_fallback_profile(
        self, name: str, series: pd.Series, error: str
    ) -> ColumnProfile:
        return ColumnProfile(
            name=name,
            analytical_type="UNUSABLE",
            dtype_raw=str(series.dtype) if hasattr(series, "dtype") else "unknown",
            n_total=len(series) if hasattr(series, "__len__") else 0,
            n_null=0,
            null_pct=0.0,
            n_unique=0,
            unique_ratio=0.0,
            profile_errors=[f"Profiler failed: {error[:200]}"],
        )
