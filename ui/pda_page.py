"""
Pushdown Automaton (PDA) Interactive Simulator and Diagnostics Page.
Redesigned with a visual tape reader ribbon, vertical stack viewer, and step controls.
"""

import streamlit as st
import pandas as pd
from algorithms.grammar import EPSILON
from algorithms.pda import PDA, PDASimulator, get_predefined_pdas


def render_pda_page():
    st.title("🥞 Pushdown Automaton (PDA) Simulator")
    st.caption("Interactive execution engine for Pushdown Automata with animated stack, tape ribbon, and state machine visualization.")

    pdas_catalog = st.session_state.predefined_pdas

    # Model Selector Card
    c_sel, c_acc = st.columns([2, 1])
    with c_sel:
        selected_pda_name = st.selectbox(
            "Select Pushdown Automaton Model:",
            options=list(pdas_catalog.keys()),
            index=list(pdas_catalog.keys()).index(st.session_state.selected_pda_key)
            if st.session_state.selected_pda_key in pdas_catalog else 0
        )
        if selected_pda_name != st.session_state.selected_pda_key:
            st.session_state.selected_pda_key = selected_pda_name
            st.session_state.current_pda = pdas_catalog[selected_pda_name]
            if "pda_simulator" in st.session_state:
                del st.session_state["pda_simulator"]
            st.rerun()

    active_pda: PDA = st.session_state.current_pda

    with c_acc:
        st.markdown(f"""
        <div style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:10px; padding:10px 14px;">
            <div style="font-size:0.8rem; color:#64748b;">
                Acceptance: <span class="badge-tag badge-start" style="margin:0;">{active_pda.acceptance_mode}</span>
            </div>
            <div style="font-size:0.8rem; color:#64748b; margin-top:4px;">
                Start: <code>{active_pda.start_state}</code> | Stack Z₀: <code>{active_pda.initial_stack_symbol}</code>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with st.expander("📖 Formal 7-Tuple Definition $M = (Q, \\Sigma, \\Gamma, \\delta, q_0, Z_0, F)$", expanded=False):
        st.write(f"**Model Description:** {active_pda.description}")
        t1, t2, t3 = st.columns(3)
        with t1:
            st.write(f"**States ($Q$):** {', '.join(sorted(active_pda.states))}")
            st.write(rf"**Input Alphabet ($\Sigma$):** {', '.join(sorted(active_pda.input_alphabet))}")
        with t2:
            st.write(rf"**Stack Alphabet ($\Gamma$):** {', '.join(sorted(active_pda.stack_alphabet))}")
            st.write(f"**Accepting States ($F$):** {', '.join(sorted(active_pda.accepting_states))}")
        with t3:
            st.write(f"**Start State ($q_0$):** `{active_pda.start_state}`")
            st.write(f"**Initial Stack ($Z_0$):** `{active_pda.initial_stack_symbol}`")

        st.markdown(r"**Transition Function ($\delta$):**")
        trans_rows = []
        for t in active_pda.transitions:
            trans_rows.append({
                "Current State": t.from_state,
                "Input Symbol": t.input_symbol,
                "Pop Stack Top": t.pop_symbol,
                "Next State": t.to_state,
                "Push String": t.push_str,
                "Formal Notation": t.label()
            })
        st.dataframe(pd.DataFrame(trans_rows), use_container_width=True, hide_index=True)

    st.divider()

    # Simulation Controls
    st.subheader("Interactive Stepper Controller")
    default_input = "aabb" if "a" in active_pda.input_alphabet else ("(())" if "(" in active_pda.input_alphabet else "")

    pda_input_str = st.text_input(
        "Input String to Simulate:",
        value=default_input,
        placeholder="e.g. aabb or leave empty for ε"
    )

    sim_key = f"sim_{active_pda.name}_{pda_input_str}"
    if "pda_simulator_key" not in st.session_state or st.session_state.pda_simulator_key != sim_key:
        st.session_state.pda_simulator = PDASimulator(active_pda, pda_input_str)
        st.session_state.pda_simulator_key = sim_key

    sim: PDASimulator = st.session_state.pda_simulator

    # Stepper Control Row
    b1, b2, b3, b4, b_info = st.columns([1, 1, 1, 1, 3])
    with b1:
        if st.button("⏮️ Reset", use_container_width=True):
            sim.reset()
            st.rerun()
    with b2:
        if st.button("◀️ Previous", use_container_width=True, disabled=(sim.current_step_index == 0)):
            sim.step_backward()
            st.rerun()
    with b3:
        if st.button("▶️ Next", use_container_width=True, disabled=(sim.current_step_index >= sim.total_steps - 1)):
            sim.step_forward()
            st.rerun()
    with b4:
        if st.button("⏭️ Run All", use_container_width=True):
            sim.run_all()
            st.rerun()
    with b_info:
        verdict_badge = "<span class='badge-tag badge-term'>✓ ACCEPTED</span>" if sim.is_accepted else "<span class='badge-tag badge-eps'>✗ REJECTED</span>"
        st.markdown(f"**Step {sim.current_step_index} of {sim.total_steps - 1}** &bull; Overall Result: {verdict_badge}", unsafe_allow_html=True)

    curr_step = sim.current_step

    # Visual Tape Reader Ribbon
    if pda_input_str:
        tokens = list(pda_input_str.strip())
        consumed_count = len(tokens) - len(curr_step.remaining_input) if curr_step else 0

        tape_html = ["<div class='tape-container'><span style='font-size:0.75rem; text-transform:uppercase; color:#94a3b8; font-weight:700;'>Input Tape Reader Ribbon</span><div class='tape-cells'>"]
        for idx, tok in enumerate(tokens):
            if idx < consumed_count - 1:
                cls = "tape-cell tape-cell-consumed"
                lbl = ""
            elif idx == consumed_count - 1 and consumed_count > 0:
                cls = "tape-cell tape-cell-current"
                lbl = "<span class='tape-pointer'>▲ Read</span>"
            elif idx == consumed_count:
                cls = "tape-cell tape-cell-current"
                lbl = "<span class='tape-pointer'>▲ Head</span>"
            else:
                cls = "tape-cell tape-cell-unread"
                lbl = ""
            tape_html.append(f"<div class='{cls}'><span>{tok}</span>{lbl}</div>")
        tape_html.append("</div></div>")
        st.markdown("".join(tape_html), unsafe_allow_html=True)

    # Current Configuration & Stack Display
    if curr_step:
        col_state, col_stack = st.columns([1, 1])
        with col_state:
            st.markdown(f"""
            <div style="background:#ffffff; border:1px solid #e2e8f0; border-radius:12px; padding:20px; box-shadow:0 2px 4px rgba(0,0,0,0.04);">
                <h4 style="margin:0 0 12px 0; color:#0f172a; font-weight:700;">📍 Current Machine State</h4>
                <div style="display:flex; gap:12px; align-items:center; margin-bottom:10px;">
                    <span style="font-size:0.85rem; color:#64748b;">Active State:</span>
                    <span class="badge-tag badge-var" style="font-size:1.1rem; padding:6px 14px; margin:0;">{curr_step.state}</span>
                </div>
                <div style="font-size:0.9rem; color:#475569; margin-bottom:6px;">
                    <b>Remaining Input:</b> <code>{curr_step.input_str()}</code>
                </div>
                <div style="font-size:0.9rem; color:#475569;">
                    <b>Transition Action:</b> {curr_step.explanation}
                </div>
            </div>
            """, unsafe_allow_html=True)

        with col_stack:
            stack_elements = curr_step.stack_after
            stack_items_html = []
            if not stack_elements:
                stack_items_html.append("<div style='color:#ef4444; font-size:0.9rem; text-align:center; padding:8px;'>[STACK IS EMPTY]</div>")
            else:
                for i, sym in enumerate(stack_elements):
                    if i == 0:
                        stack_items_html.append(f"<div class='stack-item stack-item-top'>🔝 TOP: {sym}</div>")
                    else:
                        stack_items_html.append(f"<div class='stack-item'>{sym}</div>")

            st.markdown(f"""
            <div class="stack-viewer-card">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <h4 style="margin:0; color:#0f172a; font-weight:700;">🥞 LIFO Stack Column</h4>
                    <span class="badge-tag badge-pill" style="margin:0;">Depth: {len(stack_elements)}</span>
                </div>
                <div class="stack-column">
                    {''.join(stack_items_html)}
                </div>
            </div>
            """, unsafe_allow_html=True)

    # State Diagram with active state highlighted
    st.subheader("Directed State-Transition Graph (Active State Highlighted)")
    highlight_st = curr_step.state if curr_step else None
    dot_source = active_pda.to_dot(current_highlight_state=highlight_st)
    st.graphviz_chart(dot_source)

    # Complete Step Trace Table
    st.subheader("Step-by-Step Execution Trace")
    trace_data = []
    for s in sim.steps:
        trans_text = s.transition_applied.label() if s.transition_applied else "Initial State"
        trace_data.append({
            "Step": s.step_number,
            "State": s.state,
            "Remaining Input": s.input_str(),
            "Stack Before": s.stack_before_str(),
            "Transition": trans_text,
            "Stack After": s.stack_after_str(),
            "Explanation": s.explanation
        })
    st.dataframe(pd.DataFrame(trace_data), use_container_width=True, hide_index=True)

    # Predefined Acceptance & Rejection Suite
    st.divider()
    st.subheader("🧪 Standard Language Test Cases Matrix")
    if active_pda.name == "PDA for L = { a^n b^n | n ≥ 0 }":
        t_acc, t_rej = st.columns(2)
        with t_acc:
            st.markdown("**Accepted Strings ($a^n b^n$):**")
            acc_list = ["", "ab", "aabb", "aaabbb"]
            acc_results = []
            for item in acc_list:
                toks = list(item)
                res, _, exp = active_pda.simulate(toks)
                acc_results.append({
                    "Input String": repr(item) if item else "ε (empty)",
                    "Expected": "Accepted",
                    "Actual": "Accepted" if res else "Rejected",
                    "Status": "✅ PASS" if res else "❌ FAIL"
                })
            st.dataframe(pd.DataFrame(acc_results), use_container_width=True, hide_index=True)

        with t_rej:
            st.markdown("**Rejected Strings ($a^n b^n$):**")
            rej_list = ["a", "b", "aab", "abb", "abab", "aaabb"]
            rej_results = []
            for item in rej_list:
                toks = list(item)
                res, _, exp = active_pda.simulate(toks)
                rej_results.append({
                    "Input String": repr(item),
                    "Expected": "Rejected",
                    "Actual": "Accepted" if res else "Rejected",
                    "Status": "✅ PASS" if not res else "❌ FAIL"
                })
            st.dataframe(pd.DataFrame(rej_results), use_container_width=True, hide_index=True)
