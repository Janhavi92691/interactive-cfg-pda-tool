"""
Grammar Derivations Page (Leftmost and Rightmost).
Redesigned with sentential step ribbons and comparative analysis.
"""

import streamlit as st
import pandas as pd
from algorithms.grammar import CFG, EPSILON
from algorithms.derivations import leftmost_derivation, rightmost_derivation


def render_derivation_page():
    st.title("🔀 Grammar Derivations Explorer")
    st.caption("Demonstrate step-by-step sentential expansions via Leftmost and Rightmost derivations.")

    g: CFG = st.session_state.current_grammar

    # Grammar Quick Overview
    st.markdown(f"""
    <div style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:10px; padding:12px 16px; margin-bottom:16px;">
        <span style="font-size:0.85rem; color:#475569;">
            <b>Active Grammar:</b> <code>{g.start_symbol}</code> &bull; 
            <b>Terminals:</b> {', '.join(f'<code>{t}</code>' for t in sorted(g.terminals))} &bull;
            <b>Variables:</b> {', '.join(f'<code>{v}</code>' for v in sorted(g.variables))}
        </span>
    </div>
    """, unsafe_allow_html=True)

    with st.expander("View Active Grammar Rules", expanded=False):
        st.code(g.to_text(), language="text")

    st.markdown("### 🎯 Target String Derivation Search")
    col_input, col_mode, col_depth = st.columns([2, 1, 1])

    with col_input:
        target_input = st.text_input(
            "Enter Target String to Derive:",
            value="aabb" if "a" in g.terminals and "b" in g.terminals else ("id + id" if "id" in g.terminals else ""),
            placeholder="e.g. aabb or ( id + id ), or leave empty for ε",
            help="For multi-character terminals like 'id', separate with spaces or use standard tokens."
        )

    with col_mode:
        deriv_mode = st.selectbox(
            "Derivation Mode:",
            options=["Leftmost Derivation", "Rightmost Derivation", "Both (Side-by-Side)"]
        )

    with col_depth:
        max_steps = st.slider("Max Search Depth:", min_value=5, max_value=25, value=15)

    if st.button("🚀 Search & Expand Derivation", type="primary"):
        tokens = g.tokenize_input(target_input)

        if tokens is None:
            st.error(f"Cannot tokenize input string '{target_input}' with the active grammar's terminal set {sorted(g.terminals)}.")
            st.info("Make sure all input symbols correspond to valid terminals defined in the grammar.")
            return

        token_display = " ".join(tokens) if tokens else EPSILON
        st.write(f"**Parsed Token Sequence:** `{token_display}` ({len(tokens)} tokens)")

        # Render Leftmost Derivation
        if deriv_mode in ["Leftmost Derivation", "Both (Side-by-Side)"]:
            st.subheader("Leftmost Derivation ($S \\Rightarrow_{lm}^* w$)")
            with st.spinner("Searching leftmost derivation path..."):
                steps_lm, msg_lm = leftmost_derivation(g, tokens, max_steps=max_steps)

            if steps_lm:
                st.markdown(f"""
                <div class="status-banner-accepted">
                    <b>✓ Leftmost Derivation Found:</b> Derived in <b>{len(steps_lm)-1}</b> steps.
                </div>
                """, unsafe_allow_html=True)

                # Sentential Ribbon
                ribbon_items = []
                for s in steps_lm:
                    form_txt = s.form_string()
                    ribbon_items.append(f"<span class='badge-tag badge-var'>{form_txt}</span>")
                st.markdown(f"**Sentential Expansion Chain:** {' ➔ '.join(ribbon_items)}", unsafe_allow_html=True)

                # Step details table
                table_data = [s.to_dict() for s in steps_lm]
                st.dataframe(pd.DataFrame(table_data), use_container_width=True, hide_index=True)
            else:
                st.markdown(f"""
                <div class="status-banner-rejected">
                    <b>✗ Derivation Unsuccessful:</b> {msg_lm}
                </div>
                """, unsafe_allow_html=True)

        # Render Rightmost Derivation
        if deriv_mode in ["Rightmost Derivation", "Both (Side-by-Side)"]:
            st.subheader("Rightmost Derivation ($S \\Rightarrow_{rm}^* w$)")
            with st.spinner("Searching rightmost derivation path..."):
                steps_rm, msg_rm = rightmost_derivation(g, tokens, max_steps=max_steps)

            if steps_rm:
                st.markdown(f"""
                <div class="status-banner-accepted">
                    <b>✓ Rightmost Derivation Found:</b> Derived in <b>{len(steps_rm)-1}</b> steps.
                </div>
                """, unsafe_allow_html=True)

                ribbon_items = []
                for s in steps_rm:
                    form_txt = s.form_string()
                    ribbon_items.append(f"<span class='badge-tag badge-term'>{form_txt}</span>")
                st.markdown(f"**Sentential Expansion Chain:** {' ➔ '.join(ribbon_items)}", unsafe_allow_html=True)

                table_data = [s.to_dict() for s in steps_rm]
                st.dataframe(pd.DataFrame(table_data), use_container_width=True, hide_index=True)
            else:
                st.markdown(f"""
                <div class="status-banner-rejected">
                    <b>✗ Derivation Unsuccessful:</b> {msg_rm}
                </div>
                """, unsafe_allow_html=True)
