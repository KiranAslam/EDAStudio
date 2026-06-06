DASHBOARD_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,400;0,9..40,600;0,9..40,700;1,9..40,400&display=swap');

    html, body, [class*="css"] {
        font-family: 'DM Sans', system-ui, sans-serif;
        background: radial-gradient(circle at top left, #f8fbff 0%, #ffffff 44%, #f8fafc 100%);
    }

    .block-container {
        padding-top: 1.25rem;
        padding-bottom: 2rem;
        max-width: 1600px;
    }

    .stApp {
        background:
            radial-gradient(circle at top right, rgba(59, 130, 246, 0.08), transparent 22%),
            radial-gradient(circle at bottom left, rgba(15, 23, 42, 0.04), transparent 28%),
            linear-gradient(180deg, #f8fbff 0%, #ffffff 40%, #f8fafc 100%);
    }

    .app-shell {
        display: grid;
        gap: 1rem;
        margin-bottom: 1rem;
    }

    .main-header {
        background: linear-gradient(135deg, #0f172a 0%, #12345a 45%, #0ea5e9 130%);
        padding: 1.5rem 1.75rem;
        border-radius: 18px;
        margin-bottom: 1rem;
        color: #f8fafc;
        box-shadow: 0 18px 40px rgba(15, 23, 42, 0.18);
        position: relative;
        overflow: hidden;
    }
    .main-header::after {
        content: "";
        position: absolute;
        inset: 0;
        background: linear-gradient(135deg, rgba(255,255,255,0.12), transparent 55%);
        pointer-events: none;
    }
    .main-header h1 {
        margin: 0;
        font-size: 2rem;
        font-weight: 700;
        letter-spacing: -0.03em;
    }
    .main-header p {
        margin: 0.35rem 0 0 0;
        opacity: 0.9;
        font-size: 0.95rem;
    }

    .hero-badges {
        display: flex;
        flex-wrap: wrap;
        gap: 0.5rem;
        margin-top: 1rem;
    }
    .hero-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.35rem;
        padding: 0.35rem 0.7rem;
        border-radius: 999px;
        background: rgba(255,255,255,0.12);
        border: 1px solid rgba(255,255,255,0.16);
        font-size: 0.8rem;
        font-weight: 600;
        color: #eef6ff;
    }

    .section-card {
        background: rgba(255, 255, 255, 0.84);
        border: 1px solid #e2e8f0;
        border-radius: 16px;
        box-shadow: 0 8px 28px rgba(15, 23, 42, 0.05);
        padding: 1rem 1.1rem;
        margin-bottom: 1rem;
        backdrop-filter: blur(6px);
    }
    .section-card h3 {
        margin: 0 0 0.3rem 0;
        font-size: 1rem;
        color: #0f172a;
    }
    .section-card p {
        margin: 0;
        color: #64748b;
        font-size: 0.92rem;
    }

    .workflow-grid {
        display: grid;
        grid-template-columns: repeat(3, minmax(0, 1fr));
        gap: 0.75rem;
        margin-top: 0.75rem;
    }
    .workflow-step {
        background: linear-gradient(180deg, #ffffff 0%, #f8fbff 100%);
        border: 1px solid #dbeafe;
        border-radius: 14px;
        padding: 0.85rem 0.95rem;
    }
    .workflow-step .step-kicker {
        font-size: 0.72rem;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: #0284c7;
        font-weight: 700;
        margin-bottom: 0.25rem;
    }
    .workflow-step .step-title {
        font-size: 0.98rem;
        font-weight: 700;
        color: #0f172a;
        margin-bottom: 0.25rem;
    }
    .workflow-step .step-text {
        font-size: 0.88rem;
        color: #64748b;
        line-height: 1.45;
    }

    .metric-card {
        background: linear-gradient(180deg, #ffffff 0%, #f8fbff 100%);
        border: 1px solid #dbeafe;
        border-radius: 14px;
        padding: 1rem 1.1rem;
        box-shadow: 0 8px 22px rgba(15,23,42,0.05);
    }
    .metric-card .label {
        color: #64748b;
        font-size: 0.72rem;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        font-weight: 600;
    }
    .metric-card .value {
        color: #0f172a;
        font-size: 1.45rem;
        font-weight: 700;
        margin-top: 0.25rem;
    }

    .status-banner {
        padding: 0.75rem 1rem;
        border-radius: 12px;
        margin-bottom: 1rem;
        font-size: 0.9rem;
        box-shadow: 0 4px 16px rgba(15,23,42,0.04);
    }
    .status-success { background: #ecfdf5; border-left: 4px solid #10b981; color: #065f46; }
    .status-info { background: #eff6ff; border-left: 4px solid #3b82f6; color: #1e40af; }
    .status-warn { background: #fffbeb; border-left: 4px solid #f59e0b; color: #92400e; }

    .hint-strip {
        border: 1px solid #e2e8f0;
        border-radius: 14px;
        padding: 0.85rem 1rem;
        background: #ffffff;
        color: #475569;
        margin-bottom: 0.9rem;
    }

    .stButton > button {
        border-radius: 12px;
        padding: 0.6rem 1rem;
        border: none;
        font-weight: 700;
        box-shadow: 0 10px 20px rgba(239, 68, 68, 0.18);
    }
    .stButton > button:hover {
        transform: translateY(-1px);
    }

    .stDownloadButton > button {
        border-radius: 12px;
        border: 1px solid #dbeafe;
    }

    div[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #f8fafc 0%, #f1f5f9 100%);
        border-right: 1px solid #e2e8f0;
    }
    div[data-testid="stSidebar"] .block-container {
        padding-top: 1rem;
        padding-bottom: 1.5rem;
    }

    div[data-testid="stFileUploaderDropzone"] {
        border-radius: 14px;
        border: 1px dashed #cbd5e1;
        background: #ffffff;
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: rgba(241, 245, 249, 0.8);
        padding: 8px;
        border-radius: 14px;
        border: 1px solid #e2e8f0;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 10px;
        font-weight: 600;
        padding: 0.5rem 1.25rem;
    }

    .stDataFrame, .stPlotlyChart {
        border-radius: 14px;
        overflow: hidden;
    }

    @media (max-width: 1100px) {
        .workflow-grid {
            grid-template-columns: 1fr;
        }
    }
</style>
"""


def render_header():
    import streamlit as st

    st.markdown(DASHBOARD_CSS, unsafe_allow_html=True)
    st.markdown(
        """
        <div class="main-header">
            <h1>EDA Studio</h1>
            <p>Professional data exploration with dtype-aware charts, safe defaults, and export-ready analytics</p>
            <div class="hero-badges">
                <span class="hero-badge">Upload → Profile → Visualize</span>
                <span class="hero-badge">No invalid chart combos</span>
                <span class="hero-badge">Cloud-ready Streamlit app</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_workflow_hint(has_data: bool) -> None:
    import streamlit as st

    if has_data:
        st.markdown(
            """
            <div class="hint-strip">
                <strong>Working set loaded.</strong> Use the Dashboard for a quick overview, Automated EDA for deterministic analysis, and Chart Builder for custom visualizations.
            </div>
            """,
            unsafe_allow_html=True,
        )
        return

    st.markdown(
        """
        <div class="section-card">
            <h3>Get started in three steps</h3>
            <p>Upload a file, review the dataset profile, then choose a chart or exploratory view.</p>
            <div class="workflow-grid">
                <div class="workflow-step">
                    <div class="step-kicker">Step 1</div>
                    <div class="step-title">Upload data</div>
                    <div class="step-text">Use the sidebar to load CSV, Excel, TSV, or Parquet.</div>
                </div>
                <div class="workflow-step">
                    <div class="step-kicker">Step 2</div>
                    <div class="step-title">Review profile</div>
                    <div class="step-text">Check row counts, nulls, dtypes, and sampling status.</div>
                </div>
                <div class="workflow-step">
                    <div class="step-kicker">Step 3</div>
                    <div class="step-title">Build visuals</div>
                    <div class="step-text">Use dtype-filtered chart options for a guided, safe workflow.</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def metric_row_html(metrics: list[tuple[str, str]]) -> str:
    cards = "".join(
        (
            f'<div class="metric-card">'
            f'<div class="label">{label}</div>'
            f'<div class="value">{value}</div>'
            f'</div>'
        )
        for label, value in metrics
    )
    cols = len(metrics)
    return (
        f'<div style="display:grid; grid-template-columns: repeat({cols}, 1fr); '
        'gap:1rem; margin-bottom:1.25rem;">'
        f"{cards}"
        "</div>"
    )
