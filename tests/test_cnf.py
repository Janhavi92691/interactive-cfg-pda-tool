"""
Tests for Chomsky Normal Form (CNF) conversion and structural validation.
"""

import pytest
from algorithms.grammar import CFG
from algorithms.cnf import convert_to_cnf, is_in_cnf
from algorithms.cyk import cyk_parse


def test_cnf_conversion_anbn():
    g = CFG.from_text("S -> a S b | ε", start_symbol="S")
    cnf_g, stages = convert_to_cnf(g)

    assert len(stages) >= 6
    valid, violations = is_in_cnf(cnf_g)
    assert valid, f"CNF violations in converted anbn grammar: {violations}"

    # Verify that converted grammar accepts 'ab', 'aabb' and rejects 'a', 'aab' via CYK
    res_eps = cyk_parse(cnf_g, [])
    assert res_eps.is_accepted

    res_ab = cyk_parse(cnf_g, ["a", "b"])
    assert res_ab.is_accepted

    res_aabb = cyk_parse(cnf_g, ["a", "a", "b", "b"])
    assert res_aabb.is_accepted

    res_aab = cyk_parse(cnf_g, ["a", "a", "b"])
    assert not res_aab.is_accepted


def test_cnf_conversion_with_unit_and_nullable():
    # Grammar with unit production and nullable
    text = """
    S -> A B | c
    A -> a | ε
    B -> b | A
    """
    g = CFG.from_text(text, start_symbol="S")
    cnf_g, stages = convert_to_cnf(g)
    valid, violations = is_in_cnf(cnf_g)
    assert valid, f"CNF violations: {violations}"


def test_cnf_arithmetic_binarization():
    text = """
    E -> E + T | T
    T -> T * F | F
    F -> a
    """
    g = CFG.from_text(text, start_symbol="E")
    cnf_g, stages = convert_to_cnf(g)
    valid, violations = is_in_cnf(cnf_g)
    assert valid, f"CNF violations in arithmetic grammar: {violations}"
