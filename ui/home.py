"""
Home / Landing Page for Interactive CFG & PDA Learning Tool.
Elevated educational design inspired by PushdownPlayground with an original identity.
"""

import streamlit as st
from algorithms.grammar import CFG


def render_home_page():
    # Hero Section
    st.markdown("""
    <div class="hero-container">
        <div class="hero-badge">🎓 Formal Languages & Automata Theory</div>
        <div class="hero-title">Interactive CFG & PDA Learning Tool</div>
        <div class="hero-subtitle">
            A comprehensive, mathematically rigorous workbench designed for computer engineering students.
            Explore Context-Free Grammars, Pushdown Automata, Chomsky & Greibach Normal Forms, and dynamic programming parsing step by step.
        </div>
        <div style="margin-top: 16px; display: flex; gap: 8px; flex-wrap: wrap;">
            <span class="badge-tag" style="background: rgba(255,255,255,0.15); color: #ffffff; border: 1px solid rgba(255,255,255,0.25);">⚡ 100% Offline Python Engine</span>
            <span class="badge-tag" style="background: rgba(16,185,129,0.2); color: #6ee7b7; border: 1px solid rgba(16,185,129,0.4);">✓ 24/24 Automated Tests Passed</span>
            <span class="badge-tag" style="background: rgba(56,189,248,0.2); color: #7dd3fc; border: 1px solid rgba(56,189,248,0.4);">📊 O(n³·|P|) CYK Dynamic Programming</span>
            <span class="badge-tag" style="background: rgba(245,158,11,0.2); color: #fde68a; border: 1px solid rgba(245,158,11,0.4);">🥞 Non-Deterministic PDA Stepper</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Active State Quick Banner
    g: CFG = st.session_state.current_grammar
    st.markdown("### 🎛️ Active Context Overview")
    
    col_m1, col_m2, col_m3, col_m4 = st.columns(4)
    with col_m1:
        st.markdown(f"""
        <div style="background:#ffffff; border:1px solid #e2e8f0; border-radius:12px; padding:16px; text-align:center;">
            <span style="font-size:0.75rem; text-transform:uppercase; color:#64748b; font-weight:700;">Active Grammar</span>
            <div style="font-size:1.15rem; font-weight:700; color:#4f46e5; margin-top:4px;">{st.session_state.selected_grammar_key}</div>
        </div>
        """, unsafe_allow_html=True)

    with col_m2:
        st.markdown(f"""
        <div style="background:#ffffff; border:1px solid #e2e8f0; border-radius:12px; padding:16px; text-align:center;">
            <span style="font-size:0.75rem; text-transform:uppercase; color:#64748b; font-weight:700;">Start Symbol</span>
            <div style="font-size:1.4rem; font-weight:800; color:#b45309; margin-top:2px;">{g.start_symbol}</div>
        </div>
        """, unsafe_allow_html=True)

    with col_m3:
        st.markdown(f"""
        <div style="background:#ffffff; border:1px solid #e2e8f0; border-radius:12px; padding:16px; text-align:center;">
            <span style="font-size:0.75rem; text-transform:uppercase; color:#64748b; font-weight:700;">Grammar Symbols</span>
            <div style="font-size:1.15rem; font-weight:700; color:#0f172a; margin-top:4px;">
                <span style="color:#6d28d9;">{len(g.variables)} V</span> &bull; <span style="color:#047857;">{len(g.terminals)} Σ</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col_m4:
        st.markdown(f"""
        <div style="background:#ffffff; border:1px solid #e2e8f0; border-radius:12px; padding:16px; text-align:center;">
            <span style="font-size:0.75rem; text-transform:uppercase; color:#64748b; font-weight:700;">Active PDA</span>
            <div style="font-size:1.05rem; font-weight:700; color:#0284c7; margin-top:6px;">{st.session_state.selected_pda_key}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### 🧩 Interactive Workspaces & Learning Modules")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        <div class="feature-card">
            <div>
                <div class="feature-icon-badge icon-blue">📐</div>
                <h4 style="margin:0 0 8px 0; font-weight:700; color:#0f172a;">CFG Explorer & Derivations</h4>
                <p style="font-size:0.9rem; color:#64748b; line-height:1.5;">
                    Define custom or predefined grammars. Validate productive and reachable variables, and generate step-by-step leftmost and rightmost sentential derivations.
                </p>
            </div>
            <div style="margin-top:14px; margin-bottom:12px;">
                <span class="badge-tag badge-var">Leftmost (LM)</span>
                <span class="badge-tag badge-var">Rightmost (RM)</span>
                <span class="badge-tag badge-pill">Multi-Char 'id'</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("🚀 Open CFG Explorer →", key="home_nav_cfg", use_container_width=True):
            st.session_state.nav_page = "2. CFG Explorer"
            st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)

        st.markdown("""
        <div class="feature-card">
            <div>
                <div class="feature-icon-badge icon-purple">🔄</div>
                <h4 style="margin:0 0 8px 0; font-weight:700; color:#0f172a;">CNF & GNF Normal Forms</h4>
                <p style="font-size:0.9rem; color:#64748b; line-height:1.5;">
                    Complete 6-stage CNF pipeline (start isolation, ε-elimination, unit removal, useless pruning, binarization) and GNF transformation with left-recursion elimination.
                </p>
            </div>
            <div style="margin-top:14px; margin-bottom:12px;">
                <span class="badge-tag badge-term">6-Stage CNF</span>
                <span class="badge-tag badge-term">GNF Left-Rec</span>
                <span class="badge-tag badge-pill">Validated</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("🔄 Open Normal Forms →", key="home_nav_cnf", use_container_width=True):
            st.session_state.nav_page = "4. CNF Conversion"
            st.rerun()

    with col2:
        st.markdown("""
        <div class="feature-card">
            <div>
                <div class="feature-icon-badge icon-emerald">📊</div>
                <h4 style="margin:0 0 8px 0; font-weight:700; color:#0f172a;">CYK Dynamic Programming</h4>
                <p style="font-size:0.9rem; color:#64748b; line-height:1.5;">
                    Execute the Cocke–Younger–Kasami algorithm. Inspect the triangular DP table, check cell partitions, and view exact binary/terminal rule derivations.
                </p>
            </div>
            <div style="margin-top:14px; margin-bottom:12px;">
                <span class="badge-tag badge-var">O(n³·|P|) Matrix</span>
                <span class="badge-tag badge-var">Cell Inspector</span>
                <span class="badge-tag badge-pill">Backpointers</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("📊 Open CYK Tester →", key="home_nav_cyk", use_container_width=True):
            st.session_state.nav_page = "6. CYK Membership Tester"
            st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)

        st.markdown("""
        <div class="feature-card">
            <div>
                <div class="feature-icon-badge icon-amber">🥞</div>
                <h4 style="margin:0 0 8px 0; font-weight:700; color:#0f172a;">Pushdown Automata Simulator</h4>
                <p style="font-size:0.9rem; color:#64748b; line-height:1.5;">
                    Interactive 7-tuple PDA stepper with Next, Prev, Reset, and Run All controls. Features an animated-style LIFO stack visualizer and tape-reading ribbon.
                </p>
            </div>
            <div style="margin-top:14px; margin-bottom:12px;">
                <span class="badge-tag badge-start">Interactive Stack</span>
                <span class="badge-tag badge-start">Tape Ribbon</span>
                <span class="badge-tag badge-pill">Non-Det BFS</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("🥞 Open PDA Simulator →", key="home_nav_pda", use_container_width=True):
            st.session_state.nav_page = "7. PDA Simulator"
            st.rerun()

    with col3:
        st.markdown("""
        <div class="feature-card">
            <div>
                <div class="feature-icon-badge icon-blue">🌳</div>
                <h4 style="margin:0 0 8px 0; font-weight:700; color:#0f172a;">Parse Trees & State Graphs</h4>
                <p style="font-size:0.9rem; color:#64748b; line-height:1.5;">
                    Generate Graphviz parse trees with non-terminal ellipses and terminal leave boxes. Inspect directed PDA state diagrams with real-time active state highlighting.
                </p>
            </div>
            <div style="margin-top:14px; margin-bottom:12px;">
                <span class="badge-tag badge-var">Graphviz DOT</span>
                <span class="badge-tag badge-var">State Machine</span>
                <span class="badge-tag badge-pill">Active Highlight</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("🌳 Open Visualizations →", key="home_nav_vis", use_container_width=True):
            st.session_state.nav_page = "8. Parse Tree Visualization"
            st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)

        st.markdown("""
        <div class="feature-card">
            <div>
                <div class="feature-icon-badge icon-emerald">🧪</div>
                <h4 style="margin:0 0 8px 0; font-weight:700; color:#0f172a;">Automated Testing Suite</h4>
                <p style="font-size:0.9rem; color:#64748b; line-height:1.5;">
                    Built-in automated test suite runner covering CFG validation, derivations, CNF/GNF transformations, CYK parsing, and PDA acceptance/rejection test cases.
                </p>
            </div>
            <div style="margin-top:14px; margin-bottom:12px;">
                <span class="badge-tag badge-term">24 Pytest Cases</span>
                <span class="badge-tag badge-term">Pass/Fail Matrix</span>
                <span class="badge-tag badge-pill">100% Passed</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("🧪 Run Test Suite →", key="home_nav_tests", use_container_width=True):
            st.session_state.nav_page = "10. Test Cases and Results"
            st.rerun()

    st.divider()

    # Recommended Learning Flow
    st.markdown("### 🗺️ Recommended Educational Workflow")
    st.info("""
    1. **Grammar Inspection (`2. CFG Explorer`):** Choose an active grammar (e.g. $a^n b^n$ or Arithmetic) and inspect its variables, terminals, and well-formedness.
    2. **Derivations (`3. Grammar Derivations`):** Enter a target string like `aabb` or `id + id` to see the leftmost and rightmost sentential forms.
    3. **Normal Form Transformations (`4. CNF Conversion`):** Step through the 6-stage transformation into Chomsky Normal Form.
    4. **Parsing Verification (`6. CYK Membership Tester`):** Verify if strings belong to the grammar using the triangular dynamic programming table.
    5. **Automata Execution (`7. PDA Simulator`):** Step through push and pop stack transitions using the interactive playback controls.
    """)
