import pandas as pd
import streamlit as st

from core.profiler import DataProfiler
from utils.error_handling import safe_component


@safe_component("Column dictionary failed.")
def render_column_dictionary():
    df = st.session_state.get("working_df")
    profiles = st.session_state.get("column_profiles", {})
    if df is None:
        st.info("Upload a dataset to manage columns.")
        return

    st.markdown("### Column dictionary")
    st.caption("Override analytical types, rename columns, and mark ordered axes.")

    st.subheader("Rename columns")
    rename_col = st.selectbox("Select column to rename", df.columns.tolist())
    new_name = st.text_input("Display name", st.session_state.get("column_renames", {}).get(rename_col, rename_col))
    if st.button("Apply rename"):
        renames = st.session_state.setdefault("column_renames", {})
        renames[rename_col] = new_name
        st.success(f"Renamed '{rename_col}' → '{new_name}' (display only).")

    st.subheader("Type overrides")
    ambiguous = [c for c, p in profiles.items() if p.analytical_type == "AMBIGUOUS"]
    if ambiguous:
        for col in ambiguous:
            choice = st.radio(
                f"`{col}` — treat as",
                ["CATEGORICAL", "CONTINUOUS"],
                horizontal=True,
                key=f"override_{col}",
            )
            if st.button(f"Apply override for {col}", key=f"btn_{col}"):
                st.session_state.setdefault("column_overrides", {})[col] = choice
                profiler = DataProfiler()
                st.session_state["column_profiles"] = profiler.profile_dataframe(df)
                st.rerun()
    else:
        st.info("No ambiguous integer columns detected.")

    st.subheader("Ordered axis flag")
    cont_cols = [c for c, p in profiles.items() if p.analytical_type in ("CONTINUOUS", "AMBIGUOUS")]
    ordered_col = st.selectbox("Mark as ordered (for line charts)", ["—"] + cont_cols)
    if ordered_col != "—" and st.button("Mark ordered"):
        st.session_state.setdefault("ordered_columns", set()).add(ordered_col)
        profiler = DataProfiler()
        st.session_state["column_profiles"] = profiler.profile_dataframe(df)
        st.success(f"'{ordered_col}' marked as ordered.")
        st.rerun()

    st.subheader("Full profiles")
    rows = []
    for col, p in profiles.items():
        rows.append(
            {
                "Column": col,
                "Analytical type": p.analytical_type,
                "Dtype": p.dtype_raw,
                "Null %": p.null_pct,
                "Unique": p.n_unique,
                "Mean": p.mean,
                "Median": p.median,
                "Skew": p.skewness,
                "Histogram": p.eligible_for_histogram,
                "Correlation": p.eligible_for_correlation,
                "Errors": "; ".join(p.profile_errors) if p.profile_errors else "",
            }
        )
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    if st.button("Re-profile all columns"):
        profiler = DataProfiler()
        st.session_state["column_profiles"] = profiler.profile_dataframe(df)
        st.success("Profiles refreshed.")
        st.rerun()
