DASHBOARD_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,400;0,9..40,600;0,9..40,700;1,9..40,400&display=swap');

    html, body, [class*="css"] {
        font-family: 'DM Sans', system-ui, sans-serif;
    }

    .main-header {
        background: linear-gradient(135deg, #0f172a 0%, #1e3a5f 50%, #0c4a6e 100%);
        padding: 1.75rem 2rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        color: #f8fafc;
        box-shadow: 0 4px 24px rgba(15, 23, 42, 0.15);
    }
    .main-header h1 {
        margin: 0;
        font-size: 1.85rem;
        font-weight: 700;
        letter-spacing: -0.02em;
    }
    .main-header p {
        margin: 0.35rem 0 0 0;
        opacity: 0.88;
        font-size: 0.95rem;
    }

    .metric-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 1rem 1.25rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    }
    .metric-card .label {
        color: #64748b;
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        font-weight: 600;
    }
    .metric-card .value {
        color: #0f172a;
        font-size: 1.5rem;
        font-weight: 700;
        margin-top: 0.25rem;
    }

    .status-banner {
        padding: 0.75rem 1rem;
        border-radius: 8px;
        margin-bottom: 1rem;
        font-size: 0.9rem;
    }
    .status-success { background: #ecfdf5; border-left: 4px solid #10b981; color: #065f46; }
    .status-info { background: #eff6ff; border-left: 4px solid #3b82f6; color: #1e40af; }
    .status-warn { background: #fffbeb; border-left: 4px solid #f59e0b; color: #92400e; }

    div[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #f8fafc 0%, #f1f5f9 100%);
    }
    div[data-testid="stSidebar"] .block-container {
        padding-top: 1rem;
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: #f1f5f9;
        padding: 6px;
        border-radius: 10px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        font-weight: 600;
        padding: 0.5rem 1.25rem;
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
            <p>Professional data exploration — automated EDA and custom visual analytics</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def metric_row_html(metrics: list[tuple[str, str]]) -> str:
    cards = ""
    for label, value in metrics:
        cards += f"""
        <div class="metric-card">
            <div class="label">{label}</div>
            <div class="value">{value}</div>
        </div>
        """
    cols = len(metrics)
    return f"""
    <div style="display:grid; grid-template-columns: repeat({cols}, 1fr);
                gap:1rem; margin-bottom:1.25rem;">
        {cards}
    </div>
    """
