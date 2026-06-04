# Development

## Setup

```bash
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -r requirements.txt
streamlit run app.py
```

## Adding a chart type

1. Add spec to `config/chart_eligibility.py`
2. Implement branch in `core/charts/__init__.py`
3. Add availability logic in `ui/chart_builder.py` `_chart_availability`
4. Extend `core/plot_sanitizer.py` MIN_ROWS if needed

## Gate tests (manual)

- Upload empty file → error, no traceback
- Upload sample_sales.csv → line chart on `order_date` works (string→datetime)
- 200+ category bar → Top-N truncation message
- Upload file A then B → data reflects B only

## Code style

Keep limits in `config/limits.py` only. Wrap new UI renderers with `@safe_component`.
