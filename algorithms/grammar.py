"""
Context-Free Grammar (CFG) and Production representations.
"""

from typing import List, Set, Tuple, Optional, Dict
import re

EPSILON = 'ε'
EPSILON_ALIASES = {'epsilon', 'eps', 'ε', 'lambda', 'λ', '^', "''", '""'}


class Production:
    """Represents a CFG production rule: head -> body."""
    def __init__(self, head: str, body: Tuple[str, ...]):
        self.head = head.strip()
        self.body = tuple(sym.strip() for sym in body if sym.strip())

    @property
    def is_epsilon(self) -> bool:
        return len(self.body) == 0 or (len(self.body) == 1 and self.body[0] in EPSILON_ALIASES)

    @property
    def clean_body(self) -> Tuple[str, ...]:
        if self.is_epsilon:
            return ()
        return self.body

    def __repr__(self) -> str:
        body_str = " ".join(self.clean_body) if self.clean_body else EPSILON
        return f"{self.head} -> {body_str}"

    def __eq__(self, other) -> bool:
        if isinstance(other, Production):
            return self.head == other.head and self.clean_body == other.clean_body
        return False

    def __hash__(self) -> int:
        return hash((self.head, self.clean_body))


class CFG:
    """
    Context-Free Grammar formal 4-tuple G = (V, Σ, R, S):
      V: Variables / Non-terminals (set of strings)
      Σ: Terminals (set of strings)
      R: Production rules (list of Production objects)
      S: Start symbol (string)
    """
    def __init__(
        self,
        variables: Set[str],
        terminals: Set[str],
        productions: List[Production],
        start_symbol: str
    ):
        self.variables = set(variables)
        self.terminals = set(terminals)
        self.productions = [
            Production(p.head, p.clean_body) for p in productions
        ]
        self.start_symbol = start_symbol.strip()

    def productions_for(self, variable: str) -> List[Production]:
        return [p for p in self.productions if p.head == variable]

    def add_production(self, head: str, body: Tuple[str, ...]) -> None:
        prod = Production(head, body)
        if prod not in self.productions:
            self.productions.append(prod)
            self.variables.add(head)

    def clone(self) -> 'CFG':
        return CFG(
            variables=set(self.variables),
            terminals=set(self.terminals),
            productions=[Production(p.head, p.clean_body) for p in self.productions],
            start_symbol=self.start_symbol
        )

    def to_text(self) -> str:
        """Export grammar rules to readable string representation."""
        grouped: Dict[str, List[str]] = {}
        for p in self.productions:
            rhs = " ".join(p.clean_body) if p.clean_body else EPSILON
            grouped.setdefault(p.head, []).append(rhs)
        
        lines = []
        # Print start symbol first
        if self.start_symbol in grouped:
            lines.append(f"{self.start_symbol} -> " + " | ".join(grouped[self.start_symbol]))
        for head, bodies in sorted(grouped.items()):
            if head != self.start_symbol:
                lines.append(f"{head} -> " + " | ".join(bodies))
        return "\n".join(lines)

    def tokenize_input(self, text: str) -> Optional[List[str]]:
        """
        Tokenize a target string against the grammar's terminal set.
        Returns a list of terminal tokens, or None if the string contains symbols
        that cannot be tokenized using the terminal set.
        Handles epsilon: empty text or 'ε' / 'epsilon' -> []
        """
        stripped = text.strip()
        if not stripped or stripped in EPSILON_ALIASES:
            return []

        # If user provided spaces between tokens, check if split works
        space_split = [tok for tok in stripped.split() if tok]
        if all(tok in self.terminals for tok in space_split):
            return space_split

        # Otherwise, perform greedy longest-match tokenization based on self.terminals
        sorted_terminals = sorted(self.terminals, key=len, reverse=True)
        tokens = []
        idx = 0
        s = stripped.replace(" ", "")  # disregard whitespace if continuous
        while idx < len(s):
            matched = False
            for term in sorted_terminals:
                if s.startswith(term, idx):
                    tokens.append(term)
                    idx += len(term)
                    matched = True
                    break
            if not matched:
                return None
        return tokens

    @classmethod
    def from_text(
        cls,
        text: str,
        start_symbol: Optional[str] = None,
        custom_terminals: Optional[Set[str]] = None,
        custom_variables: Optional[Set[str]] = None
    ) -> 'CFG':
        """
        Parse user-entered grammar text.
        Format example:
          S -> a S b | epsilon
          A -> a | B
        """
        lines = [line.strip() for line in text.strip().splitlines() if line.strip() and not line.strip().startswith("#")]
        if not lines:
            raise ValueError("Grammar input is empty.")

        productions: List[Production] = []
        raw_variables: Set[str] = set()
        first_head: Optional[str] = None

        # First pass: collect heads and raw rules
        rule_specs = []
        for line in lines:
            if "->" in line:
                head, rhs = line.split("->", 1)
            elif ":" in line:
                head, rhs = line.split(":", 1)
            elif "::=" in line:
                head, rhs = line.split("::=", 1)
            else:
                raise ValueError(f"Invalid rule format on line: '{line}'. Expected '->' or '::='.")
            
            head = head.strip()
            if not head:
                raise ValueError(f"Missing LHS variable in line: '{line}'.")
            if first_head is None:
                first_head = head
            raw_variables.add(head)

            alternatives = [alt.strip() for alt in rhs.split("|")]
            rule_specs.append((head, alternatives))

        inferred_start = start_symbol.strip() if start_symbol and start_symbol.strip() else first_head

        # Determine terminal candidate symbols
        # Terminals are symbols that are not in variables and not epsilon
        inferred_terminals = set(custom_terminals) if custom_terminals else set()
        inferred_variables = set(custom_variables) if custom_variables else set(raw_variables)

        for head, alternatives in rule_specs:
            for alt in alternatives:
                if alt in EPSILON_ALIASES:
                    productions.append(Production(head, ()))
                    continue

                # Tokenize RHS
                # If space separated:
                tokens = [t for t in alt.split() if t]
                if not tokens:
                    productions.append(Production(head, ()))
                    continue

                # If tokens are given with spaces
                if len(tokens) > 1 or any(t in inferred_variables or t in EPSILON_ALIASES for t in tokens):
                    clean_tokens = []
                    for t in tokens:
                        if t in EPSILON_ALIASES:
                            continue
                        clean_tokens.append(t)
                        if t not in inferred_variables:
                            inferred_terminals.add(t)
                    productions.append(Production(head, tuple(clean_tokens)))
                else:
                    # Single chunk like 'aSb', 'aabb', or 'id'
                    chunk = tokens[0]
                    # Check if chunk contains any defined variable
                    has_var = any(v in chunk for v in inferred_variables)
                    if not has_var and (chunk in inferred_terminals or chunk.isidentifier() or len(chunk) == 1):
                        # Multi-char or single-char terminal token (e.g. 'id', '+', 'a')
                        clean_tokens = [chunk]
                        inferred_terminals.add(chunk)
                    else:
                        # Tokenize chunk: match variables first, then 1-char terminals
                        clean_tokens = []
                        i = 0
                        while i < len(chunk):
                            var_match = None
                            for v in sorted(inferred_variables, key=len, reverse=True):
                                if chunk.startswith(v, i):
                                    var_match = v
                                    break
                            if var_match:
                                clean_tokens.append(var_match)
                                i += len(var_match)
                            else:
                                char = chunk[i]
                                clean_tokens.append(char)
                                inferred_terminals.add(char)
                                i += 1
                    productions.append(Production(head, tuple(clean_tokens)))

        return cls(
            variables=inferred_variables,
            terminals=inferred_terminals,
            productions=productions,
            start_symbol=inferred_start
        )


def get_predefined_grammars() -> Dict[str, Dict]:
    """Return catalog of educational predefined grammars."""
    return {
        "G1: Balanced anbn": {
            "name": "Balanced strings a^n b^n (n >= 0)",
            "description": "Context-free language L = { a^n b^n | n ≥ 0 }. Generates ε, ab, aabb, aaabbb, ...",
            "text": "S -> a S b | ε",
            "start_symbol": "S",
            "terminals": {"a", "b"},
            "example_strings": ["", "ab", "aabb", "aaabbb"],
            "rejected_strings": ["a", "b", "aab", "abb", "abab"]
        },
        "G2: Palindromes": {
            "name": "Palindromes over {a, b}",
            "description": "All symmetric strings over {a, b}. Generates ε, a, b, aa, bb, aba, abba, ...",
            "text": "S -> a S a | b S b | a | b | ε",
            "start_symbol": "S",
            "terminals": {"a", "b"},
            "example_strings": ["", "a", "b", "aa", "aba", "abba"],
            "rejected_strings": ["ab", "ba", "aab", "abb"]
        },
        "G3: Arithmetic Expressions": {
            "name": "Simple Arithmetic Expressions",
            "description": "Expressions with precedence: * over +, parentheses, and identifier 'id'.",
            "text": "E -> E + T | T\nT -> T * F | F\nF -> ( E ) | id",
            "start_symbol": "E",
            "terminals": {"+", "*", "(", ")", "id"},
            "example_strings": ["id", "id + id", "id * id", "( id + id ) * id"],
            "rejected_strings": ["id +", "+ id", "id *", "( id", "id id"]
        },
        "G4: Balanced Parentheses": {
            "name": "Dyck Language (Balanced Parentheses)",
            "description": "Well-nested matching parentheses: ε, (), (()), ()()",
            "text": "S -> ( S ) S | ε",
            "start_symbol": "S",
            "terminals": {"(", ")"},
            "example_strings": ["", "()", "(())", "()()", "((()))"],
            "rejected_strings": ["(", ")", ")(", "(()", "())"]
        },
        "G5: Equal a and b": {
            "name": "Equal count of a's and b's",
            "description": "Strings where count of 'a' equals count of 'b': ε, ab, ba, abba, baab",
            "text": "S -> a S b S | b S a S | ε",
            "start_symbol": "S",
            "terminals": {"a", "b"},
            "example_strings": ["", "ab", "ba", "aabb", "abab", "baab"],
            "rejected_strings": ["a", "b", "aab", "abb", "aaabb"]
        }
    }
