"""
Shared UI Components, Modern CSS Styling, and Session State Management.
Inspired by modern educational design systems with an original aesthetic.
"""

import streamlit as st
from algorithms.grammar import CFG, get_predefined_grammars
from algorithms.pda import PDA, get_predefined_pdas

CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Fira+Code:wght@400;500;600;700&display=swap');

:root {
    --primary: #4f46e5;
    --primary-light: #6366f1;
    --primary-dark: #3730a3;
    --secondary: #0f172a;
    --accent: #06b6d4;
    --success: #10b981;
    --warning: #f59e0b;
    --danger: #f43f5e;
    --bg-card: #ffffff;
    --border-color: #e2e8f0;
}

html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    color: #1e293b;
}

code, pre {
    font-family: 'Fira Code', monospace !important;
}

/* App Header / Hero Banner */
.hero-container {
    background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 50%, #0f172a 100%);
    border-radius: 16px;
    padding: 32px 36px;
    color: #f8fafc;
    border: 1px solid rgba(255, 255, 255, 0.1);
    box-shadow: 0 20px 25px -5px rgba(15, 23, 42, 0.25), 0 8px 10px -6px rgba(15, 23, 42, 0.25);
    margin-bottom: 28px;
    position: relative;
    overflow: hidden;
}

.hero-container::before {
    content: '';
    position: absolute;
    top: -50%;
    right: -20%;
    width: 300px;
    height: 300px;
    background: radial-gradient(circle, rgba(99, 102, 241, 0.2) 0%, transparent 70%);
    border-radius: 50%;
    pointer-events: none;
}

.hero-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 4px 12px;
    border-radius: 9999px;
    background: rgba(99, 102, 241, 0.2);
    border: 1px solid rgba(165, 180, 252, 0.3);
    color: #c7d2fe;
    font-size: 0.75rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-bottom: 12px;
}

.hero-title {
    font-size: 2.25rem;
    font-weight: 800;
    letter-spacing: -0.025em;
    margin-bottom: 8px;
    background: linear-gradient(90deg, #ffffff 0%, #c7d2fe 50%, #38bdf8 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.hero-subtitle {
    font-size: 1.05rem;
    color: #94a3b8;
    line-height: 1.6;
    max-width: 820px;
}

/* Feature & Metric Cards */
.feature-card {
    background: #ffffff;
    border-radius: 14px;
    padding: 22px;
    border: 1px solid #e2e8f0;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.04), 0 2px 4px -2px rgba(0, 0, 0, 0.04);
    transition: all 0.2s ease-in-out;
    height: 100%;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
}

.feature-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 12px 20px -3px rgba(0, 0, 0, 0.08), 0 4px 6px -4px rgba(0, 0, 0, 0.04);
    border-color: #cbd5e1;
}

.feature-icon-badge {
    width: 44px;
    height: 44px;
    border-radius: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.4rem;
    margin-bottom: 14px;
}

.icon-blue { background: #eff6ff; color: #2563eb; }
.icon-purple { background: #f5f3ff; color: #7c3aed; }
.icon-emerald { background: #ecfdf5; color: #059669; }
.icon-amber { background: #fffbeb; color: #d97706; }
.icon-rose { background: #fff1f2; color: #e11d48; }

/* Badges */
.badge-tag {
    display: inline-flex;
    align-items: center;
    padding: 4px 10px;
    font-size: 0.78rem;
    font-weight: 600;
    border-radius: 6px;
    margin-right: 6px;
    margin-bottom: 6px;
    font-family: 'Fira Code', monospace;
}

.badge-var { background-color: #ede9fe; color: #6d28d9; border: 1px solid #ddd6fe; }
.badge-term { background-color: #d1fae5; color: #047857; border: 1px solid #a7f3d0; }
.badge-start { background-color: #fef3c7; color: #b45309; border: 1px solid #fde68a; }
.badge-eps { background-color: #fee2e2; color: #b91c1c; border: 1px solid #fecaca; }
.badge-pill { background-color: #f1f5f9; color: #475569; border: 1px solid #e2e8f0; }

/* Status Banners */
.status-banner-accepted {
    background: linear-gradient(90deg, #ecfdf5 0%, #f0fdf4 100%);
    border: 1px solid #86efac;
    border-left: 5px solid #10b981;
    border-radius: 10px;
    padding: 16px 20px;
    color: #065f46;
    margin: 16px 0;
}

.status-banner-rejected {
    background: linear-gradient(90deg, #fff1f2 0%, #fff5f5 100%);
    border: 1px solid #fca5a5;
    border-left: 5px solid #ef4444;
    border-radius: 10px;
    padding: 16px 20px;
    color: #991b1b;
    margin: 16px 0;
}

/* PDA Tape Reader Ribbon */
.tape-container {
    background: #0f172a;
    border-radius: 12px;
    padding: 16px 20px;
    color: #f8fafc;
    border: 1px solid #334155;
    margin: 14px 0;
    overflow-x: auto;
}

.tape-cells {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-top: 8px;
}

.tape-cell {
    width: 44px;
    height: 48px;
    border-radius: 8px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    font-family: 'Fira Code', monospace;
    font-size: 1.1rem;
    font-weight: 700;
    border: 2px solid #334155;
    background: #1e293b;
    color: #94a3b8;
    position: relative;
}

.tape-cell-consumed {
    background: #1e293b;
    color: #64748b;
    border-color: #334155;
    opacity: 0.6;
}

.tape-cell-current {
    background: #4f46e5;
    color: #ffffff;
    border-color: #818cf8;
    box-shadow: 0 0 12px rgba(99, 102, 241, 0.6);
    transform: scale(1.08);
}

.tape-cell-unread {
    background: #334155;
    color: #f8fafc;
    border-color: #475569;
}

.tape-pointer {
    font-size: 0.7rem;
    color: #38bdf8;
    text-transform: uppercase;
    font-weight: 700;
    margin-top: 4px;
}

/* PDA Stack Visualizer */
.stack-viewer-card {
    background: #ffffff;
    border-radius: 12px;
    padding: 18px;
    border: 1px solid #e2e8f0;
    box-shadow: 0 2px 4px rgba(0,0,0,0.04);
}

.stack-column {
    display: flex;
    flex-direction: column;
    align-items: stretch;
    gap: 6px;
    max-width: 260px;
    margin: 12px auto;
    border-bottom: 4px solid #334155;
    border-left: 2px dashed #cbd5e1;
    border-right: 2px dashed #cbd5e1;
    padding: 12px 10px 6px 10px;
    border-radius: 0 0 8px 8px;
}

.stack-item {
    background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
    border: 1px solid #cbd5e1;
    border-radius: 6px;
    padding: 8px 12px;
    font-family: 'Fira Code', monospace;
    font-size: 0.95rem;
    font-weight: 600;
    text-align: center;
    color: #1e293b;
    box-shadow: 0 1px 2px rgba(0,0,0,0.05);
}

.stack-item-top {
    background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
    border: 1px solid #f59e0b;
    color: #92400e;
    box-shadow: 0 2px 5px rgba(245, 158, 11, 0.2);
}

/* Sentential Derivation Ribbon */
.derivation-step-card {
    background: #ffffff;
    border-radius: 10px;
    padding: 14px 18px;
    border: 1px solid #e2e8f0;
    margin-bottom: 10px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    font-family: 'Fira Code', monospace;
}

.step-num-badge {
    background: #f1f5f9;
    color: #475569;
    font-weight: 700;
    padding: 3px 8px;
    border-radius: 6px;
    font-size: 0.8rem;
}

/* CYK Triangular Table Layout */
.cyk-table {
    border-collapse: separate;
    border-spacing: 6px;
    margin-top: 14px;
    width: 100%;
}

.cyk-cell {
    background: #f8fafc;
    border: 1px solid #cbd5e1;
    border-radius: 8px;
    padding: 12px 8px;
    text-align: center;
    font-family: 'Fira Code', monospace;
    font-size: 0.88rem;
    transition: all 0.15s;
}

.cyk-cell:hover {
    border-color: #6366f1;
    background: #f5f3ff;
}

.cyk-root-highlight {
    background: #fef08a !important;
    border: 2px solid #ca8a04 !important;
    box-shadow: 0 4px 10px rgba(202, 138, 4, 0.2);
    font-weight: 700;
}

/* Sidebar Custom Styling */
section[data-testid="stSidebar"] {
    background-color: #f8fafc;
    border-right: 1px solid #e2e8f0;
}
</style>
"""


def apply_custom_styles():
    """Inject polished modern CSS stylesheet."""
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


def init_session_state():
    """Initialize persistent session variables."""
    predefined_grammars = get_predefined_grammars()
    predefined_pdas = get_predefined_pdas()

    if "predefined_grammars" not in st.session_state:
        st.session_state.predefined_grammars = predefined_grammars

    if "predefined_pdas" not in st.session_state:
        st.session_state.predefined_pdas = predefined_pdas

    if "selected_grammar_key" not in st.session_state:
        st.session_state.selected_grammar_key = "G1: Balanced anbn"

    if "current_grammar" not in st.session_state:
        g_data = predefined_grammars[st.session_state.selected_grammar_key]
        st.session_state.current_grammar = CFG.from_text(
            g_data["text"],
            start_symbol=g_data["start_symbol"]
        )

    if "selected_pda_key" not in st.session_state:
        st.session_state.selected_pda_key = "PDA: a^n b^n"

    if "current_pda" not in st.session_state:
        st.session_state.current_pda = predefined_pdas[st.session_state.selected_pda_key]


def render_sidebar_grammar_selector():
    """Render sleek grammar controller in the sidebar."""
    st.sidebar.markdown("""
    <div style="padding: 10px 0 6px 0;">
        <span style="font-size: 0.72rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.08em; color: #64748b;">
            Active Grammar Context
        </span>
    </div>
    """, unsafe_allow_html=True)

    grammar_options = list(st.session_state.predefined_grammars.keys())
    selected_key = st.sidebar.selectbox(
        "Select Active Grammar:",
        options=grammar_options,
        index=grammar_options.index(st.session_state.selected_grammar_key)
        if st.session_state.selected_grammar_key in grammar_options else 0,
        key="sidebar_grammar_choice",
        label_visibility="collapsed"
    )

    if selected_key != st.session_state.selected_grammar_key:
        st.session_state.selected_grammar_key = selected_key
        g_data = st.session_state.predefined_grammars[selected_key]
        st.session_state.current_grammar = CFG.from_text(
            g_data["text"],
            start_symbol=g_data["start_symbol"]
        )
        st.rerun()

    # Active grammar summary card in sidebar
    g: CFG = st.session_state.current_grammar
    st.sidebar.markdown(f"""
    <div style="background:#ffffff; border:1px solid #e2e8f0; border-radius:10px; padding:10px 12px; margin-top:8px;">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:4px;">
            <span style="font-size:0.75rem; color:#64748b; font-weight:600;">Start Symbol</span>
            <span class="badge-tag badge-start" style="margin:0;">{g.start_symbol}</span>
        </div>
        <div style="display:flex; justify-content:space-between; align-items:center; font-size:0.75rem; color:#64748b;">
            <span>Variables: <b>{len(g.variables)}</b></span>
            <span>Terminals: <b>{len(g.terminals)}</b></span>
            <span>Rules: <b>{len(g.productions)}</b></span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.sidebar.divider()
