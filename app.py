import streamlit as st

from core.session_state import initialize_session_state
from ui.chart_builder import render_chart_builder
from ui.eda_panel import render_eda
from ui.overview_panel import render_overview
from ui.styles import render_header, render_workflow_hint
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
    has_data = render_upload_sidebar()
    render_workflow_hint(has_data)

    tab_overview, tab_eda, tab_charts = st.tabs(
        [
            "Dashboard",
            "Automated EDA",
            "Chart Builder",
        ]
    )

    with tab_overview:
        render_overview()

    with tab_eda:
        render_eda()

    with tab_charts:
        render_chart_builder()

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
        "EDA Studio v1.1 · Dtype-aware charts · No tracebacks in production UI"
    )


if __name__ == "__main__":
    with exception_boundary("Application startup", reraise=False):
        main()
