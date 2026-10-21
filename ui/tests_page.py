"""
Test Cases and Automated Results Page.
Redesigned with category KPI cards, CSV export, and filtered inspection.
"""

import streamlit as st
import pandas as pd
from algorithms.grammar import CFG, Production
from algorithms.validation import validate_grammar
from algorithms.derivations import leftmost_derivation
from algorithms.cnf import convert_to_cnf, is_in_cnf
from algorithms.gnf import convert_to_gnf, is_in_gnf
from algorithms.cyk import cyk_parse
from algorithms.pda import get_predefined_pdas


def run_all_test_cases():
    """Execute test matrix and return structured results."""
    records = []
    pdas = get_predefined_pdas()
    anbn_pda = pdas["PDA: a^n b^n"]
    g_anbn = CFG.from_text("S -> a S b | ε", start_symbol="S")
    cnf_anbn, _ = convert_to_cnf(g_anbn)

    # 1. Grammar Parsing & Multi-character terminals
    g_arith = CFG.from_text("E -> E + T | T\nT -> T * F | F\nF -> ( E ) | id", start_symbol="E")
    records.append({
        "Category": "Grammar Parsing",
        "Test Case": "Arithmetic with 'id'",
        "Input": "F -> ( E ) | id",
        "Expected": "'id' in terminals",
        "Actual": "'id' in terminals" if "id" in g_arith.terminals else "split",
        "Status": "✅ PASS" if "id" in g_arith.terminals else "❌ FAIL",
        "Explanation": "Ensures multi-character terminals such as 'id' are tokenized atomically."
    })

    # 2. Grammar Validation
    g_bad = CFG(variables={"S"}, terminals={"a"}, productions=[Production("S", ("a", "Z"))], start_symbol="S")
    val_ok, errs, _ = validate_grammar(g_bad)
    records.append({
        "Category": "Grammar Validation",
        "Test Case": "Undefined Variable on RHS",
        "Input": "S -> a Z (Z undefined)",
        "Expected": "Validation Error caught",
        "Actual": "Validation Error caught" if not val_ok else "Allowed",
        "Status": "✅ PASS" if not val_ok else "❌ FAIL",
        "Explanation": "Rejects production rules referencing undefined variables."
    })

    # 3. Derivations
    steps_lm, msg_lm = leftmost_derivation(g_anbn, ["a", "a", "b", "b"])
    records.append({
        "Category": "Derivations",
        "Test Case": "Leftmost derivation for 'aabb'",
        "Input": "'aabb' in S -> aSb | ε",
        "Expected": "Derived in 4 steps",
        "Actual": f"Derived in {len(steps_lm)} steps" if steps_lm else "Failed",
        "Status": "✅ PASS" if steps_lm and len(steps_lm) == 4 else "❌ FAIL",
        "Explanation": "Verifies step-by-step leftmost sentential replacement."
    })

    # 4. CNF Conversion
    cnf_ok, cnf_viols = is_in_cnf(cnf_anbn)
    records.append({
        "Category": "CNF Conversion",
        "Test Case": "CNF structural requirements",
        "Input": "S -> a S b | ε",
        "Expected": "Valid CNF (0 violations)",
        "Actual": f"Violations: {len(cnf_viols)}",
        "Status": "✅ PASS" if cnf_ok else "❌ FAIL",
        "Explanation": "All productions conform to A -> BC, A -> a, or S0 -> ε."
    })

    # 5. GNF Conversion
    g_gnf_test = CFG.from_text("S -> a S b | a b", start_symbol="S")
    gnf_res, _ = convert_to_gnf(g_gnf_test)
    gnf_ok, gnf_viols = is_in_gnf(gnf_res)
    records.append({
        "Category": "GNF Conversion",
        "Test Case": "GNF terminal-first rules",
        "Input": "S -> a S b | a b",
        "Expected": "Valid GNF (0 violations)",
        "Actual": f"Violations: {len(gnf_viols)}",
        "Status": "✅ PASS" if gnf_ok else "❌ FAIL",
        "Explanation": "All non-empty rules begin with terminal followed by variables."
    })

    # 6. CYK Parsing
    cyk_cases = [
        ([], True, "Epsilon string w = ε"),
        (["a", "b"], True, "Valid string 'ab'"),
        (["a", "a", "b", "b"], True, "Valid string 'aabb'"),
        (["a"], False, "Rejected string 'a'"),
        (["a", "a", "b"], False, "Rejected string 'aab'"),
        (["a", "b", "a", "b"], False, "Rejected string 'abab'")
    ]
    for toks, should_acc, label in cyk_cases:
        res = cyk_parse(cnf_anbn, toks)
        passed = (res.is_accepted == should_acc)
        records.append({
            "Category": "CYK Parsing",
            "Test Case": label,
            "Input": "".join(toks) if toks else "ε",
            "Expected": "Accepted" if should_acc else "Rejected",
            "Actual": "Accepted" if res.is_accepted else "Rejected",
            "Status": "✅ PASS" if passed else "❌ FAIL",
            "Explanation": f"CYK DP matrix membership verification for {label}."
        })

    # 7. PDA Simulation
    pda_cases = [
        ([], True, "Epsilon string w = ε"),
        (["a", "b"], True, "Valid string 'ab'"),
        (["a", "a", "b", "b"], True, "Valid string 'aabb'"),
        (["a", "a", "a", "b", "b", "b"], True, "Valid string 'aaabbb'"),
        (["a"], False, "Rejected string 'a'"),
        (["b"], False, "Rejected string 'b'"),
        (["a", "a", "b"], False, "Rejected string 'aab'"),
        (["a", "b", "b"], False, "Rejected string 'abb'"),
        (["a", "b", "a", "b"], False, "Rejected string 'abab'")
    ]
    for toks, should_acc, label in pda_cases:
        is_acc, _, diag = anbn_pda.simulate(toks)
        passed = (is_acc == should_acc)
        records.append({
            "Category": "PDA Simulator",
            "Test Case": label,
            "Input": "".join(toks) if toks else "ε",
            "Expected": "Accepted" if should_acc else "Rejected",
            "Actual": "Accepted" if is_acc else "Rejected",
            "Status": "✅ PASS" if passed else "❌ FAIL",
            "Explanation": f"PDA transition and stack simulation: {diag[:60]}..."
        })

    return records


def render_tests_page():
    st.title("🧪 Automated Test Suite & Verification Matrix")
    st.caption("Live test runner evaluating grammar parsing, transformations, parsing tables, and automata mechanics.")

    records = run_all_test_cases()
    df = pd.DataFrame(records)

    total_tests = len(df)
    passed_tests = sum(df["Status"] == "✅ PASS")
    failed_tests = total_tests - passed_tests

    # Top KPI Banner
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    with kpi1:
        st.metric("Total Test Cases", total_tests)
    with kpi2:
        st.metric("Passed Cases", passed_tests)
    with kpi3:
        st.metric("Failed Cases", failed_tests)
    with kpi4:
        st.metric("Success Rate", f"{(passed_tests/total_tests)*100:.1f}%")

    if failed_tests == 0:
        st.markdown(f"""
        <div class="status-banner-accepted">
            <b>✓ Full Verification Succeeded:</b> All <b>{total_tests}</b> test cases across all modules executed with 100% pass rate.
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="status-banner-rejected">
            <b>⚠️ Test Failures Encountered:</b> {failed_tests} tests did not match expected outcomes.
        </div>
        """, unsafe_allow_html=True)

    # Controls Row: Filter by Category, Search, CSV export
    col_filter, col_search, col_csv = st.columns([1, 2, 1])
    with col_filter:
        categories = ["All Categories"] + sorted(df["Category"].unique().tolist())
        selected_cat = st.selectbox("Filter Category:", categories)

    with col_search:
        search_kw = st.text_input("Search Test Cases / Inputs:", placeholder="e.g. aabb, id, CNF, PDA...")

    with col_csv:
        st.write("")
        st.write("")
        csv_data = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            "📥 Export CSV Report",
            data=csv_data,
            file_name="cfg_pda_test_report.csv",
            mime="text/csv",
            use_container_width=True
        )

    # Filter DataFrame
    filtered_df = df.copy()
    if selected_cat != "All Categories":
        filtered_df = filtered_df[filtered_df["Category"] == selected_cat]

    if search_kw.strip():
        kw = search_kw.strip().lower()
        filtered_df = filtered_df[
            filtered_df["Test Case"].str.lower().str.contains(kw) |
            filtered_df["Input"].str.lower().str.contains(kw) |
            filtered_df["Category"].str.lower().str.contains(kw) |
            filtered_df["Explanation"].str.lower().str.contains(kw)
        ]

    st.dataframe(filtered_df, use_container_width=True, hide_index=True)
