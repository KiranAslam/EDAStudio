"""
EDA Studio — Production data visualization and automated EDA.
Run: streamlit run app.py
"""

import streamlit as st

from core.session_state import initialize_session_state
from ui.chart_builder import render_chart_builder
from ui.column_dictionary import render_column_dictionary
from ui.eda_panel import render_eda
from ui.overview_panel import render_overview
from ui.styles import render_header
from ui.upload_panel import render_upload_sidebar
from utils.error_handling import exception_boundary

st.set_page_config(
    page_title="EDA Studio",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)


def main():
    initialize_session_state()
    render_header()
    render_upload_sidebar()

    tab_overview, tab_eda, tab_charts, tab_columns = st.tabs(
        [
            "Dashboard",
            "Automated EDA",
            "Chart Builder",
            "Column Dictionary",
        ]
    )

    with tab_overview:
        render_overview()

    with tab_eda:
        render_eda()

    with tab_charts:
        render_chart_builder()

    with tab_columns:
        render_column_dictionary()

    st.sidebar.divider()
    st.sidebar.markdown("### Export working data")
    df = st.session_state.get("working_df")
    if df is not None:
        st.sidebar.download_button(
            "Download CSV (working set)",
            df.to_csv(index=False).encode("utf-8"),
            st.session_state.get("uploaded_file_name", "data") + "_working.csv",
            "text/csv",
        )

    st.sidebar.markdown("---")
    st.sidebar.caption(
        "EDA Studio v1.0 · Dtype-aware charts · No tracebacks in production UI"
    )


if __name__ == "__main__":
    with exception_boundary("Application startup", reraise=False):
        main()
