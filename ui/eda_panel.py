import json

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

from config.limits import LIMITS
from core.cached_operations import compute_correlation_matrix, compute_distribution
from core.session_state import get_df_hash
from utils.error_handling import safe_component


@safe_component("Automated EDA failed.")
def render_eda():
    df = st.session_state.get("working_df")
    profiles = st.session_state.get("column_profiles", {})
    if df is None:
        st.info("Upload a dataset to run automated EDA.")
        return

    st.markdown("### Automated exploratory analysis")
    st.caption(
        "Deterministic insights driven by column profiles — adjust scope and thresholds below."
    )

    continuous = [c for c, p in profiles.items() if p.eligible_for_histogram]
    categorical = [c for c, p in profiles.items() if p.eligible_for_bar]
    num_cols = [c for c, p in profiles.items() if p.eligible_for_correlation]

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        sample_size = st.slider(
            "EDA sample size",
            1000,
            min(500_000, len(df)),
            min(LIMITS["SAMPLE_TARGET_ROWS"], len(df)),
            step=1000,
        )
    with c2:
        corr_threshold = st.slider(
            "Mask |correlation| below",
            0.0,
            0.5,
            st.session_state.get("eda_corr_threshold", 0.0),
            0.05,
        )
    with c3:
        outlier_fence = st.selectbox(
            "Outlier fence",
            [1.5, 3.0],
            format_func=lambda x: f"{x}× IQR" + (" (standard)" if x == 1.5 else " (conservative)"),
        )
    with c4:
        corr_method = st.selectbox("Correlation method", ["pearson", "spearman", "kendall"])

    eda_df = df.sample(min(sample_size, len(df)), random_state=42) if len(df) > sample_size else df

    tab_dist, tab_cat, tab_corr, tab_out = st.tabs(
        ["Distributions", "Categories", "Correlations", "Outliers"]
    )

    with tab_dist:
        if not continuous:
            st.warning("No continuous columns available for distribution analysis.")
        else:
            selected = st.multiselect(
                "Numerical columns",
                continuous,
                default=continuous[: min(4, len(continuous))],
            )
            for col in selected:
                dist, err = compute_distribution(get_df_hash(), col)
                if err:
                    st.warning(f"{col}: {err}")
                    continue
                fig = px.histogram(
                    x=dist["data"],
                    nbins=dist["n_bins"],
                    title=f"{col} — mean={dist['mean']:.2g}, median={dist['median']:.2g}",
                )
                st.plotly_chart(fig, use_container_width=True)

    with tab_cat:
        if not categorical:
            st.warning("No suitable categorical columns.")
        else:
            cat_col = st.selectbox("Category column", categorical)
            if cat_col:
                counts = eda_df[cat_col].value_counts().head(25)
                fig = px.bar(
                    x=counts.index.astype(str),
                    y=counts.values,
                    labels={"x": cat_col, "y": "Count"},
                    title=f"Top categories — {cat_col}",
                )
                fig.update_layout(xaxis_tickangle=-45)
                st.plotly_chart(fig, use_container_width=True)

    with tab_corr:
        if len(num_cols) < 2:
            st.warning("Correlation matrix requires at least 2 numerical columns.")
        else:
            selected_num = st.multiselect(
                "Include columns",
                num_cols,
                default=num_cols[: min(12, len(num_cols))],
            )
            if len(selected_num) >= 2:
                corr, err = compute_correlation_matrix(
                    get_df_hash(), tuple(selected_num), corr_method
                )
                if err:
                    st.error(err)
                else:
                    masked = corr.mask(np.abs(corr) < corr_threshold)
                    fig = px.imshow(
                        masked,
                        color_continuous_scale="RdBu_r",
                        zmin=-1,
                        zmax=1,
                        text_auto=".2f",
                        title="Correlation heatmap",
                    )
                    st.plotly_chart(fig, use_container_width=True)

    with tab_out:
        if not continuous:
            st.warning("No continuous columns for outlier detection.")
        else:
            out_col = st.selectbox("Metric", continuous, key="outlier_col")
            series = eda_df[out_col].replace([np.inf, -np.inf], np.nan).dropna()
            q1, q3 = series.quantile(0.25), series.quantile(0.75)
            iqr = q3 - q1
            lower = q1 - outlier_fence * iqr
            upper = q3 + outlier_fence * iqr
            outliers = series[(series < lower) | (series > upper)]
            st.metric("Outlier count", len(outliers))
            st.metric("Outlier %", f"{100 * len(outliers) / len(series):.2f}%")
            fig = px.box(eda_df, y=out_col, title=f"Box plot — {out_col}")
            st.plotly_chart(fig, use_container_width=True)

    st.divider()
    st.subheader("Pair plot (scatter matrix)")
    if len(num_cols) >= 3:
        pair_cols = st.multiselect(
            "Pair plot columns (max 8)",
            num_cols,
            default=num_cols[: min(5, len(num_cols))],
            max_selections=LIMITS["PAIR_PLOT_MAX_COLUMNS"],
        )
        hue = st.selectbox(
            "Color by (optional)",
            ["None"] + categorical,
        )
        if pair_cols and len(pair_cols) >= 2:
            sample = eda_df.sample(min(2000, len(eda_df)), random_state=42)
            fig = px.scatter_matrix(
                sample,
                dimensions=pair_cols,
                color=None if hue == "None" else hue,
            )
            st.plotly_chart(fig, use_container_width=True)

    if st.button("Export EDA settings (JSON)"):
        cfg = {
            "sample_size": sample_size,
            "corr_threshold": corr_threshold,
            "outlier_fence": outlier_fence,
            "corr_method": corr_method,
        }
        st.download_button(
            "Download EDA config",
            json.dumps(cfg, indent=2),
            "eda_config.json",
            "application/json",
        )
