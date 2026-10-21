# Interactive CFG and PDA Learning Tool

An educational web application for Computer Science and Engineering students studying **Theory of Computation (Automata Theory)**. Explore Context-Free Grammars (CFGs), Pushdown Automata (PDAs), Chomsky Normal Form (CNF), Greibach Normal Form (GNF), and the CYK dynamic programming parsing algorithm.

---

## 🌟 Key Features

1. **CFG Explorer & Diagnostics:** Define custom grammars or load predefined academic grammars ($a^n b^n$, palindromes, arithmetic expressions, Dyck languages). Validates non-generating and unreachable symbols.
2. **Leftmost & Rightmost Derivations:** Interactively derive target strings step-by-step with bounded BFS search avoiding infinite loops.
3. **6-Stage Chomsky Normal Form (CNF) Pipeline:** Start symbol isolation, $\epsilon$-elimination, unit production elimination, useless symbol pruning, terminal replacement, and binarization.
4. **Greibach Normal Form (GNF) Conversion:** Variable ordering, forward/backward substitution, and left-recursion elimination.
5. **Cocke-Younger-Kasami (CYK) Membership Tester:** Interactive triangular dynamic programming table with cell inspector explaining derivation backpointers.
6. **Pushdown Automata (PDA) Simulator:** Step forward, step backward, reset, and run all with live LIFO stack display and acceptance diagnostics.
7. **Graph Visualizations:** Graphical Graphviz parse trees and directed state diagrams with active state highlighting.
8. **Automated Test Matrix:** Live browser-based test suite runner with 100% pass verification.

---

## 💻 Installation & Setup (Windows)

### Prerequisites
- Python 3.10+ (tested on Python 3.14)
- Web Browser (Chrome, Edge, Firefox)

### Step 1: Clone or Navigate to the Repository
```powershell
cd c:\Users\janha\Desktop\interactive-cfg-pda-tool
```

### Step 2: Create and Activate Virtual Environment
```powershell
python -m venv .venv
.venv\Scripts\activate
```

### Step 3: Install Required Dependencies
```powershell
python -m pip install -r requirements.txt
```

### Step 4: Run the Streamlit Application
```powershell
python -m streamlit run app.py
```

The application will automatically open in your default browser at `http://localhost:8501`.

---

## 🧪 Running Automated Tests

Run the full pytest automated test suite with verbose output:

```powershell
python -m pytest -v
```

All 24 test cases across CFG parsing, derivations, CNF/GNF conversions, CYK DP parsing, and PDA simulation will execute and verify algorithm correctness.

---

## 📂 Project Architecture

```
interactive-cfg-pda-tool/
├── app.py                     # Main Streamlit application entrypoint & router
├── requirements.txt           # Python dependency specification
├── README.md                  # Installation, execution & overview guide
├── .gitignore                 # Version control ignore definitions
├── algorithms/                # Pure Python algorithmic engines (UI-independent)
│   ├── __init__.py            # Algorithm module exports
│   ├── grammar.py             # CFG, Production classes, tokenization, catalog
│   ├── validation.py          # CFG syntax, generating, and reachable diagnostics
│   ├── derivations.py         # Leftmost/rightmost derivations & bounded search
│   ├── cnf.py                 # Genuine 6-stage CNF transformation pipeline
│   ├── gnf.py                 # Greibach Normal Form pipeline & left recursion
│   ├── cyk.py                 # Cocke-Younger-Kasami DP matrix & cell backpointers
│   ├── pda.py                 # Formal 7-tuple PDA simulator & DOT exporter
│   └── parse_tree.py          # ParseTreeNode and Graphviz parse tree builder
├── ui/                        # Modular Streamlit user interface components
│   ├── __init__.py            # UI package init
│   ├── common.py              # CSS styles, session state & shared grammar selector
│   ├── home.py                # Landing page & feature cards
│   ├── cfg_page.py            # CFG editor, rule viewer & diagnostics
│   ├── derivation_page.py     # Derivation viewer & step tracer
│   ├── cnf_page.py            # CNF pipeline viewer with stage breakdowns
│   ├── gnf_page.py            # GNF conversion viewer
│   ├── cyk_page.py            # CYK triangular DP table & interactive cell inspector
│   ├── pda_page.py            # Interactive PDA stepper & stack visualizer
│   ├── visualization_page.py  # Graphviz parse trees & PDA state graphs
│   ├── tests_page.py          # Live test execution matrix
│   └── about_page.py          # Academic project info & theoretical notes
├── tests/                     # Pytest automated test suite
│   ├── test_grammar.py        # Grammar parsing & validation tests
│   ├── test_derivations.py    # Derivations & sample string tests
│   ├── test_cnf.py            # CNF conversion & equivalence tests
│   ├── test_gnf.py            # GNF conversion tests
│   ├── test_cyk.py            # CYK matrix & acceptance tests
│   └── test_pda.py            # PDA execution & stack tests
└── docs/                      # Submission documentation
    ├── project_report.md      # Full academic project report (19 sections)
    ├── flowchart.md           # Mermaid system, CYK, CNF, and PDA diagrams
    └── test_cases.md          # Comprehensive test cases and results table
```

---

## 📖 Theoretical Quick Reference

- **CFG:** $G = (V, \Sigma, R, S)$
- **CNF:** $A \to BC$ or $A \to a$, with optional $S_0 \to \epsilon$.
- **GNF:** $A \to a \alpha$ where $a \in \Sigma, \alpha \in V^*$.
- **CYK Complexity:** $O(n^3 \cdot |P|)$ where $n$ is string length and $|P|$ is rule count.
- **PDA:** $M = (Q, \Sigma, \Gamma, \delta, q_0, Z_0, F)$ with LIFO stack operations.

---

## 📜 Academic Attribution & Project Metadata

- **Author / Developer:** Janhavi ([@Janhavi92691](https://github.com/Janhavi92691))
- **GitHub Repository:** [https://github.com/Janhavi92691/interactive-cfg-pda-tool](https://github.com/Janhavi92691/interactive-cfg-pda-tool)
- **Visual Design Reference & Inspiration:** [PushdownPlayground](https://github.com/hannyjangir1-commits/PushdownPlayground)
- **License:** MIT License

