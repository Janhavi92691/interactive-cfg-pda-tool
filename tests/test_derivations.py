"""
Tests for Leftmost, Rightmost derivations and string generation.
"""

import pytest
from algorithms.grammar import CFG
from algorithms.derivations import leftmost_derivation, rightmost_derivation, generate_sample_strings


@pytest.fixture
def anbn_grammar():
    return CFG.from_text("S -> a S b | ε", start_symbol="S")


@pytest.fixture
def palindrome_grammar():
    return CFG.from_text("S -> a S a | b S b | a | b | ε", start_symbol="S")


def test_leftmost_derivation_anbn(anbn_grammar):
    target = ["a", "a", "b", "b"]
    steps, msg = leftmost_derivation(anbn_grammar, target)
    assert steps is not None
    assert "Success" in msg
    assert steps[0].sentential_form == ("S",)
    assert steps[-1].sentential_form == ("a", "a", "b", "b")
    assert len(steps) == 4  # S => aSb => aaSbb => aabb


def test_rightmost_derivation_anbn(anbn_grammar):
    target = ["a", "b"]
    steps, msg = rightmost_derivation(anbn_grammar, target)
    assert steps is not None
    assert steps[-1].sentential_form == ("a", "b")


def test_palindrome_derivation(palindrome_grammar):
    target = ["a", "b", "a"]
    steps, msg = leftmost_derivation(palindrome_grammar, target)
    assert steps is not None
    assert steps[-1].sentential_form == ("a", "b", "a")


def test_derivation_rejection(anbn_grammar):
    target = ["a", "a", "b"]  # Not in anbn
    steps, msg = leftmost_derivation(anbn_grammar, target, max_steps=8)
    assert steps is None
    assert "cannot be derived" in msg or "Search bound reached" in msg


def test_generate_sample_strings(anbn_grammar):
    samples = generate_sample_strings(anbn_grammar, max_depth=6, max_count=5)
    assert len(samples) >= 3
    # Should contain ε, ab, aabb
    assert any(s in ("ε", "") for s in samples)
    assert "ab" in samples
    assert "aabb" in samples
