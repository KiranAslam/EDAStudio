import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from scipy import stats

from core.cardinality_guard import enforce_cardinality_limit, enforce_scatter_density_limit
from config.limits import LIMITS


def build_plotly_figure(df: pd.DataFrame, config: dict) -> go.Figure:
    chart_type = config["chart_type"]
    x_col = config.get("x_col")
    y_col = config.get("y_col")
    color_col = config.get("color_col")
    size_col = config.get("size_col")
    agg_func = config.get("agg_func", "count")
    trendline = config.get("trendline", False)
    log_y = config.get("log_y", False)
    hierarchy_cols = config.get("hierarchy_cols", [])
    dimensions = config.get("dimensions", [])
    corr_method = config.get("corr_method", "pearson")
    corr_threshold = config.get("corr_threshold", 0.0)
    ohlc = config.get("ohlc")
    location_mode = config.get("location_mode", "ISO-3")

    if color_col in (None, "None", ""):
        color_col = None
    if size_col in (None, "None", ""):
        size_col = None

    if chart_type == "histogram":
        nbins = config.get("nbins")
        fig = px.histogram(df, x=x_col, color=color_col, nbins=nbins or None)
        if log_y:
            fig.update_layout(yaxis_type="log")
        return fig

    if chart_type == "bar":
        x_series = df[x_col]
        if config.get("top_n"):
            x_series, _ = enforce_cardinality_limit(
                x_series, "bar", df[y_col] if y_col else None, config["top_n"], agg_func
            )
        if y_col and agg_func != "count":
            agg_df = (
                pd.DataFrame({"x": x_series, "y": df[y_col]})
                .groupby("x")["y"]
                .agg(agg_func)
                .reset_index()
            )
            fig = px.bar(agg_df, x="x", y="y", color=color_col if color_col else None)
        else:
            counts = x_series.value_counts().reset_index()
            counts.columns = ["x", "y"]
            fig = px.bar(counts, x="x", y="y")
        fig.update_layout(yaxis_rangemode="tozero")
        return fig

    if chart_type == "scatter":
        df, density = enforce_scatter_density_limit(df, x_col, y_col)
        render_mode = density.get("render_mode", "svg")
        fig = px.scatter(
            df,
            x=x_col,
            y=y_col,
            color=color_col,
            size=size_col,
            trendline="ols" if trendline else None,
            render_mode=render_mode,
            opacity=0.4 if len(df) > 1000 else 0.8,
        )
        return fig

    if chart_type in ("line", "timeseries"):
        fig = px.line(df, x=x_col, y=y_col, color=color_col)
        fig.update_traces(connectgaps=False)
        if chart_type == "timeseries":
            fig.update_xaxes(
                rangeslider_visible=True,
                rangeselector=dict(
                    buttons=[
                        dict(count=1, label="1M", step="month"),
                        dict(count=6, label="6M", step="month"),
                        dict(count=1, label="1Y", step="year"),
                        dict(step="all", label="All"),
                    ]
                ),
            )
        return fig

    if chart_type == "box":
        fig = px.box(df, x=x_col, y=y_col, color=color_col, points="outliers")
        return fig

    if chart_type == "violin":
        fig = px.violin(
            df, x=x_col, y=y_col, color=color_col, box=True, points="outliers"
        )
        return fig

    if chart_type == "pie":
        x_series, _ = enforce_cardinality_limit(df[x_col], "pie", top_n_override=7)
        if y_col:
            agg_df = pd.DataFrame({"labels": x_series, "values": df[y_col]}).groupby(
                "labels"
            )["values"].sum().reset_index()
        else:
            agg_df = x_series.value_counts().reset_index()
            agg_df.columns = ["labels", "values"]
        fig = px.pie(agg_df, names="labels", values="values")
        return fig

    if chart_type == "heatmap_crosstab":
        x_series, _ = enforce_cardinality_limit(df[x_col], "heatmap_crosstab")
        y_series, _ = enforce_cardinality_limit(df[y_col], "heatmap_crosstab")
        ct = pd.crosstab(x_series, y_series)
        fig = px.imshow(ct, color_continuous_scale="Blues", aspect="auto")
        return fig

    if chart_type == "heatmap_correlation":
        cols = dimensions or df.select_dtypes(include="number").columns.tolist()
        corr = df[cols].replace([np.inf, -np.inf], np.nan).corr()
        mask = np.abs(corr) < corr_threshold
        corr_masked = corr.mask(mask)
        fig = px.imshow(
            corr_masked,
            color_continuous_scale="RdBu_r",
            zmin=-1,
            zmax=1,
            aspect="auto",
            text_auto=".2f",
        )
        return fig

    if chart_type == "scatter_matrix":
        dims = dimensions[: LIMITS["PAIR_PLOT_MAX_COLUMNS"]]
        sample = df
        if len(df) > 2000:
            sample = df.sample(2000, random_state=42)
        fig = px.scatter_matrix(
            sample,
            dimensions=dims,
            color=color_col if color_col in sample.columns else None,
        )
        return fig

    if chart_type == "treemap":
        path = hierarchy_cols if hierarchy_cols else [x_col]
        fig = px.treemap(df, path=path, values=y_col)
        return fig

    if chart_type == "parcoords":
        dims = dimensions
        fig = go.Figure(
            data=go.Parcoords(
                dimensions=[
                    dict(label=c, values=df[c]) for c in dims if c in df.columns
                ],
                line=dict(
                    color=df[color_col] if color_col and color_col in df.columns else None,
                    colorscale="Viridis",
                    showscale=bool(color_col),
                ),
            )
        )
        return fig

    if chart_type == "candlestick" and ohlc:
        fig = go.Figure(
            data=[
                go.Candlestick(
                    x=df[ohlc["date"]],
                    open=df[ohlc["open"]],
                    high=df[ohlc["high"]],
                    low=df[ohlc["low"]],
                    close=df[ohlc["close"]],
                )
            ]
        )
        return fig

    if chart_type == "choropleth":
        fig = px.choropleth(
            df,
            locations=x_col,
            color=y_col,
            locationmode=location_mode,
            color_continuous_scale="Viridis",
        )
        return fig

    if chart_type == "kde":
        clean = df[x_col].replace([np.inf, -np.inf], np.nan).dropna()
        kde = stats.gaussian_kde(clean)
        xs = np.linspace(clean.min(), clean.max(), 200)
        ys = kde(xs)
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=xs, y=ys, fill="tozeroy", name="KDE"))
        fig.add_trace(go.Histogram(x=clean, histnorm="probability density", opacity=0.4))
        return fig

    raise ValueError(f"Unsupported chart type: {chart_type}")
