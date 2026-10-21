"""
Tests for CFG parsing, tokenization, validation, and serialization.
"""

import pytest
from algorithms.grammar import CFG, Production, EPSILON, get_predefined_grammars
from algorithms.validation import validate_grammar


def test_production_basics():
    p1 = Production("S", ("a", "S", "b"))
    assert p1.head == "S"
    assert p1.clean_body == ("a", "S", "b")
    assert not p1.is_epsilon

    p_eps = Production("S", ("epsilon",))
    assert p_eps.is_epsilon
    assert p_eps.clean_body == ()

    p_empty = Production("S", ())
    assert p_empty.is_epsilon
    assert p_empty.clean_body == ()


def test_cfg_from_text_anbn():
    text = "S -> a S b | epsilon"
    cfg = CFG.from_text(text)
    assert cfg.start_symbol == "S"
    assert "S" in cfg.variables
    assert "a" in cfg.terminals
    assert "b" in cfg.terminals
    assert len(cfg.productions) == 2


def test_arithmetic_grammar_tokenization():
    text = """
    E -> E + T | T
    T -> T * F | F
    F -> ( E ) | id
    """
    cfg = CFG.from_text(text)
    assert cfg.start_symbol == "E"
    assert "id" in cfg.terminals
    assert "+" in cfg.terminals
    assert "*" in cfg.terminals
    assert "(" in cfg.terminals
    assert ")" in cfg.terminals

    # Test tokenizing arithmetic string with 'id'
    tokens = cfg.tokenize_input("id + id * id")
    assert tokens == ["id", "+", "id", "*", "id"]

    tokens_paren = cfg.tokenize_input("( id + id ) * id")
    assert tokens_paren == ["(", "id", "+", "id", ")", "*", "id"]


def test_validation_missing_start_symbol():
    cfg = CFG(variables=set(), terminals={"a"}, productions=[], start_symbol="")
    is_valid, errors, _ = validate_grammar(cfg)
    assert not is_valid
    assert any("Start symbol is missing" in err for err in errors)


def test_validation_undefined_rhs_variable():
    # Production references X which is neither variable nor terminal
    prod = Production("S", ("a", "X"))
    cfg = CFG(variables={"S"}, terminals={"a"}, productions=[prod], start_symbol="S")
    is_valid, errors, _ = validate_grammar(cfg)
    assert not is_valid
    assert any("X" in err for err in errors)


def test_predefined_grammars_validity():
    catalog = get_predefined_grammars()
    assert len(catalog) >= 3
    for name, data in catalog.items():
        cfg = CFG.from_text(data["text"], start_symbol=data["start_symbol"])
        is_valid, errors, warnings = validate_grammar(cfg)
        assert is_valid, f"Grammar {name} failed validation: {errors}"
