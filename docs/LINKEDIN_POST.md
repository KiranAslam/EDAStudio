# LinkedIn Post Draft

I built **EDA Studio**, a Streamlit-based exploratory data analysis app focused on safe, dtype-aware charting and a clean user experience.

What it does:
- Upload CSV, Excel, TSV, or Parquet files
- Auto-profile columns into continuous, categorical, temporal, and geo-like types
- Block invalid chart combinations before they reach the renderer
- Support charts like histogram, scatter, line, time series, bubble, heatmap, treemap, parcoords, and more
- Auto-sample large files and sanitize data before plotting
- Export charts and working data for further analysis

What I learned while building it:
- Good analytics UX is as much about guardrails as it is about visualization
- Data type handling matters a lot when building reliable charts
- A small amount of orchestration can make the app feel much more professional

Highlights:
- Defensive file validation
- Memory-aware loading
- Dtype coercion for selected chart inputs
- Reusable Plotly chart factory
- No raw tracebacks in the production UI

This project started as a chart builder, but it evolved into a more complete data exploration tool.

If you're working with messy tabular data and want a faster first pass at exploration, this kind of workflow can save a lot of time.

#Python #Streamlit #Plotly #DataAnalysis #EDA #DataScience #Analytics #PortfolioProject

Optional shorter version:

I built a Streamlit app called **EDA Studio** for dtype-aware exploratory data analysis and chart building.

It supports file upload, profiling, safe chart filtering, auto-sampling, and Plotly exports. The main focus was making the UX clean, reliable, and practical for real tabular data.

It turned into a strong portfolio project because it combines data validation, profiling, chart orchestration, and polished UI design in one app.
