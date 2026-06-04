import numpy as np
import pandas as pd
import streamlit as st


@st.cache_data(ttl=1800, max_entries=10, show_spinner=False)
def compute_correlation_matrix(
    df_hash: str,
    column_names: tuple[str, ...],
    method: str = "pearson",
) -> tuple[pd.DataFrame | None, str | None]:
    df = st.session_state.get("working_df")
    if df is None:
        return None, "No dataset loaded."
    try:
        numeric_df = df[list(column_names)].select_dtypes(include="number")
        if len(numeric_df.columns) < 2:
            return None, "Correlation requires at least 2 numerical columns."
        clean = numeric_df.replace([np.inf, -np.inf], np.nan)
        clean = clean.dropna(axis=1, thresh=int(len(clean) * 0.5))
        if len(clean.columns) < 2:
            return None, "Too many nulls — need 2+ columns with >50% data."
        corr = clean.corr(method=method, min_periods=5)
        diag = np.diag(corr.values)
        if not np.allclose(diag[~np.isnan(diag)], 1.0, atol=1e-4):
            return None, "Unexpected correlation result — check constant columns."
        return corr, None
    except Exception as e:
        return None, f"Correlation failed: {type(e).__name__}: {str(e)[:200]}"


@st.cache_data(ttl=3600, max_entries=20, show_spinner=False)
def compute_distribution(
    df_hash: str, column_name: str
) -> tuple[dict | None, str | None]:
    df = st.session_state.get("working_df")
    if df is None:
        return None, "No dataset loaded."
    try:
        col = df[column_name]
        clean = col.replace([np.inf, -np.inf], np.nan).dropna()
        if len(clean) == 0:
            return None, f"Column '{column_name}' has no valid values."
        q75, q25 = np.percentile(clean, [75, 25])
        iqr = q75 - q25
        if iqr > 0:
            bin_width = 2 * iqr / (len(clean) ** (1 / 3))
            n_bins = max(5, min(100, int((clean.max() - clean.min()) / bin_width)))
        else:
            n_bins = min(50, int(clean.nunique()))
        return {
            "data": clean.tolist(),
            "n_bins": n_bins,
            "mean": float(clean.mean()),
            "median": float(clean.median()),
            "std": float(clean.std()) if len(clean) > 1 else 0.0,
            "skew": float(clean.skew()) if len(clean) > 2 else 0.0,
            "n_valid": len(clean),
        }, None
    except Exception as e:
        return None, str(e)[:200]
