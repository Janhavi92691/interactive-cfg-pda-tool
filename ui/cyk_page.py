"""
CYK Membership Tester and Dynamic Programming Matrix Page.
Redesigned with triangular table styling, cell inspection, and acceptance diagnostics.
"""

import streamlit as st
import pandas as pd
from algorithms.grammar import CFG, EPSILON
from algorithms.cnf import is_in_cnf, convert_to_cnf
from algorithms.cyk import cyk_parse, CYKResult
from algorithms.parse_tree import cyk_to_tree


def render_cyk_page():
    st.title("📊 CYK Dynamic Programming Parser")
    st.caption("Cocke–Younger–Kasami (CYK) $O(n^3 \\cdot |P|)$ matrix membership algorithm for grammars in Chomsky Normal Form.")

    g: CFG = st.session_state.current_grammar
    valid_cnf, violations = is_in_cnf(g)

    # Determine parse grammar: CYK requires Chomsky Normal Form (CNF)
    if not valid_cnf:
        parse_grammar, cnf_steps = convert_to_cnf(g)
        st.info(
            f"💡 **Chomsky Normal Form (CNF) Auto-Preparation Active:** "
            f"The CYK algorithm mathematically requires rules in CNF ($A \\rightarrow BC$ or $A \\rightarrow a$). "
            f"Your active grammar `{g.start_symbol} -> ...` was automatically converted into equivalent CNF "
            f"(Start symbol: `{parse_grammar.start_symbol}`) to parse string membership and construct parse trees accurately."
        )
        with st.expander("🔍 Inspect Internal CNF Grammar Rules", expanded=False):
            st.markdown(f"**CNF Start Symbol:** `{parse_grammar.start_symbol}`")
            for p in parse_grammar.productions:
                st.markdown(f"- `{p}`")
            if st.button("💾 Set this CNF Grammar as Active in Session"):
                st.session_state.current_grammar = parse_grammar
                st.session_state.selected_grammar_key = f"CNF ({g.start_symbol})"
                st.success("Set as active grammar!")
                st.rerun()
    else:
        parse_grammar = g
        st.success(f"✓ **Active Grammar is in valid Chomsky Normal Form (CNF)** (Start Symbol: `{g.start_symbol}`).")

    st.markdown("### 🔤 String Membership Testing")
    col_input, col_btn = st.columns([3, 1])

    with col_input:
        target_str = st.text_input(
            "Target Input String:",
            value="aabb" if "a" in g.terminals and "b" in g.terminals else ("id + id" if "id" in g.terminals else ""),
            placeholder="e.g. aabb or leave empty for ε"
        )

    with col_btn:
        st.write("")
        st.write("")
        run_cyk = st.button("🚀 Run CYK Parse", type="primary", use_container_width=True)

    if run_cyk or target_str is not None:
        tokens = g.tokenize_input(target_str)
        if tokens is None:
            tokens = parse_grammar.tokenize_input(target_str)
        if tokens is None:
            st.error(f"Cannot tokenize input '{target_str}' with grammar terminals {sorted(g.terminals)}.")
            return

        with st.spinner("Populating CYK dynamic programming matrix..."):
            result: CYKResult = cyk_parse(parse_grammar, tokens)

        # Result Banner
        if result.is_accepted:
            st.markdown(f"""
            <div class="status-banner-accepted">
                <h3 style="margin:0 0 4px 0; color:#065f46;">🎉 String ACCEPTED</h3>
                <p style="margin:0; font-size:0.95rem;">{result.explanation}</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="status-banner-rejected">
                <h3 style="margin:0 0 4px 0; color:#991b1b;">❌ String REJECTED</h3>
                <p style="margin:0; font-size:0.95rem;">{result.explanation}</p>
            </div>
            """, unsafe_allow_html=True)

        # If non-empty, render Triangular DP Table
        if tokens:
            st.subheader("Triangular Dynamic Programming Matrix $T[l][i]$")
            st.caption("Rows represent substring lengths $l = n \\dots 1$. Columns represent starting index $i$. The root cell $T[n][1]$ determines acceptance.")

            n = len(tokens)
            matrix_data = []
            for l in range(n, 0, -1):
                row_dict = {"Length (l)": f"l = {l}"}
                for i in range(n):
                    if i + l <= n:
                        cell = result.get_cell(l, i)
                        vars_str = "{" + ", ".join(sorted(cell.variables)) + "}" if cell.variables else "∅"
                        if l == n and i == 0:
                            vars_str = f"⭐ {vars_str}"
                        row_dict[f"w[{i+1}]: '{tokens[i]}'"] = vars_str
                    else:
                        row_dict[f"w[{i+1}]: '{tokens[i]}'"] = ""
                matrix_data.append(row_dict)

            st.dataframe(pd.DataFrame(matrix_data), use_container_width=True, hide_index=True)

            # Interactive Cell Inspector
            st.subheader("🔍 Cell Derivation Inspector")
            st.caption("Select any cell to inspect which production rules and split partitions formed its variable set.")

            c1, c2 = st.columns(2)
            with c1:
                sel_length = st.selectbox(
                    "Select Substring Length (l):",
                    options=list(range(1, n + 1)),
                    index=n - 1
                )
            with c2:
                max_start = n - sel_length
                sel_start = st.selectbox(
                    "Select Start Index (i):",
                    options=list(range(max_start + 1)),
                    format_func=lambda idx: f"Index {idx+1} (substring: '{''.join(tokens[idx:idx+sel_length])}')"
                )

            inspect_cell = result.get_cell(sel_length, sel_start)
            if inspect_cell:
                sub_str = " ".join(inspect_cell.substring)
                st.markdown(f"**Inspecting Cell:** `T[{sel_length}][{sel_start+1}]` &bull; **Substring:** `'{sub_str}'`")
                if not inspect_cell.variables:
                    st.info("Cell is empty (∅): No production rules can derive this substring.")
                else:
                    st.write(f"**Variables in cell:** {', '.join(f'`{v}`' for v in sorted(inspect_cell.variables))}")
                    for var, derivs in inspect_cell.derivations.items():
                        st.markdown(f"**Derivations for `{var}`:**")
                        for d in derivs:
                            st.write(f"- {d['explanation']} *(via `{d['rule']}`)*")

            # Parse Tree from CYK Backpointers
            if result.is_accepted:
                st.subheader("🌲 Reconstructed Parse Tree (from CYK Backpointers)")
                tree_root = cyk_to_tree(parse_grammar, result)
                if tree_root:
                    st.graphviz_chart(tree_root.to_dot())
