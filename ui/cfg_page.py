"""
CFG Explorer and Grammar Management Page.
Redesigned with modern cards, symbol badges, and diagnostics.
"""

import streamlit as st
import pandas as pd
from algorithms.grammar import CFG, get_predefined_grammars
from algorithms.validation import validate_grammar
from algorithms.derivations import generate_sample_strings


def render_cfg_page():
    st.title("🔤 Context-Free Grammar Workspace")
    st.caption("Inspect, create, edit, validate, and analyze Context-Free Grammars (CFGs).")

    tabs = st.tabs([
        "📋 Active Grammar & Diagnostics",
        "✏️ Custom Grammar Editor",
        "💡 Predefined Academic Library"
    ])

    # -------------------------------------------------------------
    # TAB 1: Active Grammar & Diagnostics
    # -------------------------------------------------------------
    with tabs[0]:
        g: CFG = st.session_state.current_grammar

        # Metric Badges
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.markdown(f"""
            <div style="background:#ffffff; border:1px solid #e2e8f0; border-radius:10px; padding:14px; text-align:center;">
                <span style="font-size:0.75rem; text-transform:uppercase; color:#64748b; font-weight:700;">Start Symbol</span>
                <div style="font-size:1.3rem; font-weight:800; color:#b45309;">{g.start_symbol}</div>
            </div>
            """, unsafe_allow_html=True)
        with c2:
            st.markdown(f"""
            <div style="background:#ffffff; border:1px solid #e2e8f0; border-radius:10px; padding:14px; text-align:center;">
                <span style="font-size:0.75rem; text-transform:uppercase; color:#64748b; font-weight:700;">Variables (V)</span>
                <div style="font-size:1.3rem; font-weight:800; color:#6d28d9;">{len(g.variables)}</div>
            </div>
            """, unsafe_allow_html=True)
        with c3:
            st.markdown(f"""
            <div style="background:#ffffff; border:1px solid #e2e8f0; border-radius:10px; padding:14px; text-align:center;">
                <span style="font-size:0.75rem; text-transform:uppercase; color:#64748b; font-weight:700;">Terminals (Σ)</span>
                <div style="font-size:1.3rem; font-weight:800; color:#047857;">{len(g.terminals)}</div>
            </div>
            """, unsafe_allow_html=True)
        with c4:
            st.markdown(f"""
            <div style="background:#ffffff; border:1px solid #e2e8f0; border-radius:10px; padding:14px; text-align:center;">
                <span style="font-size:0.75rem; text-transform:uppercase; color:#64748b; font-weight:700;">Productions</span>
                <div style="font-size:1.3rem; font-weight:800; color:#0f172a;">{len(g.productions)}</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Production Rules View
        st.subheader("Production Rules Table ($R$)")
        rules_data = []
        for idx, p in enumerate(g.productions, 1):
            rhs_str = " ".join(p.clean_body) if p.clean_body else "ε (empty)"
            p_type = "Epsilon Rule (ε)" if p.is_epsilon else ("Terminal" if len(p.clean_body) == 1 and p.clean_body[0] in g.terminals else "Compound Expansion")
            rules_data.append({
                "#": idx,
                "LHS (Variable)": p.head,
                "RHS (Body)": rhs_str,
                "Classification": p_type
            })
        st.dataframe(pd.DataFrame(rules_data), use_container_width=True, hide_index=True)

        # Grammar Diagnostics
        st.subheader("Grammar Validation & Diagnostics")
        is_valid, errors, warnings = validate_grammar(g)

        if is_valid and not warnings:
            st.markdown("""
            <div class="status-banner-accepted">
                <b>✓ Grammar is Well-Formed & Valid:</b> All variables have defining productions, terminals are consistent, and start symbol derives terminal strings.
            </div>
            """, unsafe_allow_html=True)
        else:
            if errors:
                for err in errors:
                    st.error(f"❌ {err}")
            if warnings:
                for warn in warnings:
                    st.warning(f"⚠️ {warn}")

        # Symbol Sets
        with st.expander("🔍 Detailed Symbol Sets Breakdown", expanded=False):
            col_v, col_t = st.columns(2)
            with col_v:
                st.write("**Non-Terminal Variables ($V$):**")
                v_html = " ".join([f"<span class='badge-tag badge-var'>{v}</span>" for v in sorted(g.variables)])
                st.markdown(v_html, unsafe_allow_html=True)
            with col_t:
                st.write(r"**Terminal Symbols ($\Sigma$):**")
                t_html = " ".join([f"<span class='badge-tag badge-term'>{t}</span>" for t in sorted(g.terminals)])
                st.markdown(t_html, unsafe_allow_html=True)

        # Sample Generated Strings
        st.subheader("Sample Generated Strings")
        with st.spinner("Generating sample terminal strings via bounded BFS..."):
            samples = generate_sample_strings(g, max_depth=6, max_count=12)
        if samples:
            chips = " ".join([f"<span class='badge-tag badge-term'>{s if s else 'ε'}</span>" for s in samples])
            st.markdown(chips, unsafe_allow_html=True)
        else:
            st.info("No terminal strings found within search bound depth.")

    # -------------------------------------------------------------
    # TAB 2: Custom Grammar Editor
    # -------------------------------------------------------------
    with tabs[1]:
        st.subheader("Interactive Grammar Editor")
        st.markdown("""
        Enter production rules one per line using `->` or `::=`. Separate alternatives with `|`.
        Epsilon productions can be represented as `epsilon`, `eps`, `ε`, or empty RHS.
        """)

        # Template quick buttons
        col_t1, col_t2, col_t3 = st.columns(3)
        with col_t1:
            st.caption("Syntax Helper: Epsilon aliases (`ε`, `epsilon`, `eps`) are supported.")
        with col_t2:
            st.caption("Multi-character terminals like `id` are supported.")
        with col_t3:
            st.caption("Whitespaces delineate individual tokens.")

        custom_text = st.text_area(
            "Production Rules:",
            value=st.session_state.current_grammar.to_text(),
            height=180,
            help="Example:\nS -> a S b | epsilon"
        )

        col_s, col_t = st.columns(2)
        with col_s:
            custom_start = st.text_input(
                "Start Symbol (optional override):",
                value=st.session_state.current_grammar.start_symbol,
                placeholder="Defaults to LHS of first rule"
            )
        with col_t:
            custom_terms = st.text_input(
                "Explicit Terminals (optional):",
                value=" ".join(sorted(st.session_state.current_grammar.terminals)),
                placeholder="e.g. a, b or id, +, *"
            )

        col_save, col_reset = st.columns([1, 3])
        with col_save:
            if st.button("💾 Apply & Update Grammar", type="primary", use_container_width=True):
                try:
                    term_set = set(custom_terms.replace(",", " ").split()) if custom_terms.strip() else None
                    new_g = CFG.from_text(
                        text=custom_text,
                        start_symbol=custom_start.strip() if custom_start.strip() else None,
                        custom_terminals=term_set
                    )
                    valid, errs, warns = validate_grammar(new_g)
                    if not valid:
                        st.error("Validation failed:\n" + "\n".join(errs))
                    else:
                        st.session_state.current_grammar = new_g
                        st.session_state.selected_grammar_key = "Custom Grammar"
                        st.session_state.predefined_grammars["Custom Grammar"] = {
                            "name": "Custom User Grammar",
                            "description": "User-defined custom grammar configuration.",
                            "text": custom_text,
                            "start_symbol": new_g.start_symbol,
                            "terminals": new_g.terminals,
                            "example_strings": [],
                            "rejected_strings": []
                        }
                        st.success("Custom grammar saved and activated successfully!")
                        st.rerun()
                except Exception as ex:
                    st.error(f"Error parsing grammar: {str(ex)}")

        with col_reset:
            if st.button("🔄 Reset to Default", use_container_width=True):
                key = st.session_state.selected_grammar_key
                if key in st.session_state.predefined_grammars and key != "Custom Grammar":
                    data = st.session_state.predefined_grammars[key]
                    st.session_state.current_grammar = CFG.from_text(data["text"], start_symbol=data["start_symbol"])
                    st.success(f"Reset to '{key}'.")
                    st.rerun()

    # -------------------------------------------------------------
    # TAB 3: Predefined Academic Library
    # -------------------------------------------------------------
    with tabs[2]:
        st.subheader("Academic Predefined Grammars Library")
        catalog = get_predefined_grammars()
        for key, info in catalog.items():
            with st.container():
                st.markdown(f"#### 📖 {info['name']}")
                st.write(info['description'])
                st.code(info['text'], language="text")

                col_load, col_samples = st.columns([1, 3])
                with col_load:
                    if st.button(f"Load '{key}'", key=f"load_{key}", use_container_width=True):
                        st.session_state.selected_grammar_key = key
                        st.session_state.current_grammar = CFG.from_text(
                            info["text"],
                            start_symbol=info["start_symbol"]
                        )
                        st.success(f"Loaded '{key}' into active session.")
                        st.rerun()
                with col_samples:
                    samples_str = ", ".join([repr(s) if s else "ε" for s in info['example_strings']])
                    st.caption(f"**Sample valid strings:** {samples_str}")
                st.divider()
