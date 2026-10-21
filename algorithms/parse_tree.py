"""
Parse Tree Data Structure and Graphviz Tree Generator.
"""

from typing import List, Optional, Dict, Any
from .grammar import CFG, EPSILON
from .derivations import DerivationStep


class ParseTreeNode:
    """Represents a node in a Context-Free Grammar Parse Tree."""
    _node_counter = 0

    def __init__(self, label: str, is_terminal: bool = False):
        ParseTreeNode._node_counter += 1
        self.node_id = f"node_{ParseTreeNode._node_counter}"
        self.label = label
        self.is_terminal = is_terminal
        self.children: List['ParseTreeNode'] = []

    def add_child(self, child: 'ParseTreeNode'):
        self.children.append(child)

    def to_dot(self) -> str:
        """Render tree into Graphviz DOT language format."""
        lines = [
            'digraph ParseTree {',
            '  rankdir=TB;',
            '  bgcolor="transparent";',
            '  node [fontname="Arial", fontsize=12];',
            '  edge [fontname="Arial", fontsize=10, color="#64748b", arrowhead=none];'
        ]

        def traverse(node: ParseTreeNode):
            if node.is_terminal:
                # Terminal leaves: green/teal filled box
                lines.append(
                    f'  "{node.node_id}" [label="{node.label}", shape=box, style="filled,rounded", fillcolor="#dcfce7", color="#16a34a", fontcolor="#15803d", penwidth=1.5];'
                )
            else:
                # Non-terminal nodes: soft blue filled ellipse
                lines.append(
                    f'  "{node.node_id}" [label="{node.label}", shape=ellipse, style="filled", fillcolor="#e0e7ff", color="#4f46e5", fontcolor="#312e81", penwidth=1.5];'
                )

            for child in node.children:
                lines.append(f'  "{node.node_id}" -> "{child.node_id}";')
                traverse(child)

        traverse(self)
        lines.append('}')
        return "\n".join(lines)


def derivation_to_tree(
    grammar: CFG,
    steps: List[DerivationStep]
) -> Optional[ParseTreeNode]:
    """
    Construct a ParseTreeNode from a sequence of leftmost derivation steps.
    """
    if not steps:
        return None

    # Reset node counter for clean IDs
    ParseTreeNode._node_counter = 0

    root = ParseTreeNode(grammar.start_symbol, is_terminal=False)
    # Active leaves list containing (symbol, node_ref)
    current_leaves: List[ParseTreeNode] = [root]

    # Skip step 0 (initial start symbol)
    for step in steps[1:]:
        prod = step.rule_applied
        if not prod:
            continue

        # In leftmost derivation, find the leftmost variable matching prod.head
        target_idx = None
        for idx, leaf in enumerate(current_leaves):
            if not leaf.is_terminal and leaf.label == prod.head:
                target_idx = idx
                break

        if target_idx is None:
            # Fallback search if index was recorded
            if step.replaced_index is not None and step.replaced_index < len(current_leaves):
                target_idx = step.replaced_index

        if target_idx is None:
            continue

        parent_node = current_leaves[target_idx]

        # Create child nodes for the production body
        new_children: List[ParseTreeNode] = []
        if not prod.clean_body:
            # Epsilon production
            eps_leaf = ParseTreeNode(EPSILON, is_terminal=True)
            parent_node.add_child(eps_leaf)
            new_children.append(eps_leaf)
        else:
            for sym in prod.clean_body:
                is_term = sym in grammar.terminals
                child = ParseTreeNode(sym, is_terminal=is_term)
                parent_node.add_child(child)
                new_children.append(child)

        # Replace parent_node at target_idx with its children in current_leaves
        current_leaves = current_leaves[:target_idx] + new_children + current_leaves[target_idx + 1:]

    return root


def cyk_to_tree(grammar: CFG, cyk_result: Any) -> Optional[ParseTreeNode]:
    """
    Construct a parse tree from CYK dynamic programming backpointers.
    """
    if not cyk_result or not cyk_result.is_accepted or not cyk_result.tokens:
        return None

    ParseTreeNode._node_counter = 0
    n = len(cyk_result.tokens)

    def build_subtree(l: int, i: int, var: str) -> Optional[ParseTreeNode]:
        node = ParseTreeNode(var, is_terminal=False)
        cell = cyk_result.get_cell(l, i)
        if not cell or var not in cell.derivations:
            return node

        derivation_options = cell.derivations[var]
        if not derivation_options:
            return node

        # Pick the first valid derivation option
        deriv = derivation_options[0]
        if deriv["type"] == "terminal":
            leaf = ParseTreeNode(deriv["terminal"], is_terminal=True)
            node.add_child(leaf)
        elif deriv["type"] == "binary":
            split_k = deriv["split_k"]
            left_v = deriv["left_var"]
            right_v = deriv["right_var"]

            left_child = build_subtree(split_k, i, left_v)
            right_child = build_subtree(l - split_k, i + split_k, right_v)

            if left_child:
                node.add_child(left_child)
            if right_child:
                node.add_child(right_child)

        return node

    return build_subtree(n, 0, grammar.start_symbol)
