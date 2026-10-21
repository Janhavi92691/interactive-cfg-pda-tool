"""
Interactive CFG & PDA Explorer
Main Streamlit Application Entrypoint.
"""

import streamlit as st

# Configure page metadata
st.set_page_config(
    page_title="Interactive CFG & PDA Explorer",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

from ui.common import apply_custom_styles, init_session_state, render_sidebar_grammar_selector
from ui.home import render_home_page
from ui.cfg_page import render_cfg_page
from ui.derivation_page import render_derivation_page
from ui.cnf_page import render_cnf_page
from ui.gnf_page import render_gnf_page
from ui.cyk_page import render_cyk_page
from ui.pda_page import render_pda_page
from ui.visualization_page import render_visualization_page
from ui.tests_page import render_tests_page
from ui.about_page import render_about_page

# Inject styles and initialize state
apply_custom_styles()
init_session_state()

# Sidebar Navigation
st.sidebar.markdown("""
<div style="text-align: center; margin-bottom: 15px;">
    <h2 style="margin: 0; font-size: 1.35rem; font-weight: 800; color: #0f172a;">🎓 CFG & PDA Explorer</h2>
    <div style="font-size: 0.78rem; color: #64748b; margin-top: 2px;">Theory of Computation Workbench</div>
    <div style="margin-top: 6px;">
        <span class="badge-tag badge-var" style="font-size: 0.72rem; padding: 2px 8px; margin: 0;">v1.0 &bull; Janhavi92691</span>
    </div>
</div>
""", unsafe_allow_html=True)

# Render active grammar selector in sidebar
render_sidebar_grammar_selector()

# Navigation menu
PAGES = [
    "1. Home",
    "2. CFG Explorer",
    "3. Grammar Derivations",
    "4. CNF Conversion",
    "5. GNF Conversion",
    "6. CYK Membership Tester",
    "7. PDA Simulator",
    "8. Parse Tree Visualization",
    "9. PDA State Diagram",
    "10. Test Cases and Results",
    "11. About Project"
]

selected_page = st.sidebar.radio(
    "Navigation Menu:",
    options=PAGES,
    index=0
)

st.sidebar.divider()
st.sidebar.caption("Interactive CFG & PDA Learning Tool &bull; Academic Edition")

# Page Routing
if selected_page == "1. Home":
    render_home_page()
elif selected_page == "2. CFG Explorer":
    render_cfg_page()
elif selected_page == "3. Grammar Derivations":
    render_derivation_page()
elif selected_page == "4. CNF Conversion":
    render_cnf_page()
elif selected_page == "5. GNF Conversion":
    render_gnf_page()
elif selected_page == "6. CYK Membership Tester":
    render_cyk_page()
elif selected_page == "7. PDA Simulator":
    render_pda_page()
elif selected_page == "8. Parse Tree Visualization":
    render_visualization_page(mode="parse_tree")
elif selected_page == "9. PDA State Diagram":
    render_visualization_page(mode="pda_diagram")
elif selected_page == "10. Test Cases and Results":
    render_tests_page()
elif selected_page == "11. About Project":
    render_about_page()
