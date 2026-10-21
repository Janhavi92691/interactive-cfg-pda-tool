"""
CFG Validation and Diagnostic algorithms.
"""

from typing import List, Set, Dict, Tuple
from .grammar import CFG, Production


def compute_generating_symbols(grammar: CFG) -> Set[str]:
    """Find all variables that can derive a string of terminals (generating/productive)."""
    generating: Set[str] = set()
    changed = True
    while changed:
        changed = False
        for prod in grammar.productions:
            if prod.head not in generating:
                # Can this production derive terminals?
                # All symbols in body must either be terminals or already in generating
                if all(sym in grammar.terminals or sym in generating for sym in prod.clean_body):
                    generating.add(prod.head)
                    changed = True
    return generating


def compute_reachable_symbols(grammar: CFG) -> Set[str]:
    """Find all symbols reachable from the start symbol."""
    reachable: Set[str] = {grammar.start_symbol}
    changed = True
    while changed:
        changed = False
        for prod in grammar.productions:
            if prod.head in reachable:
                for sym in prod.clean_body:
                    if sym not in reachable:
                        reachable.add(sym)
                        changed = True
    return reachable


def validate_grammar(grammar: CFG) -> Tuple[bool, List[str], List[str]]:
    """
    Validate a Context-Free Grammar.
    Returns:
      (is_valid, errors, warnings)
    """
    errors: List[str] = []
    warnings: List[str] = []

    # 1. Start symbol check
    if not grammar.start_symbol:
        errors.append("Validation Error: Start symbol is missing or empty.")
    elif grammar.start_symbol not in grammar.variables:
        errors.append(f"Validation Error: Start symbol '{grammar.start_symbol}' has no defining production rules.")

    # 2. Check for empty productions list
    if not grammar.productions:
        errors.append("Validation Error: The grammar contains no production rules.")

    # 3. Check for undefined variables on RHS
    defined_heads = {p.head for p in grammar.productions}
    for p in grammar.productions:
        for sym in p.clean_body:
            if sym not in grammar.terminals and sym not in grammar.variables:
                errors.append(
                    f"Validation Error in rule '{p}': Symbol '{sym}' is neither a defined variable nor a terminal."
                )

    # 4. Check for variable without any production rule
    for var in grammar.variables:
        if var not in defined_heads:
            errors.append(f"Validation Error: Variable '{var}' is declared but has no production rules.")

    # If there are already fatal errors, return early
    if errors:
        return False, errors, warnings

    # 5. Productive (generating) symbols check
    generating = compute_generating_symbols(grammar)
    if grammar.start_symbol not in generating:
        warnings.append(
            f"Warning: Start symbol '{grammar.start_symbol}' is non-generating (it cannot derive any string of terminals). Language L(G) is empty."
        )
    non_generating = grammar.variables - generating
    if non_generating:
        warnings.append(
            f"Warning: Non-generating variable(s) detected: {sorted(non_generating)}. These rules can never derive terminal strings."
        )

    # 6. Reachable symbols check
    reachable = compute_reachable_symbols(grammar)
    unreachable_vars = (grammar.variables - reachable)
    if unreachable_vars:
        warnings.append(
            f"Notice: Unreachable variable(s) from start symbol '{grammar.start_symbol}': {sorted(unreachable_vars)}."
        )

    return True, errors, warnings
