# test_translation.py

"""
Runs test cases for the LaTeX to Lean translation logic.
"""

import logging
import argparse
from typing import Dict

# Import the core translator function and default maps
try:
    from ast_to_lean import latex_to_lean_symbols
    from translation_maps import DEFAULT_LATEX_ENV_TO_LEAN_KEYWORD
except ImportError as e:
    print(f"FATAL: Could not import required modules for testing: {e}")
    exit(1)

# --- Test Runner Function ---
def run_tests():
    """Executes a series of predefined test cases."""
    print("--- Running Translation Examples ---")

    # Use the default environment map for most tests
    default_env_map = DEFAULT_LATEX_ENV_TO_LEAN_KEYWORD.copy()

    def run_test(name: str, latex_input: str, env_map: Dict[str, str] = default_env_map):
        print(f"\n--- Testing: {name} ---")
        print("Input LaTeX:")
        # Indent input LaTeX slightly for readability in output
        print("\n".join("  " + line for line in latex_input.strip().split('\n')))
        # Call the translator with the specified environment map
        # Ensure tolerant_parsing=False unless testing tolerance specifically
        translated_output = latex_to_lean_symbols(latex_input, environment_map=env_map, tolerant_parsing=False)
        print("\nTranslated Output:")
        if translated_output is not None:
            # Indent output slightly
            print("\n".join("  " + line for line in translated_output.strip().split('\n')))
        else:
            print("  Translation Failed.")
        print("-" * 40)

    # --- Basic Tests ---
    run_test("Basic Symbols",
             r"Let A ⊆ B. If x ∈ A → x ∈ B. ∀ ε > 0, a ≠ b, c ≥ d.")
    run_test("Fractions",
             r"Simple: $1/2$. Complex num: $(a+b)/c$. Nested: $(1/x)/(1+(1/y))$. Frac macro: $\frac{a+b}{c-d}$")
    run_test("Fonts & mathbf",
             r"Sets $\mathbb{R}, \mathcal{F}, \mathbf{v}$. $\mathbb{F}_q$. $\mathcal{P}(S)$.")
    run_test("Square Roots",
             r"$\sqrt{2}$, $\sqrt{x^2+y^2}$, $\sqrt{\frac{a}{b}}$. $\sqrt{(a+b)/c}$.")
    run_test("Align Environment",
             r"""Text before. \begin{align*} f(x) &= x^2 \\ g(x) &= x^3 \end{align*} Text after.""")

    # --- Label Handling Tests ---
    run_test("Theorem Env with Label",
             r"\begin{theorem}\label{ThmPythagoras} $a^2+b^2=c^2$. \end{theorem}")
    run_test("Lemma Env with Optional Arg and Label",
             r"\begin{lemma}[TRI]\label{LemTriangleIneq} $\|u+v\| \le \|u\| + \|v\|$. \end{lemma}")
    # Test proposition which maps to 'theorem' by default
    run_test("Prop Env with No Label/Arg",
             r"\begin{proposition} $2+2=4$. \end{proposition}")
    run_test("Theorem Env with Label and Display Math",
              r"""
              \begin{theorem}\label{ThmHomeomA1} There is a homeomorphism
              \[ |(\mathbb{A}^1_{K^\flat})^\ad|\cong \varprojlim_{T\mapsto T^p} |(\mathbb{A}^1_K)^\ad|\ . \]
              \end{theorem}""")

    # --- Subscript/Superscript Tests ---
    run_test("Simple Subscripts (Convertible)",
             r"$x_1$, $v_i$, $A_{n}$, $f_{min}$, $k_{n+1}$, $a_{ij}$, $T_{max}$")
    run_test("Simple Subscripts (Mixed/Fallback)",
             r"$P_{red}$, $Z_{abc}$, $v_{\beta}$, $M_{1+k}$")
    run_test("Complex Subscripts (Fallback)",
             r"$X_{i \in I}$, $Y_{\text{some text}}$, $Z_{k=1}^N$")
    run_test("Empty Subscript", r"Test $x_{}$ here.")
    run_test("Simple Superscripts",
             r"$x^2$, $f(x)^n$, $\mathbb{R}^n$, $a^{i+j}$, $k^{n_i}$")
    run_test("Subscript/Superscript Combined",
             r"$A_i^j$, $B^{n+1}_k$, $C_{n^2}$")

    # --- Other Tests ---
    run_test("Proof Environment",
              r"\begin{proof} Assume $a \ne 0$. Then $a^{-1}$ exists. QED. \end{proof}")
    run_test("Unhandled Environment",
             r"\begin{itemize} \item First \item Second \end{itemize}")
    run_test("Escaped Characters", r"Price: \$10. Percentage: 50\%. Ref \#Ref. Curly \{brace\}. Ampersand \&.")

    # --- Test Custom Environment Mapping ---
    custom_map = default_env_map.copy()
    custom_map['myaxiom'] = 'axiom'
    custom_map['claim'] = 'lemma' # Override default idea for 'claim' if it existed
    run_test("Custom Environment (myaxiom)",
             r"\begin{myaxiom}\label{ax:choice} Every set can be well-ordered. \end{myaxiom}",
             env_map=custom_map)
    run_test("Custom Environment (claim -> lemma)",
             r"\begin{claim}[Important] This is true. \end{claim}",
             env_map=custom_map)

    # --- Test Complex Document Structure ---
    # This LaTeX string includes a preamble with definitions that *should* affect translation.
    # However, only the \newtheorem definitions are currently processed by process_tex_file.py
    # to create the environment map passed to the translator.
    # \newcommand and \DeclareMathOperator are NOT processed by the current setup.
    latex_complex_doc_full = r"""
    \documentclass{article}
    \usepackage{amsmath} % Affects parsing slightly, but logic should handle it

    % Custom theorem-like environments
    \newtheorem{postulate}{Postulate}
    \newtheorem*{axiom*}{Axiom} % Starred version
    \newtheorem{prop}{Proposition} % Could potentially override default

    % Custom commands and operators (NOTE: only \newtheorem affects env_map currently)
    \newcommand{\Z}{\mathbb{Z}} % \Z will likely be unhandled macro
    \newcommand{\R}{\mathbb{R}} % \R will likely be unhandled macro
    \DeclareMathOperator{\Hom}{Hom} % Already in default SYMBOL_MAP, should work
    \DeclareMathOperator{\Spec}{Spec} % Spec will likely be unhandled macro

    \begin{document}

    Here is some introductory text.

    \begin{postulate}[Euclid V]\label{post:euclid5}
    If a straight line falling on two straight lines makes the interior angles on the same side less than two right angles, the two straight lines, if produced indefinitely, meet on that side on which are the angles less than the two right angles. $f(x) = \sqrt{x}$.
    \end{postulate}

    We can use standard math like $\alpha + \beta = \gamma$.
    We can also use custom commands: elements in $\Z$ or $\R$.
    And custom operators: $\Hom(A, B)$ and $\Spec(R)$.

    \begin{axiom*} % Starred, should be handled by the custom map
    A point has no part. Use $\le$ and $\ge$.
    \end{axiom*}

    \begin{prop}\label{prop:dummy} % Should use 'Proposition' from custom map
    This is a proposition. Maybe $1/2 \in \mathbb{Q}$. Check $\mathcal{P}(S)$.
    \end{prop}

    More text. $E=mc^2$. The end.

    \end{document}
    """

    # Manually simulate preamble processing for the environment map ONLY.
    # This reflects what process_tex_file.py actually does.
    expected_custom_env_map = {
        'postulate': 'Postulate', # New environment
        'axiom*': 'Axiom',        # New starred environment
        'prop': 'Proposition'     # Override default mapping for 'proposition'
                                  # Note: DEFAULT_LATEX_ENV_TO_LEAN_KEYWORD maps 'proposition' -> 'theorem'
                                  # This test uses 'prop' -> 'Proposition' based on the \newtheorem line.
    }
    complex_test_env_map = default_env_map.copy()
    complex_test_env_map.update(expected_custom_env_map)
    # Ensure 'proposition' mapping isn't accidentally used if 'prop' is defined
    if 'proposition' in complex_test_env_map and 'prop' in expected_custom_env_map:
         # This logic depends on whether \newtheorem{prop} should *replace* or *coexist*
         # with a potential default 'proposition'. Assuming it defines 'prop'.
         pass # complex_test_env_map['prop'] = 'Proposition' is done by update

    # Manually extract the body content for the test run
    body_start_marker = r"\begin{document}"
    body_end_marker = r"\end{document}"
    body_start_index = latex_complex_doc_full.find(body_start_marker)
    body_end_index = latex_complex_doc_full.rfind(body_end_marker)

    if body_start_index != -1 and body_end_index != -1:
        complex_doc_body = latex_complex_doc_full[body_start_index + len(body_start_marker):body_end_index].strip()
        run_test("Complex Document (Simulated Preamble Env Processing)",
                 complex_doc_body,
                 env_map=complex_test_env_map)
    else:
        print("\n--- Skipping Complex Document Test ---")
        print("Could not extract document body from test string.")
        print("-" * 40)


# --- Main Execution Block ---
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Run test cases for LaTeX to Lean translation.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        '-v', '--verbose', action='store_true',
        help='Print INFO level logs (parsing steps, progress)'
    )
    args = parser.parse_args()

    # Configure logging for the test run
    log_level = logging.INFO if args.verbose else logging.WARNING
    log_format = '%(levelname)s: %(message)s'
    logging.basicConfig(level=log_level, format=log_format, force=True) # Use force=True

    run_tests()