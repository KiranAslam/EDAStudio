# Architecture

## Layers

1. **UI** (`ui/`) — Streamlit tabs: Dashboard, Automated EDA, Chart Builder, Column Dictionary
2. **Core** (`core/`) — Profiling, dtype coercion, sanitization, Plotly figure builders
3. **Utils** (`utils/`) — Upload validation, memory checks, error boundaries
4. **Config** (`config/`) — Limits and chart eligibility matrix

## Data flow

Upload → validate → memory check → load (dtype-optimized) → sample if huge → profile columns → user selects chart → coerce dtypes → sanitize → cardinality guard → Plotly render.

## Session state contract

On new file upload (MD5 hash change): `reset_data_state()` clears all data keys before reload. Cache keys use `uploaded_file_id` hash to prevent cross-file contamination.

## Dtype engine

When a column is selected for plotting:

- Object columns with >80% parseable dates → `pd.to_datetime`
- Object columns with >90% numeric → `pd.to_numeric`
- User overrides for `AMBIGUOUS` integers stored in `column_overrides`

## Error handling

`@safe_component` and `exception_boundary` ensure users see branded error cards (MEM_001, VAL_001, SYS_001) while full tracebacks go to logs only.
