"""
Greibach Normal Form (GNF) Conversion and Verification Page.
Redesigned with transformation stages and terminal-prefix validation.
"""

import streamlit as st
import pandas as pd
from algorithms.grammar import CFG
from algorithms.gnf import convert_to_gnf, is_in_gnf


def render_gnf_page():
    st.title("🔄 Greibach Normal Form (GNF) Pipeline")
    st.caption("Transform Context-Free Grammars so every production rule begins with a terminal symbol: $A \\to a \\alpha$.")

    g: CFG = st.session_state.current_grammar

    st.markdown(f"""
    <div style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:10px; padding:12px 16px; margin-bottom:14px;">
        <b>Current Grammar:</b> <code>{g.start_symbol}</code> &bull; 
        <b>Rules:</b> {len(g.productions)} &bull; 
        <b>Variables:</b> {len(g.variables)} &bull; 
        <b>Terminals:</b> {len(g.terminals)}
    </div>
    """, unsafe_allow_html=True)

    col_btn, col_scope = st.columns([1, 3])
    with col_btn:
        run_gnf = st.button("🚀 Execute GNF Transformation", type="primary", use_container_width=True)

    with col_scope:
        st.info("ℹ️ Standard GNF applies CNF preprocessing, variable ordering, forward/backward substitutions, and left-recursion elimination.")

    if run_gnf:
        with st.spinner("Processing GNF transformation..."):
            try:
                gnf_grammar, stages = convert_to_gnf(g)

                # Stage Stepper Breadcrumbs
                st.markdown("### 📍 Transformation Pipeline Stepper")
                stepper_html = []
                for i, s in enumerate(stages):
                    is_final = (i == len(stages) - 1)
                    tag_class = "badge-term" if is_final else "badge-var"
                    stepper_html.append(f"<span class='badge-tag {tag_class}'>{s.stage_name}</span>")
                st.markdown(" ➔ ".join(stepper_html), unsafe_allow_html=True)

                st.markdown("<br>", unsafe_allow_html=True)

                for idx, stage in enumerate(stages):
                    is_last = (idx == len(stages) - 1)
                    with st.expander(f"📍 {stage.stage_name} ({len(stage.grammar.productions)} rules)", expanded=is_last):
                        st.markdown(f"**Stage Description:** {stage.description}")
                        if stage.details:
                            st.caption(f"Details: {stage.details}")

                        c_text, c_table = st.columns([1, 2])
                        with c_text:
                            st.markdown("**Grammar Text:**")
                            st.code(stage.grammar.to_text(), language="text")
                        with c_table:
                            st.markdown("**Rules Breakdown:**")
                            data = []
                            for p in stage.grammar.productions:
                                lead_sym = p.clean_body[0] if p.clean_body else "ε"
                                is_term = lead_sym in stage.grammar.terminals if p.clean_body else True
                                data.append({
                                    "LHS": p.head,
                                    "Leading Symbol": lead_sym,
                                    "Is Terminal": "✓ Yes" if is_term else "✗ No",
                                    "Full RHS": " ".join(p.clean_body) if p.clean_body else "ε"
                                })
                            st.dataframe(pd.DataFrame(data), use_container_width=True, hide_index=True)

                st.divider()

                # Structural Validation
                st.subheader("Final GNF Structural Validation")
                valid_gnf, violations = is_in_gnf(gnf_grammar)

                if valid_gnf:
                    st.markdown("""
                    <div class="status-banner-accepted">
                        <b>✓ Greibach Normal Form Verified:</b> All non-empty production rules begin with a terminal symbol followed by zero or more non-terminals.
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown("""
                    <div class="status-banner-rejected">
                        <b>⚠️ GNF Scope Notice:</b> Some productions deviate from strict GNF requirements:
                    </div>
                    """, unsafe_allow_html=True)
                    for v in violations:
                        st.write(f"- {v}")

            except Exception as e:
                st.error(f"GNF Conversion Notice: {str(e)}")
                st.info("Grammar is outside current supported conversion scope or exceeded iteration bounds.")
