import pandas as pd
import streamlit as st

from ui.styles import metric_row_html
from utils.error_handling import safe_component


@safe_component("Overview failed to load.")
def render_overview():
    df = st.session_state.get("working_df")
    profiles = st.session_state.get("column_profiles", {})
    if df is None:
        st.info("Upload a dataset to see the data overview.")
        return

    sampling = st.session_state.get("sampling_metadata", {})
    metrics = [
        ("Rows", f"{len(df):,}"),
        ("Columns", str(len(df.columns))),
        (
            "Memory",
            f"{df.memory_usage(deep=True).sum() / 1024**2:.1f} MB",
        ),
        (
            "Continuous",
            str(sum(1 for p in profiles.values() if p.analytical_type == "CONTINUOUS")),
        ),
        (
            "Categorical",
            str(sum(1 for p in profiles.values() if p.analytical_type == "CATEGORICAL")),
        ),
        (
            "Temporal",
            str(sum(1 for p in profiles.values() if p.analytical_type == "TEMPORAL")),
        ),
    ]
    st.markdown(metric_row_html(metrics), unsafe_allow_html=True)

    if sampling.get("sampled"):
        st.markdown(
            f'<div class="status-banner status-info">Showing a sample of '
            f'{sampling["sampled_rows"]:,} rows ({sampling["sampling_ratio"]*100:.1f}%) '
            f"from {sampling['original_rows']:,} total.</div>",
            unsafe_allow_html=True,
        )

    col1, col2 = st.columns([2, 1])
    with col1:
        st.subheader("Preview")
        st.dataframe(df.head(100), use_container_width=True, height=320)
    with col2:
        st.subheader("Null summary")
        null_pct = (df.isna().sum() / len(df) * 100).round(1)
        null_df = pd.DataFrame({"Column": null_pct.index, "Null %": null_pct.values})
        null_df = null_df[null_df["Null %"] > 0].sort_values("Null %", ascending=False)
        if len(null_df) == 0:
            st.success("No null values detected.")
        else:
            st.dataframe(null_df.head(15), use_container_width=True, hide_index=True)

    st.subheader("Quick dtype summary")
    rows = []
    for col, p in profiles.items():
        rows.append(
            {
                "Column": col,
                "Type": p.analytical_type,
                "Raw dtype": p.dtype_raw,
                "Unique": p.n_unique,
                "Null %": p.null_pct,
            }
        )
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
