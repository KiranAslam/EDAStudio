# EDA Studio

Production-grade **exploratory data analysis** and **custom chart builder** built with Python, Streamlit, and Plotly.

![Python](https://img.shields.io/badge/python-3.11+-blue)
![Streamlit](https://img.shields.io/badge/streamlit-1.32+-red)

## Features

- **Professional dashboard** — KPI metrics, data preview, null summary, dtype overview
- **Automated EDA** — distributions, category frequencies, correlation heatmap (masked), outlier detection (IQR), pair plots
- **Custom chart builder** — 15+ chart types with dtype-aware axis filtering (no invalid chart combinations)
- **Smart dtype engine** — string dates (e.g. `order_date`) auto-convert to `datetime` when selected
- **Defensive engineering** — no Python tracebacks in UI; memory guards; auto-sampling for large files
- **Exports** — chart HTML/PNG, chart config JSON, EDA config JSON, working CSV download
- **Column dictionary** — rename display labels, override ambiguous integers, mark ordered axes
- **OHLC auto-detection** — candlestick preset when open/high/low/close columns exist
- **Geo detection** — choropleth when ISO-like geographic columns are found

## Quick start (local)

```bash
cd EDAStudio
python -m venv .venv
.venv\Scripts\activate          # Windows
pip install -r requirements.txt
streamlit run app.py
```

Try the sample file: [`data/sample_sales.csv`](data/sample_sales.csv)

## Deploy on Streamlit Community Cloud

1. Push this repo to **GitHub** (public repo required for free tier).
2. Go to [share.streamlit.io](https://share.streamlit.io) → **New app**.
3. Select your repo, branch `main`, main file path: `app.py`.
4. Deploy. Cloud provides ~1 GB RAM — large files are auto-sampled.

### One-time GitHub setup

```bash
git init
git add .
git commit -m "Initial release: EDA Studio dashboard"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/EDAStudio.git
git push -u origin main
```

Replace `YOUR_USERNAME` with your GitHub username.

## Project structure

```
app.py                 # Entry point
config/                # limits.py, chart_eligibility.py
core/                  # profiler, dtype_engine, charts, sanitization
ui/                    # dashboard tabs
utils/                 # validation, loading, errors
data/                  # sample datasets
docs/                  # architecture & deployment guides
```

## Chart types

Histogram, Bar, Scatter, Line, Time Series, Box, Violin, Pie, Heatmap (cross-tab & correlation), Pair Plot, Treemap, Parallel Coordinates, Candlestick (OHLC), Choropleth.

## Configuration

Edit [`config/limits.py`](config/limits.py) to tune file size caps, sampling thresholds, and scatter WebGL limits.

## Documentation

- [Architecture](docs/ARCHITECTURE.md)
- [Development guide](docs/DEVELOPMENT.md)
- [Deployment](docs/DEPLOYMENT.md)

## License

MIT — use freely for learning and production demos.
