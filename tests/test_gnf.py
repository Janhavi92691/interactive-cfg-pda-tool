"""
Tests for Greibach Normal Form (GNF) conversion and validation.
"""

import pytest
from algorithms.grammar import CFG
from algorithms.gnf import convert_to_gnf, is_in_gnf


def test_gnf_conversion_simple():
    text = """
    S -> a A | b
    A -> a
    """
    g = CFG.from_text(text, start_symbol="S")
    gnf_g, stages = convert_to_gnf(g)
    assert len(stages) >= 4
    valid, violations = is_in_gnf(gnf_g)
    assert valid, f"GNF violations: {violations}"


def test_gnf_conversion_anbn():
    g = CFG.from_text("S -> a S b | a b", start_symbol="S")
    gnf_g, stages = convert_to_gnf(g)
    valid, violations = is_in_gnf(gnf_g)
    assert valid, f"GNF violations in anbn: {violations}"
    # Every production should start with terminal
    for p in gnf_g.productions:
        if not p.is_epsilon:
            assert p.clean_body[0] in gnf_g.terminals
