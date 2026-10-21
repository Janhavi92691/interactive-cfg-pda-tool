"""
Chomsky Normal Form (CNF) Conversion and Verification Page.
Redesigned with a stage progression stepper, stage diff cards, and independent validation.
"""

import streamlit as st
import pandas as pd
from algorithms.grammar import CFG
from algorithms.cnf import convert_to_cnf, is_in_cnf


def render_cnf_page():
    st.title("🧩 Chomsky Normal Form (CNF) Pipeline")
    st.caption("Step-by-step transformation of Context-Free Grammars into Chomsky Normal Form.")

    g: CFG = st.session_state.current_grammar

    col_orig, col_ctrl = st.columns([2, 1])
    with col_orig:
        st.markdown(f"""
        <div style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:10px; padding:12px 16px;">
            <b>Input Grammar:</b> <code>{g.start_symbol}</code> &bull; 
            <b>Rules Count:</b> {len(g.productions)} &bull; 
            <b>Variables:</b> {len(g.variables)} &bull; 
            <b>Terminals:</b> {len(g.terminals)}
        </div>
        """, unsafe_allow_html=True)

    with col_ctrl:
        set_active = st.button(
            "📥 Activate Converted CNF Grammar",
            type="primary",
            use_container_width=True,
            help="Set the resulting CNF grammar as active for CYK testing."
        )

    with st.spinner("Executing 6-stage CNF transformation pipeline..."):
        cnf_grammar, stages = convert_to_cnf(g)

    if set_active:
        st.session_state.current_grammar = cnf_grammar
        st.session_state.selected_grammar_key = f"CNF ({g.start_symbol})"
        st.session_state.predefined_grammars[st.session_state.selected_grammar_key] = {
            "name": f"CNF Form of {g.start_symbol}",
            "description": "Converted Chomsky Normal Form grammar.",
            "text": cnf_grammar.to_text(),
            "start_symbol": cnf_grammar.start_symbol,
            "terminals": cnf_grammar.terminals,
            "example_strings": [],
            "rejected_strings": []
        }
        st.success("✅ Converted CNF grammar is now set as the active grammar across all pages!")
        st.rerun()

    # Stage Stepper Breadcrumbs
    st.markdown("### 📍 Transformation Pipeline Stepper")
    stepper_html = []
    for i, s in enumerate(stages):
        is_final = (i == len(stages) - 1)
        tag_class = "badge-term" if is_final else "badge-var"
        stepper_html.append(f"<span class='badge-tag {tag_class}'>Stage {i}: {s.stage_name.split(':')[1].strip() if ':' in s.stage_name else s.stage_name}</span>")
    st.markdown(" ➔ ".join(stepper_html), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Stages Accordion with Details
    for idx, stage in enumerate(stages):
        is_last = (idx == len(stages) - 1)
        with st.expander(f"📍 {stage.stage_name} ({len(stage.grammar.productions)} rules)", expanded=is_last):
            st.markdown(f"**Stage Description:** {stage.description}")
            if stage.details:
                st.caption(f"Transformation Parameters: {stage.details}")

            c_code, c_tbl = st.columns([1, 2])
            with c_code:
                st.markdown("**Grammar Text:**")
                st.code(stage.grammar.to_text(), language="text")
            with c_tbl:
                st.markdown("**Rules Breakdown:**")
                rules_list = []
                for p in stage.grammar.productions:
                    rules_list.append({
                        "LHS": p.head,
                        "RHS": " ".join(p.clean_body) if p.clean_body else "ε",
                        "RHS Symbols": len(p.clean_body)
                    })
                st.dataframe(pd.DataFrame(rules_list), use_container_width=True, hide_index=True)

    st.divider()

    # Final CNF Validation Badge & Metric
    st.subheader("Final CNF Structural Verification")
    is_valid_cnf, violations = is_in_cnf(cnf_grammar)

    if is_valid_cnf:
        st.markdown("""
        <div class="status-banner-accepted">
            <b>✓ Strict Chomsky Normal Form Verified:</b> All production rules strictly satisfy <code>A → B C</code> or <code>A → a</code> (with <code>S₀ → ε</code> allowed if empty string is in the language).
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="status-banner-rejected">
            <b>✗ CNF Structural Violations Detected:</b>
        </div>
        """, unsafe_allow_html=True)
        for v in violations:
            st.write(f"- {v}")

    c_f1, c_f2, c_f3 = st.columns(3)
    with c_f1:
        st.metric("Final CNF Variables", len(cnf_grammar.variables))
    with c_f2:
        st.metric("Final CNF Terminals", len(cnf_grammar.terminals))
    with c_f3:
        st.metric("Total CNF Rules", len(cnf_grammar.productions))
