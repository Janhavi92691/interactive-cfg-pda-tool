"""
Pushdown Automaton (PDA) Formal Representation, Simulator, and Graphviz Renderer.
"""

from typing import List, Set, Tuple, Dict, Optional, Any
from collections import deque
from .grammar import EPSILON, EPSILON_ALIASES


class PDATransition:
    """Represents a transition δ(from_state, input_sym, pop_sym) -> (to_state, push_string)."""
    def __init__(
        self,
        from_state: str,
        input_symbol: str,   # terminal or EPSILON
        pop_symbol: str,     # stack symbol to pop
        to_state: str,
        push_symbols: Tuple[str, ...]  # tuple of stack symbols pushed (first is new stack top, () is pop)
    ):
        self.from_state = from_state.strip()
        self.input_symbol = EPSILON if input_symbol in EPSILON_ALIASES or not input_symbol else input_symbol.strip()
        self.pop_symbol = pop_symbol.strip()
        self.to_state = to_state.strip()
        self.push_symbols = tuple(
            s.strip() for s in push_symbols
            if s.strip() and s.strip() not in EPSILON_ALIASES
        )

    @property
    def push_str(self) -> str:
        return "".join(self.push_symbols) if self.push_symbols else EPSILON

    def __repr__(self) -> str:
        return f"δ({self.from_state}, {self.input_symbol}, {self.pop_symbol}) -> ({self.to_state}, {self.push_str})"

    def label(self) -> str:
        return f"{self.input_symbol}, {self.pop_symbol} → {self.push_str}"


class PDASimulationStep:
    """Records one step in a PDA simulation trace."""
    def __init__(
        self,
        step_number: int,
        state: str,
        remaining_input: List[str],
        stack_before: Tuple[str, ...],
        transition_applied: Optional[PDATransition],
        stack_after: Tuple[str, ...],
        explanation: str
    ):
        self.step_number = step_number
        self.state = state
        self.remaining_input = remaining_input
        self.stack_before = stack_before
        self.transition_applied = transition_applied
        self.stack_after = stack_after
        self.explanation = explanation

    def stack_before_str(self) -> str:
        if not self.stack_before:
            return "[EMPTY]"
        return "[TOP] " + " | ".join(self.stack_before)

    def stack_after_str(self) -> str:
        if not self.stack_after:
            return "[EMPTY]"
        return "[TOP] " + " | ".join(self.stack_after)

    def input_str(self) -> str:
        return "".join(self.remaining_input) if self.remaining_input else EPSILON


class PDA:
    """
    Formal 7-tuple: M = (Q, Σ, Γ, δ, q0, Z0, F)
      Q: States
      Σ: Input alphabet
      Γ: Stack alphabet
      δ: Transitions list
      q0: Initial state
      Z0: Start stack symbol
      F: Accepting states
      acceptance_mode: 'final_state', 'empty_stack', or 'both'
    """
    def __init__(
        self,
        name: str,
        states: Set[str],
        input_alphabet: Set[str],
        stack_alphabet: Set[str],
        transitions: List[PDATransition],
        start_state: str,
        initial_stack_symbol: str,
        accepting_states: Set[str],
        acceptance_mode: str = "final_state",
        description: str = ""
    ):
        self.name = name
        self.states = set(states)
        self.input_alphabet = set(input_alphabet)
        self.stack_alphabet = set(stack_alphabet)
        self.transitions = transitions
        self.start_state = start_state
        self.initial_stack_symbol = initial_stack_symbol
        self.accepting_states = set(accepting_states)
        self.acceptance_mode = acceptance_mode  # 'final_state', 'empty_stack', 'both'
        self.description = description

    def is_configuration_accepting(self, state: str, remaining_input: List[str], stack: Tuple[str, ...]) -> bool:
        if remaining_input:
            return False  # Input must be completely consumed

        if self.acceptance_mode == "final_state":
            return state in self.accepting_states
        elif self.acceptance_mode == "empty_stack":
            return len(stack) == 0
        elif self.acceptance_mode == "both":
            return state in self.accepting_states and len(stack) == 0
        return False

    def simulate(
        self,
        input_tokens: List[str],
        max_depth: int = 40,
        max_explored: int = 2000
    ) -> Tuple[bool, List[PDASimulationStep], str]:
        """
        Simulate the PDA on the input string using BFS to handle non-determinism.
        Returns: (is_accepted, trace_steps, explanation)
        """
        # Validate input tokens
        invalid_symbols = [t for t in input_tokens if t not in self.input_alphabet]
        if invalid_symbols:
            return False, [], f"Input contains symbol(s) not in input alphabet Σ: {invalid_symbols}"

        # Configuration: (state, input_tuple, stack_tuple, trace)
        initial_stack = (self.initial_stack_symbol,)
        initial_input = tuple(input_tokens)

        # Check if already accepting at step 0
        if self.is_configuration_accepting(self.start_state, list(initial_input), initial_stack):
            step0 = PDASimulationStep(
                step_number=0,
                state=self.start_state,
                remaining_input=list(initial_input),
                stack_before=initial_stack,
                transition_applied=None,
                stack_after=initial_stack,
                explanation="Initial configuration satisfies acceptance condition directly."
            )
            return True, [step0], f"ACCEPTED: Initial state '{self.start_state}' is accepting for empty input."

        queue = deque([(self.start_state, initial_input, initial_stack, [])])
        # Visited configurations to prevent infinite loops: (state, remaining_input, stack)
        visited: Set[Tuple[str, Tuple[str, ...], Tuple[str, ...]]] = set()
        visited.add((self.start_state, initial_input, initial_stack))

        nodes_explored = 0
        closest_trace: List[PDASimulationStep] = []
        best_input_consumed = 0

        while queue and nodes_explored < max_explored:
            nodes_explored += 1
            curr_state, curr_input, curr_stack, trace = queue.popleft()

            # Keep track of best partial trace for educational diagnostics
            consumed_count = len(input_tokens) - len(curr_input)
            if consumed_count >= best_input_consumed and len(trace) > len(closest_trace):
                best_input_consumed = consumed_count
                closest_trace = trace

            if len(trace) > max_depth:
                continue

            # Check if this configuration accepts
            if self.is_configuration_accepting(curr_state, list(curr_input), curr_stack):
                # We found an accepting computation path!
                full_steps = []
                # Reconstruct step-by-step
                recon_stack = initial_stack
                recon_input = list(initial_input)

                full_steps.append(PDASimulationStep(
                    step_number=0,
                    state=self.start_state,
                    remaining_input=list(recon_input),
                    stack_before=recon_stack,
                    transition_applied=None,
                    stack_after=recon_stack,
                    explanation=f"Initial configuration in state '{self.start_state}' with stack symbol '{self.initial_stack_symbol}'."
                ))

                for i, (prev_state, trans, next_state, next_stk, next_inp) in enumerate(trace, 1):
                    read_txt = f"read '{trans.input_symbol}'" if trans.input_symbol != EPSILON else "ε-transition"
                    push_txt = f"pushed '{trans.push_str}'" if trans.push_symbols else f"popped '{trans.pop_symbol}'"
                    full_steps.append(PDASimulationStep(
                        step_number=i,
                        state=next_state,
                        remaining_input=list(next_inp),
                        stack_before=recon_stack,
                        transition_applied=trans,
                        stack_after=next_stk,
                        explanation=f"Applied {trans}: {read_txt}, {push_txt}, moved to state '{next_state}'."
                    ))
                    recon_stack = next_stk
                    recon_input = list(next_inp)

                return True, full_steps, f"ACCEPTED: Found valid accepting path in {len(trace)} transitions ({nodes_explored} configurations explored)."

            # Explore valid outgoing transitions from curr_state
            if not curr_stack:
                # Stack is empty, cannot pop anything
                continue

            stack_top = curr_stack[0]

            for trans in self.transitions:
                if trans.from_state != curr_state or trans.pop_symbol != stack_top:
                    continue

                # Case A: Epsilon transition (reads no input)
                if trans.input_symbol == EPSILON:
                    new_stack = trans.push_symbols + curr_stack[1:]
                    new_config = (trans.to_state, curr_input, new_stack)
                    if new_config not in visited:
                        visited.add(new_config)
                        new_trace = trace + [(curr_state, trans, trans.to_state, new_stack, curr_input)]
                        queue.append((trans.to_state, curr_input, new_stack, new_trace))

                # Case B: Consumes current input symbol
                elif curr_input and trans.input_symbol == curr_input[0]:
                    next_input = curr_input[1:]
                    new_stack = trans.push_symbols + curr_stack[1:]
                    new_config = (trans.to_state, next_input, new_stack)
                    if new_config not in visited:
                        visited.add(new_config)
                        new_trace = trace + [(curr_state, trans, trans.to_state, new_stack, next_input)]
                        queue.append((trans.to_state, next_input, new_stack, new_trace))

        # Reconstruct rejection steps from the longest attempted path
        rejected_steps = []
        recon_stack = initial_stack
        recon_input = list(initial_input)
        rejected_steps.append(PDASimulationStep(
            step_number=0,
            state=self.start_state,
            remaining_input=list(recon_input),
            stack_before=recon_stack,
            transition_applied=None,
            stack_after=recon_stack,
            explanation=f"Started at state '{self.start_state}'."
        ))

        for i, (prev_state, trans, next_state, next_stk, next_inp) in enumerate(closest_trace, 1):
            read_txt = f"read '{trans.input_symbol}'" if trans.input_symbol != EPSILON else "ε-transition"
            push_txt = f"pushed '{trans.push_str}'" if trans.push_symbols else f"popped '{trans.pop_symbol}'"
            rejected_steps.append(PDASimulationStep(
                step_number=i,
                state=next_state,
                remaining_input=list(next_inp),
                stack_before=recon_stack,
                transition_applied=trans,
                stack_after=next_stk,
                explanation=f"Applied {trans}: {read_txt}, {push_txt}."
            ))
            recon_stack = next_stk
            recon_input = list(next_inp)

        if nodes_explored >= max_explored:
            diag = f"REJECTED (Search Limit Reached): Explored {max_explored} configurations without reaching an accepting state. Input string may be rejected or requires a deeper exploration."
        else:
            diag = f"REJECTED: All {nodes_explored} possible transition paths halted without reaching an accepting configuration. Remaining unconsumed input: '{''.join(curr_input) if curr_input else 'none'}'."

        return False, rejected_steps, diag

    def to_dot(self, current_highlight_state: Optional[str] = None) -> str:
        """Generate Graphviz DOT source string representing the state diagram."""
        lines = [
            'digraph PDA {',
            '  rankdir=LR;',
            '  node [fontname="Arial", fontsize=12];',
            '  edge [fontname="Arial", fontsize=10];',
            '  bgcolor="transparent";',
            '  __start [shape=none, label="", width=0, height=0];'
        ]

        # Draw states
        for st in sorted(self.states):
            is_accepting = st in self.accepting_states
            shape = "doublecircle" if is_accepting else "circle"
            
            # Highlighting active state
            if current_highlight_state == st:
                style = 'style="filled,bold", fillcolor="#ffcc00", color="#d48800", penwidth=3.0, fontcolor="#000000"'
            else:
                style = 'style="filled", fillcolor="#f0f4f8", color="#2c3e50", penwidth=1.5'

            lines.append(f'  "{st}" [shape={shape}, {style}];')

        # Start arrow
        lines.append(f'  __start -> "{self.start_state}" [label="start", color="#3b82f6", penwidth=2.0];')

        # Group transitions by (from_state, to_state) to combine multiple labels nicely
        edge_labels: Dict[Tuple[str, str], List[str]] = {}
        for trans in self.transitions:
            key = (trans.from_state, trans.to_state)
            edge_labels.setdefault(key, []).append(trans.label())

        for (u, v), lbls in edge_labels.items():
            label_text = "\\n".join(lbls)
            lines.append(f'  "{u}" -> "{v}" [label="{label_text}", color="#475569"];')

        lines.append('}')
        return "\n".join(lines)


class PDASimulator:
    """Manages interactive stepping, forward/backward, and run-all state."""
    def __init__(self, pda: PDA, input_string: str):
        self.pda = pda
        self.input_string = input_string
        # Tokenize input against pda.input_alphabet
        self.tokens = list(input_string.strip()) if input_string.strip() and input_string.strip() not in EPSILON_ALIASES else []
        self.is_accepted, self.steps, self.final_message = self.pda.simulate(self.tokens)
        self.current_step_index = 0

    @property
    def total_steps(self) -> int:
        return len(self.steps)

    @property
    def current_step(self) -> Optional[PDASimulationStep]:
        if 0 <= self.current_step_index < len(self.steps):
            return self.steps[self.current_step_index]
        return None

    def step_forward(self) -> bool:
        if self.current_step_index < len(self.steps) - 1:
            self.current_step_index += 1
            return True
        return False

    def step_backward(self) -> bool:
        if self.current_step_index > 0:
            self.current_step_index -= 1
            return True
        return False

    def reset(self) -> None:
        self.current_step_index = 0

    def run_all(self) -> None:
        if self.steps:
            self.current_step_index = len(self.steps) - 1


def get_predefined_pdas() -> Dict[str, PDA]:
    """Catalog of educational Pushdown Automata."""
    pda_anbn = PDA(
        name="PDA for L = { a^n b^n | n ≥ 0 }",
        states={"q0", "q1", "q2", "q_accept"},
        input_alphabet={"a", "b"},
        stack_alphabet={"a", "Z0"},
        start_state="q0",
        initial_stack_symbol="Z0",
        accepting_states={"q_accept"},
        acceptance_mode="final_state",
        description="Pushes 'a' in state q1, pops 'a' for each 'b' in state q2, and accepts in state q_accept when stack top is Z0.",
        transitions=[
            # Epsilon input case (n = 0):
            PDATransition("q0", EPSILON, "Z0", "q_accept", ("Z0",)),
            # First 'a': transition to q1 and push 'a'
            PDATransition("q0", "a", "Z0", "q1", ("a", "Z0")),
            # In q1: continue pushing 'a'
            PDATransition("q1", "a", "a", "q1", ("a", "a")),
            # In q1: first 'b' transitions to q2 popping 'a'
            PDATransition("q1", "b", "a", "q2", ()),
            # In q2: continue popping 'a' for each 'b'
            PDATransition("q2", "b", "a", "q2", ()),
            # In q2: when all a's popped and Z0 reached, transition to q_accept
            PDATransition("q2", EPSILON, "Z0", "q_accept", ("Z0",)),
        ]
    )

    # 2. PDA for Palindromes over {a, b} of even length w w^R
    # Uses non-deterministic guess of center
    pda_wwr = PDA(
        name="Non-Deterministic PDA for Even Palindromes { w w^R }",
        states={"q_push", "q_pop", "q_accept"},
        input_alphabet={"a", "b"},
        stack_alphabet={"a", "b", "Z0"},
        start_state="q_push",
        initial_stack_symbol="Z0",
        accepting_states={"q_push", "q_accept"},
        acceptance_mode="final_state",
        description="Non-deterministically guesses the middle of the string and starts popping matching symbols.",
        transitions=[
            # Push symbols in q_push
            PDATransition("q_push", "a", "Z0", "q_push", ("a", "Z0")),
            PDATransition("q_push", "b", "Z0", "q_push", ("b", "Z0")),
            PDATransition("q_push", "a", "a", "q_push", ("a", "a")),
            PDATransition("q_push", "a", "b", "q_push", ("a", "b")),
            PDATransition("q_push", "b", "a", "q_push", ("b", "a")),
            PDATransition("q_push", "b", "b", "q_push", ("b", "b")),
            # Non-deterministic guess of center: switch to q_pop without consuming input
            PDATransition("q_push", EPSILON, "Z0", "q_pop", ("Z0",)),
            PDATransition("q_push", EPSILON, "a", "q_pop", ("a",)),
            PDATransition("q_push", EPSILON, "b", "q_pop", ("b",)),
            # Pop matching symbols in q_pop
            PDATransition("q_pop", "a", "a", "q_pop", ()),
            PDATransition("q_pop", "b", "b", "q_pop", ()),
            # Accept when Z0 reached
            PDATransition("q_pop", EPSILON, "Z0", "q_accept", ("Z0",)),
        ]
    )

    # 3. PDA for Balanced Parentheses
    pda_paren = PDA(
        name="PDA for Balanced Parentheses { ( , ) }",
        states={"q0", "q_accept"},
        input_alphabet={"(", ")"},
        stack_alphabet={"X", "Z0"},
        start_state="q0",
        initial_stack_symbol="Z0",
        accepting_states={"q_accept"},
        acceptance_mode="final_state",
        description="Pushes 'X' for '(', pops 'X' for ')'. Accepts when stack returns to Z0 and input is consumed.",
        transitions=[
            PDATransition("q0", "(", "Z0", "q0", ("X", "Z0")),
            PDATransition("q0", "(", "X", "q0", ("X", "X")),
            PDATransition("q0", ")", "X", "q0", ()),
            PDATransition("q0", EPSILON, "Z0", "q_accept", ("Z0",))
        ]
    )

    return {
        "PDA: a^n b^n": pda_anbn,
        "PDA: Even Palindromes (w w^R)": pda_wwr,
        "PDA: Balanced Parentheses": pda_paren
    }
