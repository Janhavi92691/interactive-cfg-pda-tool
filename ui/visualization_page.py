"""
Parse Tree and PDA State Diagram Visualizations Page.
Redesigned with node legends, tree geometry, and state highlights.
"""

import streamlit as st
from algorithms.grammar import CFG, EPSILON
from algorithms.derivations import leftmost_derivation
from algorithms.parse_tree import derivation_to_tree, cyk_to_tree
from algorithms.cyk import cyk_parse
from algorithms.cnf import is_in_cnf, convert_to_cnf
from algorithms.pda import PDA


def render_visualization_page(mode: str = "parse_tree"):
    """
    mode: 'parse_tree' or 'pda_diagram'
    """
    if mode == "parse_tree":
        st.title("🌳 Graphical Parse Tree Visualization")
        st.caption("Generate hierarchical derivation parse trees for Context-Free Grammars.")

        g: CFG = st.session_state.current_grammar

        # Symbol Set Banner
        st.markdown(f"""
        <div style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:10px; padding:12px 16px; margin-bottom:16px;">
            <b>Root Variable:</b> <code>{g.start_symbol}</code> &bull; 
            <b>Variables:</b> {', '.join(f'<code>{v}</code>' for v in sorted(g.variables))} &bull;
            <b>Terminals:</b> {', '.join(f'<code>{t}</code>' for t in sorted(g.terminals))}
        </div>
        """, unsafe_allow_html=True)

        c_str, c_action = st.columns([3, 1])
        with c_str:
            target_str = st.text_input(
                "Enter String to Construct Parse Tree:",
                value="aabb" if "a" in g.terminals and "b" in g.terminals else ("id + id" if "id" in g.terminals else "")
            )
        with c_action:
            st.write("")
            st.write("")
            build_btn = st.button("🌲 Build Parse Tree", type="primary", use_container_width=True)

        # Legend card
        st.markdown("""
        <div style="display:flex; gap:16px; align-items:center; margin-bottom:12px; font-size:0.85rem; color:#64748b;">
            <span><b>Legend:</b></span>
            <span><span class="badge-tag badge-var" style="margin:0;">Non-Terminal (Blue Ellipse)</span> Internal Node</span>
            <span><span class="badge-tag badge-term" style="margin:0;">Terminal Leaf (Green Box)</span> Yield Token</span>
        </div>
        """, unsafe_allow_html=True)

        if build_btn or target_str is not None:
            tokens = g.tokenize_input(target_str)
            if tokens is None:
                st.error(f"Cannot tokenize input '{target_str}' with terminal set {sorted(g.terminals)}.")
                return

            steps, msg = leftmost_derivation(g, tokens, max_steps=18)
            tree_root = None

            if steps:
                tree_root = derivation_to_tree(g, steps)
                st.markdown("""
                <div class="status-banner-accepted">
                    <b>✓ Parse Tree Constructed:</b> Generated from a valid leftmost derivation sequence.
                </div>
                """, unsafe_allow_html=True)
                st.caption("ℹ️ *Ambiguity Note:* For ambiguous grammars, this visualizes one canonical leftmost derivation parse tree.")
            else:
                valid_cnf, _ = is_in_cnf(g)
                if valid_cnf:
                    cyk_res = cyk_parse(g, tokens)
                    if cyk_res.is_accepted:
                        tree_root = cyk_to_tree(g, cyk_res)
                        st.markdown("""
                        <div class="status-banner-accepted">
                            <b>✓ Parse Tree Constructed:</b> Reconstructed from CYK dynamic programming backpointers.
                        </div>
                        """, unsafe_allow_html=True)

            if tree_root:
                dot_tree = tree_root.to_dot()
                st.graphviz_chart(dot_tree)

                with st.expander("View Graphviz DOT Source Code", expanded=False):
                    st.code(dot_tree, language="dot")
            else:
                st.markdown(f"""
                <div class="status-banner-rejected">
                    <b>✗ Parse Tree Not Found:</b> {msg}
                </div>
                """, unsafe_allow_html=True)

    elif mode == "pda_diagram":
        st.title("🎯 Pushdown Automata State Transition Diagram")
        st.caption("Directed graph representation of PDA states, transitions, stack manipulations, and acceptance conditions.")

        active_pda: PDA = st.session_state.current_pda

        col_pda, col_state = st.columns([2, 1])
        with col_pda:
            st.markdown(f"""
            <div style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:10px; padding:12px 16px;">
                <b>Automaton:</b> {active_pda.name}<br>
                <b>Acceptance Mode:</b> <span class="badge-tag badge-start" style="margin:0;">{active_pda.acceptance_mode}</span> &bull;
                <b>Accepting States (F):</b> {', '.join(sorted(active_pda.accepting_states))}
            </div>
            """, unsafe_allow_html=True)

        with col_state:
            highlight_options = ["None"] + sorted(active_pda.states)
            selected_highlight = st.selectbox(
                "Highlight Active State:",
                options=highlight_options,
                index=0
            )

        # Transition format legend
        st.markdown("""
        <div style="display:flex; gap:16px; align-items:center; margin:12px 0; font-size:0.85rem; color:#64748b;">
            <span><b>Transition Edge Format:</b> <code>input_symbol, pop_top → push_symbols</code></span>
            <span>Double Circles = <b>Accepting States</b></span>
        </div>
        """, unsafe_allow_html=True)

        dot_pda = active_pda.to_dot(
            current_highlight_state=None if selected_highlight == "None" else selected_highlight
        )
        st.graphviz_chart(dot_pda)

        with st.expander("View Graphviz DOT Source", expanded=False):
            st.code(dot_pda, language="dot")
