"""
Tests for CYK Parsing dynamic programming algorithm.
"""

import pytest
from algorithms.grammar import CFG
from algorithms.cnf import convert_to_cnf
from algorithms.cyk import cyk_parse


@pytest.fixture
def cnf_anbn():
    raw_g = CFG.from_text("S -> a S b | ε", start_symbol="S")
    cnf_g, _ = convert_to_cnf(raw_g)
    return cnf_g


def test_cyk_empty_string(cnf_anbn):
    res = cyk_parse(cnf_anbn, [])
    assert res.is_accepted
    assert "ACCEPTED" in res.explanation


def test_cyk_valid_strings(cnf_anbn):
    for s in ["ab", "aabb", "aaabbb"]:
        tokens = list(s)
        res = cyk_parse(cnf_anbn, tokens)
        assert res.is_accepted, f"String '{s}' should be accepted by anbn CYK parse."
        # Verify table shape: n x (n-l+1)
        n = len(tokens)
        assert len(res.table) == n
        assert len(res.table[0]) == n
        assert len(res.table[-1]) == 1


def test_cyk_rejected_strings(cnf_anbn):
    for s in ["a", "b", "aab", "abb", "abab", "ba", "aaabb"]:
        tokens = list(s)
        res = cyk_parse(cnf_anbn, tokens)
        assert not res.is_accepted, f"String '{s}' should be rejected by anbn CYK parse."


def test_cyk_intermediate_cell_derivations(cnf_anbn):
    tokens = ["a", "b"]
    res = cyk_parse(cnf_anbn, tokens)
    assert res.is_accepted
    # Base cells should have terminal derivations
    cell_0_0 = res.get_cell(1, 0)
    assert len(cell_0_0.variables) > 0
    # Top cell should have binary derivation
    top_cell = res.get_cell(2, 0)
    assert cnf_anbn.start_symbol in top_cell.variables
