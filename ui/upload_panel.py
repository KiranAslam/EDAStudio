import pandas as pd
import streamlit as st

from config.limits import LIMITS
from core.dtype_engine import build_column_metadata, detect_ohlc_columns
from core.profiler import DataProfiler
from core.session_state import detect_new_upload, reset_data_state
from utils.data_loader import apply_sampling_if_needed, load_with_memory_optimization
from utils.error_handling import exception_boundary
from utils.memory import check_upload_feasibility
from utils.validators import validate_uploaded_file


def render_upload_sidebar() -> bool:
    """Returns True if a dataset is loaded and ready."""
    st.sidebar.markdown("### Data source")
    uploaded = st.sidebar.file_uploader(
        "Upload dataset",
        type=["csv", "xlsx", "xls", "tsv", "parquet"],
        help=f"Max {LIMITS['MAX_FILE_SIZE_MB']} MB. Large files are auto-sampled.",
    )

    if uploaded is None:
        st.sidebar.info("Upload CSV, Excel, TSV, or Parquet to begin.")
        return st.session_state.get("working_df") is not None

    upload_count = st.session_state.get("upload_count", 0)
    if upload_count >= LIMITS["MAX_UPLOADS_PER_SESSION"]:
        st.sidebar.error("Upload limit reached for this session. Refresh the page.")
        return st.session_state.get("working_df") is not None

    if not detect_new_upload(uploaded):
        return st.session_state.get("working_df") is not None

    reset_data_state()
    st.session_state["uploaded_file_name"] = uploaded.name
    st.session_state["upload_timestamp"] = pd.Timestamp.now()
    st.session_state["upload_count"] = upload_count + 1

    validation = validate_uploaded_file(uploaded)
    st.session_state["validation_result"] = validation
    if not validation.is_valid:
        for err in validation.errors:
            st.sidebar.error(err)
        return False
    for w in validation.warnings:
        st.sidebar.warning(w)

    ok, reason = check_upload_feasibility(uploaded)
    if not ok:
        st.sidebar.error(reason)
        return False

    ext = uploaded.name.split(".")[-1].lower()
    if ext == "parquet":
        file_type = "parquet"
    elif ext in ("xlsx", "xls"):
        file_type = ext
    elif ext == "tsv":
        file_type = "tsv"
    else:
        file_type = "csv"

    with st.sidebar.status("Loading dataset...", expanded=True) as status:
        with exception_boundary("File loading"):
            t0 = pd.Timestamp.now()
            df = load_with_memory_optimization(uploaded, file_type)
            working_df, sampling_meta = apply_sampling_if_needed(df)
            st.session_state["raw_df"] = df
            st.session_state["working_df"] = working_df
            st.session_state["sampling_metadata"] = sampling_meta
            st.session_state["load_time_ms"] = (
                pd.Timestamp.now() - t0
            ).total_seconds() * 1000

        # If loading failed above, exception_boundary will have displayed an error
        # and the working set won't be in session state — bail early.
        if st.session_state.get("working_df") is None:
            return False

        with exception_boundary("Column profiling"):
            t0 = pd.Timestamp.now()
            profiler = DataProfiler()
            profiles = profiler.profile_dataframe(working_df)
            st.session_state["column_profiles"] = profiles
            st.session_state["column_metadata"] = build_column_metadata(
                working_df, profiles
            )
            st.session_state["profile_time_ms"] = (
                pd.Timestamp.now() - t0
            ).total_seconds() * 1000

        ohlc = detect_ohlc_columns(working_df)
        st.session_state["ohlc_mapping"] = ohlc
        geo_cols = [c for c, p in profiles.items() if p.is_geo_candidate]
        st.session_state["geo_column"] = geo_cols[0] if geo_cols else None

        status.update(
            label=f"Loaded {len(working_df):,} rows × {len(working_df.columns)} cols",
            state="complete",
        )

    if sampling_meta.get("sampled"):
        st.sidebar.info(
            f"Sampled {sampling_meta['sampled_rows']:,} of "
            f"{sampling_meta['original_rows']:,} rows for performance."
        )

    return True
