# EDA Studio Project Overview

## Summary
EDA Studio is a Streamlit-based exploratory data analysis and chart-building application that focuses on safe, dtype-aware visualization. It helps users upload tabular data, understand the dataset quickly, and build charts without invalid axis combinations or noisy tracebacks.

## What the project does
- Uploads CSV, TSV, Excel, or Parquet files.
- Validates file size and structure before loading.
- Optimizes memory usage during read time.
- Profiles columns into analytical types such as continuous, categorical, temporal, geo, and ordered numeric.
- Offers a dashboard with summary metrics, previews, and null diagnostics.
- Provides automated EDA views for distributions, correlations, categories, outliers, and scatter matrices.
- Provides a custom chart builder with dtype filtering for chart options.
- Supports exports for chart HTML, PNG, chart config JSON, EDA config JSON, and working CSV.

## Core design principles
### 1. Safe by default
The app blocks invalid chart combinations, checks column eligibility before rendering, and sanitizes data before chart creation.

### 2. Dtype-aware interactions
Chart inputs change based on the underlying column type. This reduces user error and makes the builder feel guided rather than generic.

### 3. Production-friendly UI
The interface uses a polished dashboard layout, sidebar-based upload flow, helpful status messages, and no raw tracebacks in the user interface.

### 4. Scalable data handling
Large files are auto-sampled, columns are coerced only when needed, and charts include cardinality and scatter-density guards.

## Important modules
### `app.py`
Main entry point. Initializes session state, renders the upload sidebar, dashboard tabs, and export controls.

### `ui/upload_panel.py`
Loads and validates uploaded datasets, profiles columns, and stores working data in session state.

### `ui/overview_panel.py`
Shows dataset KPIs, preview rows, null summary, and dtype summary.

### `ui/eda_panel.py`
Renders automated EDA views such as histograms, category bars, correlations, outliers, and pair plots.

### `ui/chart_builder.py`
Builds custom charts from the eligibility matrix and handles chart-specific controls.

### `core/profiler.py`
Classifies columns into analytical types and computes useful summary statistics.

### `core/dtype_engine.py`
Coerces selected columns when a chart requires dates, numbers, or categorical display types.

### `core/plot_sanitizer.py`
Removes invalid rows for a chart and reports data-quality warnings.

### `core/charts/__init__.py`
Builds Plotly figures for all supported chart types.

### `utils/data_loader.py`
Reads files with memory optimization and category conversion safeguards.

## Supported chart types
- Histogram
- Bar chart
- Scatter plot
- Bubble plot
- Line chart
- Time series
- Box plot
- Violin plot
- Pie chart
- Heatmap cross-tab
- Correlation heatmap
- Scatter matrix
- Treemap
- Parallel coordinates


## Data flow
1. User uploads a dataset.
2. Validation checks file type, readability, and size.
3. Loader reads the data using memory-friendly rules.
4. Session state stores raw and working data.
5. Column profiler classifies fields and computes metadata.
6. The dashboard and chart builder filter choices by column type.
7. Selected columns are coerced and sanitized for the chosen chart.
8. Plotly renders the final chart.

## Strengths
- Clear separation between UI, core logic, and utilities.
- Good defensive checks for file handling and chart creation.
- Strong foundation for a real analytics product.
- Test coverage now includes loader, profiler, dtype engine, sanitizer, chart availability, and chart rendering behavior.
- The app is already close to a portfolio-ready demo.

## Current limitations
- Automated EDA is helpful but still lighter than a full analytics platform.
- Some chart types depend on data shape and may still be limited by sample quality or category cardinality.
- The app is still most effective for medium-sized tabular datasets rather than enterprise-scale data.

