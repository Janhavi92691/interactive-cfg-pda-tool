"""
Cocke-Younger-Kasami (CYK) Dynamic Programming Membership Algorithm.
"""

from typing import List, Set, Dict, Tuple, Optional, Any
from .grammar import CFG, Production
from .cnf import is_in_cnf


class CYKCell:
    """Represents a cell in the CYK dynamic programming table with explanation."""
    def __init__(self, length: int, start_idx: int, substring: List[str]):
        self.length = length
        self.start_idx = start_idx
        self.substring = substring
        self.variables: Set[str] = set()
        # derivations: var -> list of (rule, split_point_k, left_var, right_var)
        self.derivations: Dict[str, List[Dict[str, Any]]] = {}

    def add_terminal_derivation(self, var: str, rule: Production, terminal: str):
        self.variables.add(var)
        self.derivations.setdefault(var, []).append({
            "type": "terminal",
            "rule": str(rule),
            "terminal": terminal,
            "explanation": f"Rule '{rule}' directly yields terminal '{terminal}'"
        })

    def add_binary_derivation(
        self,
        var: str,
        rule: Production,
        split_k: int,
        left_var: str,
        right_var: str
    ):
        self.variables.add(var)
        self.derivations.setdefault(var, []).append({
            "type": "binary",
            "rule": str(rule),
            "split_k": split_k,
            "left_var": left_var,
            "right_var": right_var,
            "explanation": f"Rule '{rule}' combines left '{left_var}' (len {split_k}) with right '{right_var}' (len {self.length - split_k})"
        })


class CYKResult:
    """Encapsulates the complete result of a CYK parse."""
    def __init__(
        self,
        tokens: List[str],
        table: List[List[CYKCell]],
        is_accepted: bool,
        explanation: str,
        start_symbol: str,
        is_valid_cnf: bool,
        cnf_violations: List[str]
    ):
        self.tokens = tokens
        self.table = table  # table[l-1][i] where l is length (1..n), i is 0-indexed start
        self.is_accepted = is_accepted
        self.explanation = explanation
        self.start_symbol = start_symbol
        self.is_valid_cnf = is_valid_cnf
        self.cnf_violations = cnf_violations

    def get_cell(self, length: int, start_idx: int) -> Optional[CYKCell]:
        if 1 <= length <= len(self.tokens) and 0 <= start_idx <= len(self.tokens) - length:
            return self.table[length - 1][start_idx]
        return None


def cyk_parse(grammar: CFG, tokens: List[str]) -> CYKResult:
    """
    Execute the CYK dynamic programming algorithm on tokenized input string.
    Expects grammar to be in Chomsky Normal Form (CNF).
    """
    valid_cnf, violations = is_in_cnf(grammar)
    n = len(tokens)

    # Handle empty string w = ε (length 0)
    if n == 0:
        has_eps_start = any(
            p.head == grammar.start_symbol and p.is_epsilon for p in grammar.productions
        )
        explanation = (
            f"Empty string ε is ACCEPTED because start rule '{grammar.start_symbol} -> ε' is present in the grammar."
            if has_eps_start else
            f"Empty string ε is REJECTED because the grammar does not contain the start rule '{grammar.start_symbol} -> ε'."
        )
        return CYKResult(
            tokens=[],
            table=[],
            is_accepted=has_eps_start,
            explanation=explanation,
            start_symbol=grammar.start_symbol,
            is_valid_cnf=valid_cnf,
            cnf_violations=violations
        )

    # Initialize triangular table: table[l-1][i] for length l in 1..n, start i in 0..n-l
    table: List[List[CYKCell]] = []
    for l in range(1, n + 1):
        row: List[CYKCell] = []
        for i in range(n - l + 1):
            sub = tokens[i : i + l]
            row.append(CYKCell(length=l, start_idx=i, substring=sub))
        table.append(row)

    # Base case: length l = 1 (substrings of length 1)
    for i in range(n):
        tok = tokens[i]
        cell = table[0][i]
        for p in grammar.productions:
            if len(p.clean_body) == 1 and p.clean_body[0] == tok:
                cell.add_terminal_derivation(p.head, p, tok)

    # Inductive case: length l from 2 to n
    for l in range(2, n + 1):
        for i in range(n - l + 1):
            cell = table[l - 1][i]
            # Try all partition points k from 1 to l - 1
            for k in range(1, l):
                left_cell = table[k - 1][i]
                right_cell = table[l - k - 1][i + k]

                # If either cell is empty, no combination possible for this split
                if not left_cell.variables or not right_cell.variables:
                    continue

                for p in grammar.productions:
                    if len(p.clean_body) == 2:
                        B, C = p.clean_body[0], p.clean_body[1]
                        if B in left_cell.variables and C in right_cell.variables:
                            cell.add_binary_derivation(p.head, p, k, B, C)

    # Final root cell: table[n-1][0] spanning entire string
    root_cell = table[n - 1][0]
    is_accepted = grammar.start_symbol in root_cell.variables

    token_str = " ".join(tokens)
    if is_accepted:
        explanation = (
            f"ACCEPTED: The root cell table[{n}][1] spanning the full string '{token_str}' "
            f"contains the grammar's start symbol '{grammar.start_symbol}'."
        )
    else:
        explanation = (
            f"REJECTED: The root cell table[{n}][1] spanning '{token_str}' "
            f"contains {sorted(root_cell.variables) if root_cell.variables else 'no variables'}, "
            f"which does not include the start symbol '{grammar.start_symbol}'."
        )

    if not valid_cnf:
        explanation += " (Note: Grammar contains CNF violations, which may affect accuracy unless converted to CNF first.)"

    return CYKResult(
        tokens=tokens,
        table=table,
        is_accepted=is_accepted,
        explanation=explanation,
        start_symbol=grammar.start_symbol,
        is_valid_cnf=valid_cnf,
        cnf_violations=violations
    )
