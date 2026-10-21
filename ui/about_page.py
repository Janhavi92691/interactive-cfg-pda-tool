"""
About Project Page: Theory, Architecture, and Academic Context.
Redesigned with formal definitions, stack overview, and attribution.
"""

import streamlit as st


def render_about_page():
    st.title("ℹ️ Academic Project Documentation")
    st.caption("Interactive CFG & PDA Learning Tool — Theory of Computation Academic Project")

    st.markdown("""
    ### 🎯 Project Motivation & Purpose
    The **Interactive CFG and PDA Learning Tool** is an educational software platform designed for computer science and engineering students studying **Theory of Computation (Automata Theory)**.
    It provides an interactive, visual, and mathematically sound workbench for analyzing Context-Free Grammars (CFGs), Pushdown Automata (PDAs), normal form conversions (CNF & GNF), dynamic programming parsing (CYK), and automata stack operations.

    ---
    """)

    col_meta1, col_meta2 = st.columns(2)
    with col_meta1:
        st.markdown("""
        <div style="background:#ffffff; border:1px solid #e2e8f0; border-radius:12px; padding:20px;">
            <h4 style="margin:0 0 10px 0; color:#0f172a;">👥 Project Information</h4>
            <p style="margin:4px 0; font-size:0.9rem;"><b>Author / Developer:</b> Janhavi (<code>Janhavi92691</code>)</p>
            <p style="margin:4px 0; font-size:0.9rem;"><b>Course:</b> Theory of Computation / Automata Theory</p>
            <p style="margin:4px 0; font-size:0.9rem;"><b>Repository:</b> <code>interactive-cfg-pda-tool</code></p>
            <p style="margin:4px 0; font-size:0.9rem;"><b>GitHub URL:</b> <a href="https://github.com/Janhavi92691/interactive-cfg-pda-tool" target="_blank">github.com/Janhavi92691/interactive-cfg-pda-tool</a></p>
        </div>
        """, unsafe_allow_html=True)

    with col_meta2:
        st.markdown("""
        <div style="background:#ffffff; border:1px solid #e2e8f0; border-radius:12px; padding:20px;">
            <h4 style="margin:0 0 10px 0; color:#0f172a;">🛠️ Technology Stack</h4>
            <p style="margin:4px 0; font-size:0.9rem;"><b>Language:</b> Python 3.10+ (pure Python algorithm engine)</p>
            <p style="margin:4px 0; font-size:0.9rem;"><b>UI Framework:</b> Streamlit with custom CSS design tokens</p>
            <p style="margin:4px 0; font-size:0.9rem;"><b>Visualization:</b> Graphviz (DOT language client-side rendering)</p>
            <p style="margin:4px 0; font-size:0.9rem;"><b>Testing:</b> Pytest (24 automated unit tests)</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Architecture Overview
    st.subheader("🏗️ System Architecture & File Structure")
    st.code("""
interactive-cfg-pda-tool/
    ├── app.py                     # Main application entry point and router
    ├── requirements.txt           # Python dependencies (Streamlit, Pytest, Graphviz, Pandas)
    ├── README.md                  # Comprehensive setup and usage instructions
    ├── algorithms/                # Algorithmic engine (independent of UI)
    │   ├── grammar.py             # CFG data structures, multi-character tokenization, catalog
    │   ├── validation.py          # CFG syntax, generating, and reachable diagnostics
    │   ├── derivations.py         # Leftmost & rightmost derivation search (BFS)
    │   ├── cnf.py                 # Genuine 6-stage Chomsky Normal Form conversion
    │   ├── gnf.py                 # Greibach Normal Form conversion pipeline
    │   ├── cyk.py                 # Cocke-Younger-Kasami dynamic programming parser
    │   ├── pda.py                 # Formal 7-tuple PDA simulator and Graphviz exporter
    │   └── parse_tree.py          # ParseTreeNode and Graphviz tree renderer
    ├── ui/                        # Streamlit visual components
    │   ├── common.py              # CSS styles, session state & shared grammar selector
    │   ├── home.py                # Landing page and operation cards
    │   ├── cfg_page.py            # CFG editor and symbol diagnostics
    │   ├── derivation_page.py     # Derivation viewer and step tracer
    │   ├── cnf_page.py            # CNF pipeline with stage breakdowns
    │   ├── gnf_page.py            # GNF pipeline with left-recursion removal
    │   ├── cyk_page.py            # CYK triangular DP matrix & cell inspector
    │   ├── pda_page.py            # PDA interactive stepper and stack visualizer
    │   ├── visualization_page.py  # Graphviz parse trees & PDA state graphs
    │   ├── tests_page.py          # Automated test execution dashboard
    │   └── about_page.py          # Project documentation and theoretical background
    ├── tests/                     # Automated pytest regression suite
    └── docs/                      # Comprehensive academic project report & flowcharts
    """, language="text")

    st.markdown("""
    ---
    ### 📚 Theoretical Reference Guide

    1. **Context-Free Grammar (CFG):**
       A formal 4-tuple $G = (V, \\Sigma, R, S)$ where:
       - $V$ is a finite set of non-terminal variables.
       - $\\Sigma$ is a finite set of terminal symbols ($V \\cap \\Sigma = \\emptyset$).
       - $R \\subseteq V \\times (V \\cup \\Sigma)^*$ is a finite set of production rules.
       - $S \\in V$ is the distinguished start symbol.

    2. **Chomsky Normal Form (CNF):**
       A context-free grammar is in CNF if all production rules have the form:
       - $A \\to BC$ ($B, C \\in V$)
       - $A \\to a$ ($a \\in \\Sigma$)
       - $S_0 \\to \\epsilon$ (permitted solely for the isolated start symbol if $\\epsilon \\in L(G)$).

    3. **Greibach Normal Form (GNF):**
       Every non-empty production begins with a terminal symbol, followed by zero or more variables:
       - $A \\to a \\alpha$ ($a \\in \\Sigma, \\alpha \\in V^*$).

    4. **CYK Parsing Algorithm:**
       A bottom-up dynamic programming parsing algorithm running in $O(n^3 \\cdot |R|)$ time for grammars in CNF. It populates a triangular matrix $T[l][i]$ computing all variables deriving substring $w[i \\dots i+l-1]$.

    5. **Pushdown Automata (PDA):**
       A formal 7-tuple $M = (Q, \\Sigma, \\Gamma, \\delta, q_0, Z_0, F)$ capable of recognizing Context-Free Languages via a Last-In, First-Out (LIFO) stack mechanism.
    """)
