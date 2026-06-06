import json
import importlib.util
import pandas as pd
import streamlit as st

from config.chart_eligibility import AGGREGATE_FUNCTIONS, CHART_ELIGIBILITY
from core.cardinality_guard import enforce_cardinality_limit
from core.charts import build_plotly_figure
from core.dtype_engine import (
    apply_coercions_to_dataframe,
    detect_ohlc_columns,
    get_eligible_columns,
)
from core.plot_sanitizer import sanitize_for_plot
from utils.error_handling import safe_component


def _chart_availability(profiles: dict, chart_key: str) -> tuple[bool, str]:
    spec = CHART_ELIGIBILITY[chart_key]
    if chart_key == "heatmap_correlation":
        n = sum(1 for p in profiles.values() if p.eligible_for_correlation)
        if n < spec["min_numeric_for_corr"]:
            return False, f"Needs {spec['min_numeric_for_corr']}+ numerical columns (have {n})."
        return True, ""
    if chart_key == "scatter_matrix":
        n = sum(1 for p in profiles.values() if p.eligible_for_correlation)
        if n < 3:
            return False, "Pair plot needs 3+ numerical columns."
        return True, ""
    if chart_key == "candlestick":
        ohlc = st.session_state.get("ohlc_mapping") or detect_ohlc_columns(
            st.session_state.get("working_df", pd.DataFrame())
        )
        if not ohlc:
            return False, "No OHLC columns detected (open/high/low/close + date)."
        return True, ""
    if chart_key == "choropleth":
        geo = st.session_state.get("geo_column")
        if not geo:
            return False, "No geographic identifier column detected."
        return True, ""
    x_types = spec.get("x", [])
    y_types = spec.get("y", [])
    if x_types:
        x_ok = get_eligible_columns(profiles, x_types)
        if not x_ok and chart_key not in ("heatmap_correlation", "scatter_matrix", "parcoords"):
            return False, f"No eligible X columns for {spec['label']}."
    if y_types and "NONE" not in y_types:
        y_ok = get_eligible_columns(profiles, [t for t in y_types if t != "NONE"])
        if not y_ok and chart_key not in ("histogram",):
            return False, f"No eligible Y columns for {spec['label']}."
    return True, ""


@safe_component("Chart builder failed.")
def render_chart_builder():
    df = st.session_state.get("working_df")
    profiles = st.session_state.get("column_profiles", {})
    if df is None:
        st.info("Upload a dataset to build custom charts.")
        return

    st.markdown("### Custom chart builder")
    st.caption("Charts are filtered by column type — invalid combinations are blocked.")

    available = []
    disabled_notes = {}
    for key in CHART_ELIGIBILITY:
        ok, msg = _chart_availability(profiles, key)
        if ok:
            available.append(key)
        else:
            disabled_notes[key] = msg

    chart_labels = {k: CHART_ELIGIBILITY[k]["label"] for k in available}
    if not available:
        st.error("No chart types available for this dataset.")
        for k, msg in disabled_notes.items():
            st.caption(f"• {CHART_ELIGIBILITY[k]['label']}: {msg}")
        return

    chart_type = st.selectbox(
        "Chart type",
        available,
        format_func=lambda k: chart_labels[k],
    )
    spec = CHART_ELIGIBILITY[chart_type]
    if chart_type in disabled_notes:
        st.warning(disabled_notes[chart_type])

    st.markdown(f"*{spec['description']}*")

    col_left, col_right = st.columns(2)
    x_col = y_col = color_col = size_col = None
    agg_func = "count"
    hierarchy_cols = []
    dimensions = []
    trendline = False
    log_y = False
    top_n = None

    with col_left:
        x_eligible = get_eligible_columns(profiles, spec.get("x", []))
        if spec.get("x"):
            if x_eligible:
                x_col = st.selectbox("X-axis", x_eligible)
            else:
                st.error("No eligible X-axis columns.")

        y_spec = [t for t in spec.get("y", []) if t != "NONE"]
        y_eligible = get_eligible_columns(profiles, y_spec) if y_spec else []
        if y_spec or chart_type in ("bar", "pie"):
            if "NONE" in spec.get("y", []) and chart_type in ("bar", "pie"):
                y_options = ["(Count / frequency)"] + y_eligible
                y_choice = st.selectbox("Y-axis / Value", y_options)
                if y_choice != "(Count / frequency)":
                    y_col = y_choice
                    agg_func = st.selectbox("Aggregate", AGGREGATE_FUNCTIONS[1:])
                else:
                    agg_func = "count"
            elif y_eligible:
                y_col = st.selectbox("Y-axis", y_eligible)
                if chart_type == "bar":
                    agg_func = st.selectbox("Aggregate", AGGREGATE_FUNCTIONS)
            elif chart_type not in (
                "histogram",
                "heatmap_correlation",
                "scatter_matrix",
                "parcoords",
            ):
                st.error("No eligible Y-axis columns.")

    with col_right:
        color_spec = spec.get("color", [])
        if color_spec:
            color_eligible = ["None"] + get_eligible_columns(
                profiles, [t for t in color_spec if t != "NONE"]
            )
            color_col = st.selectbox("Color", color_eligible)
            if color_col == "None":
                color_col = None

        if spec.get("size"):
            size_choices = get_eligible_columns(profiles, [t for t in spec["size"] if t != "NONE"])
            if chart_type == "bubble":
                size_eligible = size_choices
            else:
                size_eligible = ["None"] + size_choices
            size_col = st.selectbox("Size", size_eligible)
            if size_col == "None":
                size_col = None

    if chart_type == "scatter":
        trendline = st.checkbox("Show OLS trendline", value=False)
        if trendline and importlib.util.find_spec("statsmodels") is None:
            st.warning("OLS trendline needs `statsmodels`; rendering the scatter without trendline.")
            trendline = False
    if chart_type == "histogram":
        log_y = st.checkbox("Log Y-axis", value=False)

    if chart_type in ("bar", "pie", "box", "violin"):
        x_for_card = x_col
        if x_for_card and profiles.get(x_for_card):
            n_u = profiles[x_for_card].n_unique
            if n_u > CHART_ELIGIBILITY.get("pie", {}).get("warn", 5) or (
                chart_type == "bar" and n_u > 30
            ):
                top_n = st.number_input(
                    "Top N categories (+ Other)",
                    min_value=5,
                    max_value=50,
                    value=20 if chart_type == "bar" else 7,
                )

    if chart_type == "treemap":
        cat_cols = get_eligible_columns(profiles, ["CATEGORICAL"])
        hierarchy_cols = st.multiselect("Hierarchy path (ordered)", cat_cols, max_selections=3)

    if chart_type in ("heatmap_correlation", "scatter_matrix", "parcoords"):
        num_cols = [c for c, p in profiles.items() if p.eligible_for_correlation]
        dimensions = st.multiselect(
            "Numerical columns",
            num_cols,
            default=num_cols[: min(8, len(num_cols))],
            max_selections=12 if chart_type == "parcoords" else 8,
        )

    if chart_type == "line" and x_col:
        p = profiles.get(x_col)
        if p and p.analytical_type not in ("TEMPORAL", "CONTINUOUS_ORDERED"):
            st.warning(
                "Line charts should use time or ordered axes. Consider scatter plot instead."
            )
            if st.checkbox("Treat X as ordered sequence", key=f"ordered_{x_col}"):
                st.session_state.setdefault("ordered_columns", set()).add(x_col)
                profiles[x_col].analytical_type = "CONTINUOUS_ORDERED"

    if chart_type == "violin" and x_col and y_col:
        group_n = df.groupby(x_col)[y_col].count()
        small = group_n[group_n < 30]
        for g, n in small.items():
            st.warning(f"Group '{g}' has n={n}. KDE may be unreliable.")

    coerce_cols = [c for c in [x_col, y_col, color_col, size_col] if c]
    plot_df = df.copy()
    if coerce_cols:
        plot_df, coercion_reports = apply_coercions_to_dataframe(plot_df, coerce_cols)
        for r in coercion_reports:
            if r.converted or r.warnings:
                msg = f"**{r.column}**: {r.original_dtype} → {r.coerced_dtype}"
                if r.warnings:
                    msg += " — " + "; ".join(r.warnings)
                st.caption(msg)

    ohlc = st.session_state.get("ohlc_mapping")
    config = {
        "chart_type": chart_type,
        "x_col": x_col,
        "y_col": y_col,
        "color_col": color_col,
        "size_col": size_col,
        "agg_func": agg_func,
        "trendline": trendline,
        "log_y": log_y,
        "top_n": top_n,
        "hierarchy_cols": hierarchy_cols,
        "dimensions": dimensions,
        "ohlc": ohlc if chart_type == "candlestick" else None,
        "corr_threshold": st.session_state.get("eda_corr_threshold", 0.0),
    }
    st.session_state["chart_config"] = config

    if st.button("Generate chart", type="primary"):
        try:
            if chart_type in ("bar", "pie", "box", "violin") and x_col:
                plot_df = plot_df.copy()
                plot_df[x_col], card_report = enforce_cardinality_limit(
                    plot_df[x_col],
                    "pie" if chart_type == "pie" else chart_type,
                    plot_df[y_col] if y_col else None,
                    top_n,
                    agg_func,
                )
                if card_report.get("truncated"):
                    st.info(card_report["action_taken"])

            clean_df, report = sanitize_for_plot(
                plot_df,
                x_col,
                y_col,
                color_col,
                size_col,
                chart_type=chart_type if chart_type != "timeseries" else "line",
                trendline=trendline,
            )
            if report.warnings:
                with st.expander(f"Data quality notes ({len(report.warnings)})"):
                    for w in report.warnings:
                        st.warning(w)

            fig = build_plotly_figure(clean_df, config)
            st.plotly_chart(fig, use_container_width=True)

            col_a, col_b, col_c = st.columns(3)
            with col_a:
                st.download_button(
                    "Download HTML",
                    fig.to_html(include_plotlyjs="cdn"),
                    f"chart_{chart_type}.html",
                    "text/html",
                )
            with col_b:
                try:
                    img_bytes = fig.to_image(format="png", width=1200, height=700)
                    st.download_button(
                        "Download PNG",
                        img_bytes,
                        f"chart_{chart_type}.png",
                        "image/png",
                    )
                except Exception:
                    st.caption("PNG export requires kaleido.")
            with col_c:
                st.download_button(
                    "Download chart config (JSON)",
                    json.dumps(config, indent=2, default=str),
                    f"chart_{chart_type}_config.json",
                    "application/json",
                )
        except ValueError as e:
            st.error(str(e))
        except Exception as e:
            st.error(f"Chart failed: {type(e).__name__}: {str(e)[:300]}")
