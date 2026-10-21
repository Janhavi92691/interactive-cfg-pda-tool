"""
Chomsky Normal Form (CNF) Conversion Pipeline and Validator.
"""

from typing import List, Set, Tuple, Dict, Optional, Any
from itertools import product
from .grammar import CFG, Production, EPSILON


class CNFStage:
    """Records the state and explanation of an intermediate CNF stage."""
    def __init__(self, stage_name: str, description: str, grammar: CFG, details: Optional[Dict[str, Any]] = None):
        self.stage_name = stage_name
        self.description = description
        self.grammar = grammar
        self.details = details or {}


def is_in_cnf(grammar: CFG) -> Tuple[bool, List[str]]:
    """
    Validates whether a grammar strictly complies with Chomsky Normal Form.
    Allowed production shapes:
      1. A -> B C  (where B, C are variables and neither is S_0 if S_0 -> ε exists)
      2. A -> a    (where a is a single terminal)
      3. S_0 -> ε  (allowed ONLY for start symbol S_0, and S_0 must not appear on any RHS)
    """
    violations: List[str] = []

    has_epsilon_start = any(
        p.head == grammar.start_symbol and p.is_epsilon for p in grammar.productions
    )

    # Check if start symbol appears on RHS if epsilon is allowed
    if has_epsilon_start:
        for p in grammar.productions:
            if grammar.start_symbol in p.clean_body:
                violations.append(
                    f"Start symbol '{grammar.start_symbol}' appears on RHS of rule '{p}', which is forbidden in CNF when start derives ε."
                )

    for p in grammar.productions:
        head = p.head
        body = p.clean_body

        if p.is_epsilon:
            if head != grammar.start_symbol:
                violations.append(f"Illegal ε-production '{p}': only the start symbol may derive ε in CNF.")
            continue

        if len(body) == 1:
            # Must be a single terminal
            sym = body[0]
            if sym not in grammar.terminals:
                violations.append(f"Unit or non-terminal rule '{p}': RHS must be a terminal in CNF.")
        elif len(body) == 2:
            # Must be two variables
            sym1, sym2 = body[0], body[1]
            if sym1 not in grammar.variables or sym2 not in grammar.variables:
                violations.append(f"Mixed/terminal rule '{p}': RHS of length 2 must consist purely of two variables.")
        else:
            violations.append(f"Long rule '{p}': RHS length {len(body)} > 2 violates CNF binarization.")

    return (len(violations) == 0, violations)


def convert_to_cnf(original_grammar: CFG) -> Tuple[CFG, List[CNFStage]]:
    """
    Convert CFG to Chomsky Normal Form preserving language equivalence.
    Returns:
      (final_cnf_grammar, list of CNFStage objects detailing each step)
    """
    stages: List[CNFStage] = []
    g = original_grammar.clone()

    stages.append(CNFStage(
        stage_name="Stage 0: Original Grammar",
        description="Initial grammar entered by the user.",
        grammar=g.clone()
    ))

    # -------------------------------------------------------------
    # Step 1: Add new start symbol S0 -> S
    # -------------------------------------------------------------
    # Check if start symbol appears on RHS of any production
    start_on_rhs = any(g.start_symbol in p.clean_body for p in g.productions)
    old_start = g.start_symbol
    new_start = old_start

    if start_on_rhs:
        new_start = f"{old_start}_0"
        counter = 0
        while new_start in g.variables or new_start in g.terminals:
            counter += 1
            new_start = f"{old_start}_{counter}"

        g.variables.add(new_start)
        # Add new start rule at the beginning
        g.productions.insert(0, Production(new_start, (old_start,)))
        g.start_symbol = new_start
        step1_desc = f"Start symbol '{old_start}' appears on RHS. Added new start symbol '{new_start}' with rule '{new_start} -> {old_start}'."
    else:
        step1_desc = f"Start symbol '{old_start}' does not appear on any RHS. No new start symbol required."

    stages.append(CNFStage(
        stage_name="Stage 1: Start Symbol Isolation",
        description=step1_desc,
        grammar=g.clone(),
        details={"old_start": old_start, "new_start": g.start_symbol}
    ))

    # -------------------------------------------------------------
    # Step 2: Eliminate Epsilon (ε) Productions
    # -------------------------------------------------------------
    # A) Find all nullable variables
    nullable: Set[str] = set()
    changed = True
    while changed:
        changed = False
        for p in g.productions:
            if p.head not in nullable:
                if p.is_epsilon or all(sym in nullable for sym in p.clean_body):
                    nullable.add(p.head)
                    changed = True

    is_epsilon_in_lang = (old_start in nullable) or (g.start_symbol in nullable)

    # B) Generate new productions without epsilon
    new_productions: List[Production] = []
    seen_prods: Set[Tuple[str, Tuple[str, ...]]] = set()

    for p in g.productions:
        if p.is_epsilon:
            continue  # drop explicit epsilon rules for now

        # Identify indices of nullable variables in body
        nullable_indices = [i for i, sym in enumerate(p.clean_body) if sym in nullable]

        # Generate combinations (subsets of nullable variables to drop or keep)
        # Each index can be kept (True) or dropped (False)
        combinations = list(product([True, False], repeat=len(nullable_indices)))

        for combo in combinations:
            # Construct new body
            drop_indices = {nullable_indices[idx] for idx, keep in enumerate(combo) if not keep}
            new_body = tuple(sym for i, sym in enumerate(p.clean_body) if i not in drop_indices)

            if new_body:  # Non-empty body
                key = (p.head, new_body)
                if key not in seen_prods:
                    seen_prods.add(key)
                    new_productions.append(Production(p.head, new_body))

    # C) If epsilon is in language, allow S0 -> ε
    if is_epsilon_in_lang:
        # If start symbol wasn't isolated in step 1, isolate it now so S0 -> ε is valid CNF
        if g.start_symbol == old_start and start_on_rhs:
            # Already handled in step 1
            pass
        elif any(g.start_symbol in p.clean_body for p in new_productions):
            isolated_start = f"{g.start_symbol}_0"
            counter = 0
            while isolated_start in g.variables or isolated_start in g.terminals:
                counter += 1
                isolated_start = f"{g.start_symbol}_{counter}"
            new_productions.insert(0, Production(isolated_start, (g.start_symbol,)))
            g.variables.add(isolated_start)
            g.start_symbol = isolated_start

        eps_prod = Production(g.start_symbol, ())
        if (g.start_symbol, ()) not in seen_prods:
            new_productions.insert(0, eps_prod)

    g.productions = new_productions
    stages.append(CNFStage(
        stage_name="Stage 2: Elimination of ε-Productions",
        description=f"Identified nullable variables: {sorted(nullable)}. Substituted combinations of nullable variables and eliminated non-start ε-rules.",
        grammar=g.clone(),
        details={"nullable_variables": list(nullable), "epsilon_in_language": is_epsilon_in_lang}
    ))

    # -------------------------------------------------------------
    # Step 3: Eliminate Unit Productions (A -> B where B in Variables)
    # -------------------------------------------------------------
    # Find unit pairs (A, B) such that A =>* B using only unit rules
    unit_pairs: Dict[str, Set[str]] = {v: {v} for v in g.variables}

    for v in g.variables:
        queue = [v]
        visited = {v}
        while queue:
            curr = queue.pop(0)
            for p in g.productions:
                if p.head == curr and len(p.clean_body) == 1 and p.clean_body[0] in g.variables:
                    target = p.clean_body[0]
                    if target not in visited:
                        visited.add(target)
                        queue.append(target)
                        unit_pairs[v].add(target)

    # For each A, and each B in unit_pairs[A], add non-unit productions of B
    unit_elim_productions: List[Production] = []
    seen_unit_prods: Set[Tuple[str, Tuple[str, ...]]] = set()

    # Preserve start -> ε if present
    for p in g.productions:
        if p.is_epsilon and p.head == g.start_symbol:
            unit_elim_productions.append(p)
            seen_unit_prods.add((p.head, ()))

    for A in g.variables:
        for B in unit_pairs.get(A, set()):
            for p in g.productions:
                if p.head == B:
                    # If p is non-unit production
                    is_unit = len(p.clean_body) == 1 and p.clean_body[0] in g.variables
                    if not is_unit and not p.is_epsilon:
                        key = (A, p.clean_body)
                        if key not in seen_unit_prods:
                            seen_unit_prods.add(key)
                            unit_elim_productions.append(Production(A, p.clean_body))

    g.productions = unit_elim_productions
    stages.append(CNFStage(
        stage_name="Stage 3: Elimination of Unit Productions",
        description="Computed unit pairs A =>* B and replaced unit rules with corresponding target derivations.",
        grammar=g.clone(),
        details={"unit_pairs": {k: sorted(v) for k, v in unit_pairs.items() if len(v) > 1}}
    ))

    # -------------------------------------------------------------
    # Step 4: Removal of Useless and Unreachable Symbols
    # -------------------------------------------------------------
    # 4a) Productive / generating symbols
    generating: Set[str] = set()
    changed = True
    while changed:
        changed = False
        for p in g.productions:
            if p.head not in generating:
                if p.is_epsilon or all(sym in g.terminals or sym in generating for sym in p.clean_body):
                    generating.add(p.head)
                    changed = True

    # Retain start symbol if it has epsilon
    if any(p.head == g.start_symbol and p.is_epsilon for p in g.productions):
        generating.add(g.start_symbol)

    g.variables = g.variables.intersection(generating)
    g.productions = [
        p for p in g.productions
        if p.head in generating and all(sym in g.terminals or sym in generating for sym in p.clean_body)
    ]

    # 4b) Reachable symbols
    reachable: Set[str] = {g.start_symbol}
    changed = True
    while changed:
        changed = False
        for p in g.productions:
            if p.head in reachable:
                for sym in p.clean_body:
                    if sym not in reachable:
                        reachable.add(sym)
                        changed = True

    g.variables = g.variables.intersection(reachable)
    g.terminals = g.terminals.intersection(reachable)
    g.productions = [
        p for p in g.productions
        if p.head in reachable and all(sym in reachable for sym in p.clean_body)
    ]

    stages.append(CNFStage(
        stage_name="Stage 4: Elimination of Useless & Unreachable Symbols",
        description="Removed non-generating variables and variables/terminals not reachable from the start symbol.",
        grammar=g.clone(),
        details={"generating_vars": list(generating), "reachable_symbols": list(reachable)}
    ))

    # -------------------------------------------------------------
    # Step 5: Replace Terminals in Mixed / Long Productions (length >= 2)
    # -------------------------------------------------------------
    # Check which terminals appear in bodies of length >= 2
    terminals_to_replace: Set[str] = set()
    for p in g.productions:
        if len(p.clean_body) >= 2:
            for sym in p.clean_body:
                if sym in g.terminals:
                    terminals_to_replace.add(sym)

    terminal_var_map: Dict[str, str] = {}
    term_productions: List[Production] = []

    for term in sorted(terminals_to_replace):
        # Generate safe new variable name
        safe_name = f"T_{term}" if term.isalnum() else f"T_sym_{abs(hash(term)) % 1000}"
        counter = 0
        cand_name = safe_name
        while cand_name in g.variables or cand_name in g.terminals:
            counter += 1
            cand_name = f"{safe_name}_{counter}"
        
        terminal_var_map[term] = cand_name
        g.variables.add(cand_name)
        term_productions.append(Production(cand_name, (term,)))

    replaced_productions: List[Production] = []
    for p in g.productions:
        if len(p.clean_body) >= 2:
            new_body = tuple(terminal_var_map.get(sym, sym) for sym in p.clean_body)
            replaced_productions.append(Production(p.head, new_body))
        else:
            replaced_productions.append(p)

    g.productions = replaced_productions + term_productions
    stages.append(CNFStage(
        stage_name="Stage 5: Terminal Substitution in Long Productions",
        description="Replaced terminals appearing in RHS of length >= 2 with dedicated non-terminals (e.g. T_a -> a).",
        grammar=g.clone(),
        details={"terminal_map": terminal_var_map}
    ))

    # -------------------------------------------------------------
    # Step 6: Binarization of Productions with Length > 2
    # -------------------------------------------------------------
    binarized_productions: List[Production] = []
    cascade_counter = 1

    for p in g.productions:
        body = p.clean_body
        if len(body) <= 2:
            binarized_productions.append(p)
        else:
            # Binarize: A -> X1 X2 X3 ... Xk
            current_head = p.head
            for i in range(len(body) - 2):
                new_var = f"C_{cascade_counter}"
                cascade_counter += 1
                while new_var in g.variables or new_var in g.terminals:
                    new_var = f"C_{cascade_counter}"
                    cascade_counter += 1

                g.variables.add(new_var)
                binarized_productions.append(Production(current_head, (body[i], new_var)))
                current_head = new_var
            # Final pair
            binarized_productions.append(Production(current_head, (body[-2], body[-1])))

    g.productions = binarized_productions
    stages.append(CNFStage(
        stage_name="Stage 6: Binarization (Final CNF)",
        description="Binarized all productions with RHS length > 2 using intermediate cascading variables.",
        grammar=g.clone()
    ))

    return g, stages
