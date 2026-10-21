"""
Tests for Pushdown Automaton (PDA) simulation and stack mechanics.
"""

import pytest
from algorithms.pda import get_predefined_pdas, PDASimulator


@pytest.fixture
def anbn_pda():
    catalog = get_predefined_pdas()
    return catalog["PDA: a^n b^n"]


def test_pda_anbn_accepted_strings(anbn_pda):
    accepted_cases = ["", "ab", "aabb", "aaabbb"]
    for s in accepted_cases:
        tokens = list(s)
        is_acc, steps, diag = anbn_pda.simulate(tokens)
        assert is_acc, f"PDA should accept '{s}', got: {diag}"
        assert len(steps) > 0


def test_pda_anbn_rejected_strings(anbn_pda):
    rejected_cases = ["a", "b", "aab", "abb", "abab", "ba", "aaabb"]
    for s in rejected_cases:
        tokens = list(s)
        is_acc, steps, diag = anbn_pda.simulate(tokens)
        assert not is_acc, f"PDA should reject '{s}', got: {diag}"
        assert "REJECTED" in diag


def test_pda_simulator_controls(anbn_pda):
    sim = PDASimulator(anbn_pda, "aabb")
    assert sim.is_accepted
    assert sim.total_steps > 1
    assert sim.current_step_index == 0

    # Step forward
    assert sim.step_forward()
    assert sim.current_step_index == 1

    # Step backward
    assert sim.step_backward()
    assert sim.current_step_index == 0

    # Run all
    sim.run_all()
    assert sim.current_step_index == sim.total_steps - 1

    # Reset
    sim.reset()
    assert sim.current_step_index == 0


def test_pda_dot_diagram(anbn_pda):
    dot_str = anbn_pda.to_dot(current_highlight_state="q0")
    assert "digraph PDA" in dot_str
    assert "q0" in dot_str
    assert "q1" in dot_str
    assert "q2" in dot_str
    assert "fillcolor" in dot_str
