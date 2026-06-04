# Deployment — Streamlit Community Cloud

## Prerequisites

- Public GitHub repository
- `requirements.txt` at repo root
- Main file: `app.py`

## Steps

1. Push code to `main` branch.
2. Visit https://share.streamlit.io and sign in with GitHub.
3. **New app** → pick repository `EDAStudio` (or your fork).
4. **Main file path:** `app.py`
5. **Advanced:** Python 3.11
6. Click **Deploy**.

## Post-deploy

- Add your live URL to `README.md`
- Test upload with `data/sample_sales.csv`
- Verify Automated EDA and Chart Builder tabs

## Tuning for Cloud RAM (1 GB)

In `config/limits.py`:

- `SAMPLE_TARGET_ROWS = 100_000` (or lower)
- `MAX_FILE_SIZE_MB = 100` if users hit OOM

## Secrets (optional)

For Mapbox or API keys later, add `.streamlit/secrets.toml` locally (gitignored) and configure in Cloud **Settings → Secrets**.
