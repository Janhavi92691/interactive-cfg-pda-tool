"""
CFG Derivation algorithms (Leftmost, Rightmost, and Target String Search).
"""

from typing import List, Tuple, Optional, Dict, Any, Set
from collections import deque
from .grammar import CFG, Production, EPSILON


class DerivationStep:
    """Represents a single step in a derivation."""
    def __init__(
        self,
        step_number: int,
        sentential_form: Tuple[str, ...],
        replaced_variable: Optional[str] = None,
        replaced_index: Optional[int] = None,
        rule_applied: Optional[Production] = None,
        explanation: str = ""
    ):
        self.step_number = step_number
        self.sentential_form = sentential_form
        self.replaced_variable = replaced_variable
        self.replaced_index = replaced_index
        self.rule_applied = rule_applied
        self.explanation = explanation

    def form_string(self) -> str:
        if not self.sentential_form:
            return EPSILON
        return " ".join(self.sentential_form)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "step": self.step_number,
            "form": self.form_string(),
            "rule": str(self.rule_applied) if self.rule_applied else "Initial Start Symbol",
            "replaced": f"{self.replaced_variable} at position {self.replaced_index}" if self.replaced_variable else "-",
            "explanation": self.explanation
        }


def find_derivation(
    grammar: CFG,
    target_tokens: List[str],
    mode: str = "leftmost",
    max_steps: int = 15,
    max_queue: int = 5000
) -> Tuple[Optional[List[DerivationStep]], str]:
    """
    Search for a derivation of target_tokens in grammar using BFS.
    mode: 'leftmost' or 'rightmost'.
    Returns: (list of DerivationSteps if found, status_explanation)
    """
    target_tuple = tuple(target_tokens)
    target_len = len(target_tuple)

    # State: (sentential_form, list_of_steps)
    initial_form = (grammar.start_symbol,)
    initial_step = DerivationStep(
        step_number=0,
        sentential_form=initial_form,
        explanation=f"Start with root variable '{grammar.start_symbol}'"
    )

    if initial_form == target_tuple:
        return [initial_step], "Target is identical to start symbol."

    queue = deque([(initial_form, [initial_step])])
    visited: Set[Tuple[str, ...]] = {initial_form}
    nodes_explored = 0

    while queue and nodes_explored < max_queue:
        nodes_explored += 1
        curr_form, steps = queue.popleft()

        if len(steps) > max_steps:
            continue

        # Find variable to replace based on mode
        var_indices = [
            i for i, sym in enumerate(curr_form) if sym in grammar.variables
        ]
        if not var_indices:
            # Fully terminal sentential form
            if curr_form == target_tuple:
                return steps, f"Success! Derived in {len(steps)-1} steps ({nodes_explored} states explored)."
            continue

        target_idx = var_indices[0] if mode == "leftmost" else var_indices[-1]
        var_to_replace = curr_form[target_idx]

        # Count terminals in curr_form: pruning heuristic
        # If terminal count > target_len and grammar has no epsilon rules on remaining vars,
        # it might be prunable, but we keep it safe
        term_count = sum(1 for sym in curr_form if sym in grammar.terminals)
        if term_count > target_len + 3 and not any(p.is_epsilon for p in grammar.productions):
            continue

        # Try all productions for var_to_replace
        for prod in grammar.productions_for(var_to_replace):
            # Replace var_to_replace with prod.clean_body
            next_form = curr_form[:target_idx] + prod.clean_body + curr_form[target_idx + 1:]

            rhs_str = " ".join(prod.clean_body) if prod.clean_body else EPSILON
            step_obj = DerivationStep(
                step_number=len(steps),
                sentential_form=next_form,
                replaced_variable=var_to_replace,
                replaced_index=target_idx,
                rule_applied=prod,
                explanation=f"Applied rule '{prod.head} -> {rhs_str}' on {mode} non-terminal '{var_to_replace}'"
            )
            next_steps = steps + [step_obj]

            if next_form == target_tuple:
                return next_steps, f"Success! Found valid {mode} derivation in {len(next_steps)-1} steps ({nodes_explored} states explored)."

            # Bound queue length and avoid infinite cycling of identical sentential forms
            if next_form not in visited:
                visited.add(next_form)
                queue.append((next_form, next_steps))

    if nodes_explored >= max_queue:
        return None, f"Search bound reached ({max_queue} states evaluated, max depth {max_steps}). A derivation may exist beyond this bound, or the string may not belong to the language."

    return None, f"Target string cannot be derived from grammar '{grammar.start_symbol}' within depth {max_steps} ({nodes_explored} states explored)."


def leftmost_derivation(
    grammar: CFG,
    target_tokens: List[str],
    max_steps: int = 15
) -> Tuple[Optional[List[DerivationStep]], str]:
    return find_derivation(grammar, target_tokens, mode="leftmost", max_steps=max_steps)


def rightmost_derivation(
    grammar: CFG,
    target_tokens: List[str],
    max_steps: int = 15
) -> Tuple[Optional[List[DerivationStep]], str]:
    return find_derivation(grammar, target_tokens, mode="rightmost", max_steps=max_steps)


def generate_sample_strings(
    grammar: CFG,
    max_depth: int = 6,
    max_count: int = 15
) -> List[str]:
    """Generate example terminal strings in the language via bounded breadth-first search."""
    queue = deque([((grammar.start_symbol,), 0)])
    generated: List[str] = []
    seen_strings: Set[str] = set()
    visited_forms: Set[Tuple[str, ...]] = {(grammar.start_symbol,)}

    while queue and len(generated) < max_count:
        form, depth = queue.popleft()
        # Check if form is all terminals
        if all(sym in grammar.terminals for sym in form):
            res_str = "".join(form) if form else EPSILON
            if res_str not in seen_strings:
                seen_strings.add(res_str)
                generated.append(res_str)
            continue

        if depth >= max_depth:
            continue

        # Expand leftmost variable
        for i, sym in enumerate(form):
            if sym in grammar.variables:
                for prod in grammar.productions_for(sym):
                    next_form = form[:i] + prod.clean_body + form[i + 1:]
                    if next_form not in visited_forms:
                        visited_forms.add(next_form)
                        queue.append((next_form, depth + 1))
                break

    return sorted(generated, key=lambda s: (len(s), s))
