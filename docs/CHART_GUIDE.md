# Chart Guide

This guide summarizes the chart types currently implemented in EDA Studio and the column types they expect.

## Core rules

- Charts are filtered by the analytical type of the selected columns.
- Object columns are coerced when possible before plotting.
- High-cardinality categorical columns may be truncated to Top-N plus `Other`.
- Scatter plots use WebGL or sampling when row counts are large.

## Implemented charts

### Univariate

- Histogram: one continuous column.
- Bar chart: one categorical column, optionally aggregated by a numeric value.
- Pie chart: one categorical column with a recommended Top-7 cap.
- Box plot: categorical X, continuous Y.
- Violin plot: categorical X, continuous Y.

### Bivariate

- Scatter plot: continuous X and Y, optional color/size.
- Line chart: temporal or ordered X with continuous Y.
- Time series: line chart with a range slider.
- Heatmap (cross-tab): two categorical columns.
- Treemap: hierarchical categorical path plus value column.
- Candlestick: OHLC columns plus date column.
- Choropleth: geographic identifier plus numeric value.

### Multivariate

- Correlation heatmap: 2+ numeric columns.
- Scatter matrix: 3+ numeric columns, capped at 8 columns.
- Parallel coordinates: numeric multivariate profiles.

## Selection notes

- String dates such as `order_date` are promoted to temporal columns when they parse reliably.
- Small integer domains such as `0/1` are treated as categorical.
- Ambiguous integer columns can be marked as ordered in the Column Dictionary.

## Practical limits

- Very large categorical domains are truncated automatically.
- Large scatter plots switch to WebGL or sampling to keep the browser responsive.
- Unsupported combinations are hidden in the chart builder instead of failing at render time.
