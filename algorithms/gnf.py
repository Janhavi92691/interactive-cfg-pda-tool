"""
Greibach Normal Form (GNF) Conversion Pipeline and Validator.
"""

from typing import List, Set, Tuple, Dict, Optional, Any
from .grammar import CFG, Production, EPSILON
from .cnf import convert_to_cnf


class GNFStage:
    """Represents a stage in the GNF conversion pipeline."""
    def __init__(self, stage_name: str, description: str, grammar: CFG, details: Optional[Dict[str, Any]] = None):
        self.stage_name = stage_name
        self.description = description
        self.grammar = grammar
        self.details = details or {}


def is_in_gnf(grammar: CFG) -> Tuple[bool, List[str]]:
    """
    Validates whether a grammar is in Greibach Normal Form.
    Every production must be of the form:
      A -> a α
    where a in Terminals and α in Variables* (zero or more variables),
    with the sole exception of S_0 -> ε (if S_0 is start symbol and does not appear on RHS).
    """
    violations: List[str] = []

    for p in grammar.productions:
        if p.is_epsilon:
            if p.head != grammar.start_symbol:
                violations.append(f"Illegal ε-rule '{p}': only start symbol may derive ε in GNF.")
            continue

        body = p.clean_body
        if not body:
            continue

        first_sym = body[0]
        rest = body[1:]

        if first_sym not in grammar.terminals:
            violations.append(f"Rule '{p}' does not start with a terminal symbol ('{first_sym}' is not in terminals).")

        for sym in rest:
            if sym not in grammar.variables:
                violations.append(f"Rule '{p}' has non-variable symbol '{sym}' following the leading terminal.")

    return (len(violations) == 0, violations)


def convert_to_gnf(original_grammar: CFG, max_substitutions: int = 200) -> Tuple[CFG, List[GNFStage]]:
    """
    Convert CFG to Greibach Normal Form using standard CNF-based transformation.
    Steps:
      1. CNF Preprocessing (ensures ε-free/unit-free, binarized).
      2. Ordering Variables A_1 ... A_m.
      3. Forward substitution to ensure for A_i -> A_j γ, j > i.
      4. Left-recursion elimination via auxiliary variables Z_i.
      5. Backward substitution (from A_m down to A_1).
      6. Substitution into auxiliary Z variables.
    """
    stages: List[GNFStage] = []

    # Step 1: Preprocess via CNF
    cnf_grammar, _ = convert_to_cnf(original_grammar)
    stages.append(GNFStage(
        stage_name="Stage 1: CNF Preprocessing",
        description="Grammar preprocessed into CNF (unit-free, ε-free, binarized) as standard starting point.",
        grammar=cnf_grammar.clone()
    ))

    g = cnf_grammar.clone()
    epsilon_start_prod = [p for p in g.productions if p.is_epsilon and p.head == g.start_symbol]

    # Filter out epsilon production during the core transformation
    g.productions = [p for p in g.productions if not p.is_epsilon]

    # Step 2: Establish variable ordering
    # Ensure start symbol is first
    vars_list = [g.start_symbol] + [v for v in sorted(g.variables) if v != g.start_symbol]
    var_indices = {v: i for i, v in enumerate(vars_list)}

    stages.append(GNFStage(
        stage_name="Stage 2: Variable Ordering",
        description=f"Assigned linear ordering to variables: {', '.join(vars_list)}",
        grammar=g.clone(),
        details={"ordering": vars_list}
    ))

    # Helper to get productions for head
    def get_rules(head: str, prods: List[Production]) -> List[Production]:
        return [p for p in prods if p.head == head]

    current_prods = list(g.productions)
    z_variables: Set[str] = set()

    # Step 3: Forward substitution and Left-Recursion Elimination
    for i, Ai in enumerate(vars_list):
        # Substitute A_j into A_i if j < i
        substituted = True
        sub_count = 0
        while substituted and sub_count < max_substitutions:
            substituted = False
            sub_count += 1
            new_list: List[Production] = []
            for p in current_prods:
                if p.head == Ai and len(p.clean_body) > 0:
                    first = p.clean_body[0]
                    if first in var_indices and var_indices[first] < i:
                        # Substitute first variable
                        Aj = first
                        gamma = p.clean_body[1:]
                        for aj_prod in get_rules(Aj, current_prods):
                            new_body = aj_prod.clean_body + gamma
                            new_prod = Production(Ai, new_body)
                            if new_prod not in new_list:
                                new_list.append(new_prod)
                        substituted = True
                    else:
                        new_list.append(p)
                else:
                    new_list.append(p)
            current_prods = new_list

        # Now eliminate immediate left recursion on Ai: Ai -> Ai alpha
        # Separate into recursive: Ai -> Ai alpha, and non-recursive: Ai -> beta
        alphas: List[Tuple[str, ...]] = []
        betas: List[Tuple[str, ...]] = []

        other_prods: List[Production] = []
        for p in current_prods:
            if p.head == Ai:
                if len(p.clean_body) > 0 and p.clean_body[0] == Ai:
                    alphas.append(p.clean_body[1:])
                else:
                    betas.append(p.clean_body)
            else:
                other_prods.append(p)

        if alphas:
            # Introduce new variable Zi
            Zi = f"Z_{Ai}"
            c = 0
            while Zi in g.variables or Zi in g.terminals or Zi in z_variables:
                c += 1
                Zi = f"Z_{Ai}_{c}"
            z_variables.add(Zi)
            g.variables.add(Zi)

            ai_new_prods: List[Production] = []
            for beta in betas:
                ai_new_prods.append(Production(Ai, beta))
                ai_new_prods.append(Production(Ai, beta + (Zi,)))

            zi_new_prods: List[Production] = []
            for alpha in alphas:
                zi_new_prods.append(Production(Zi, alpha))
                zi_new_prods.append(Production(Zi, alpha + (Zi,)))

            current_prods = other_prods + ai_new_prods + zi_new_prods

    g.productions = current_prods
    stages.append(GNFStage(
        stage_name="Stage 3: Forward Substitution & Left-Recursion Elimination",
        description="Eliminated left-recursion and ensured for A_i -> A_j γ, j > i.",
        grammar=g.clone(),
        details={"auxiliary_variables": list(z_variables)}
    ))

    # Step 4: Backward substitution from A_m down to A_1
    for i in range(len(vars_list) - 1, -1, -1):
        Ai = vars_list[i]
        # While any production of Ai starts with a variable Aj (where j > i), substitute
        changed = True
        sub_count = 0
        while changed and sub_count < max_substitutions:
            changed = False
            sub_count += 1
            new_list = []
            for p in current_prods:
                if p.head == Ai and len(p.clean_body) > 0 and p.clean_body[0] in var_indices:
                    Aj = p.clean_body[0]
                    gamma = p.clean_body[1:]
                    for aj_prod in get_rules(Aj, current_prods):
                        new_body = aj_prod.clean_body + gamma
                        new_prod = Production(Ai, new_body)
                        if new_prod not in new_list:
                            new_list.append(new_prod)
                    changed = True
                else:
                    new_list.append(p)
            current_prods = new_list

    g.productions = current_prods
    stages.append(GNFStage(
        stage_name="Stage 4: Backward Substitution",
        description="Substituted variable prefixes from A_m down to A_1 so all original variables begin with terminals.",
        grammar=g.clone()
    ))

    # Step 5: Substitute into auxiliary Z variables
    changed = True
    sub_count = 0
    while changed and sub_count < max_substitutions:
        changed = False
        sub_count += 1
        new_list = []
        for p in current_prods:
            if p.head in z_variables and len(p.clean_body) > 0 and p.clean_body[0] in g.variables:
                lead_var = p.clean_body[0]
                gamma = p.clean_body[1:]
                for lead_prod in get_rules(lead_var, current_prods):
                    new_body = lead_prod.clean_body + gamma
                    new_prod = Production(p.head, new_body)
                    if new_prod not in new_list:
                        new_list.append(new_prod)
                changed = True
            else:
                new_list.append(p)
        current_prods = new_list

    # Re-insert epsilon start production if language accepts empty string
    if epsilon_start_prod:
        current_prods.insert(0, epsilon_start_prod[0])

    # Remove any unreferenced or duplicate rules
    seen_all: Set[Tuple[str, Tuple[str, ...]]] = set()
    final_prods: List[Production] = []
    for p in current_prods:
        key = (p.head, p.clean_body)
        if key not in seen_all:
            seen_all.add(key)
            final_prods.append(p)

    g.productions = final_prods
    stages.append(GNFStage(
        stage_name="Stage 5: Auxiliary Variable Normalization (Final GNF)",
        description="All productions normalized to begin with a terminal symbol followed by non-terminals.",
        grammar=g.clone()
    ))

    return g, stages
