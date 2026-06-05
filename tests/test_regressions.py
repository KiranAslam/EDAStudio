import io

import pandas as pd

from core.cardinality_guard import enforce_cardinality_limit
from core.dtype_engine import detect_ohlc_columns
from core.plot_sanitizer import sanitize_for_plot
from core.profiler import DataProfiler
from utils.validators import validate_uploaded_file


class UploadedFile(io.BytesIO):
    def __init__(self, data: bytes, name: str):
        super().__init__(data)
        self.name = name
        self.size = len(data)


def test_validate_rejects_empty_file():
    result = validate_uploaded_file(UploadedFile(b"", "empty.csv"))
    assert not result.is_valid
    assert any("empty" in error.lower() for error in result.errors)


def test_validate_rejects_unsupported_extension():
    result = validate_uploaded_file(UploadedFile(b"name\nvalue\n", "sample.txt"))
    assert not result.is_valid
    assert any("unsupported" in error.lower() for error in result.errors)


def test_profiler_detects_temporal_and_unusable_columns():
    df = pd.DataFrame(
        {
            "order_date": ["2025-01-01", "2025-01-02", "2025-01-03"],
            "amount": [10.5, 12.0, 11.0],
            "gender": [0, 1, 0],
            "all_null": [None, None, None],
        }
    )
    profiles = DataProfiler().profile_dataframe(df)

    assert profiles["order_date"].analytical_type == "TEMPORAL"
    assert profiles["amount"].analytical_type == "CONTINUOUS"
    assert profiles["gender"].analytical_type == "CATEGORICAL"
    assert profiles["all_null"].analytical_type == "UNUSABLE"


def test_cardinality_limit_truncates_to_top_categories():
    series = pd.Series([f"cat_{i}" for i in range(40)] + ["cat_0"] * 10)
    filtered, report = enforce_cardinality_limit(series, "bar", top_n_override=2)

    assert report["truncated"] is True
    assert report["final_unique"] == 3
    assert "Other" in set(filtered.unique())


def test_sanitize_for_plot_drops_invalid_rows():
    df = pd.DataFrame({"x": [1.0, 2.0, float("inf")], "y": [3.0, 4.0, 5.0]})
    clean, report = sanitize_for_plot(df, "x", "y", chart_type="scatter")

    assert len(clean) == 2
    assert report.inf_values_replaced == 1
    assert report.rows_dropped == 1


def test_detect_ohlc_columns_finds_standard_mapping():
    df = pd.DataFrame(
        {
            "trade_date": ["2025-01-01"],
            "open_price": [10],
            "high_price": [12],
            "low_price": [9],
            "close_price": [11],
        }
    )
    mapping = detect_ohlc_columns(df)

    assert mapping is not None
    assert mapping["date"] == "trade_date"
    assert mapping["open"] == "open_price"
    assert mapping["close"] == "close_price"
