import hashlib

import pandas as pd
import streamlit as st

SESSION_STATE_SCHEMA = {
    "uploaded_file_id": None,
    "uploaded_file_name": None,
    "upload_timestamp": None,
    "upload_count": 0,
    "raw_df": None,
    "working_df": None,
    "sampling_metadata": None,
    "validation_result": None,
    "column_profiles": None,
    "column_metadata": None,
    "column_overrides": {},
    "column_renames": {},
    "ordered_columns": set(),
    "profile_timestamp": None,
    "active_tab": "overview",
    "eda_columns_selected": [],
    "eda_sample_size": None,
    "eda_corr_threshold": 0.0,
    "eda_outlier_fence": 1.5,
    "chart_config": {},
    "last_error": None,
    "load_time_ms": None,
    "profile_time_ms": None,
    "ohlc_mapping": None,
    "geo_column": None,
}

DATA_KEYS = [
    "raw_df",
    "working_df",
    "sampling_metadata",
    "validation_result",
    "column_profiles",
    "column_metadata",
    "column_overrides",
    "column_renames",
    "ordered_columns",
    "profile_timestamp",
    "chart_config",
    "eda_columns_selected",
    "last_error",
    "load_time_ms",
    "profile_time_ms",
    "ohlc_mapping",
    "geo_column",
]


def initialize_session_state() -> None:
    for key, default_value in SESSION_STATE_SCHEMA.items():
        if key not in st.session_state:
            st.session_state[key] = default_value


def reset_data_state() -> None:
    for key in DATA_KEYS:
        st.session_state[key] = SESSION_STATE_SCHEMA[key]
    st.session_state["ordered_columns"] = set()


def detect_new_upload(uploaded_file) -> bool:
    if uploaded_file is None:
        return False
    content_hash = hashlib.md5(uploaded_file.getvalue()).hexdigest()
    if content_hash != st.session_state.get("uploaded_file_id"):
        st.session_state["uploaded_file_id"] = content_hash
        return True
    return False


def get_df_hash() -> str:
    return st.session_state.get("uploaded_file_id", "no_file")


def get_display_name(col: str) -> str:
    return st.session_state.get("column_renames", {}).get(col, col)


def apply_column_renames(df: pd.DataFrame) -> pd.DataFrame:
    renames = st.session_state.get("column_renames", {})
    if not renames:
        return df
    inv = {k: v for k, v in renames.items() if k in df.columns}
    if inv:
        return df.rename(columns=inv)
    return df
