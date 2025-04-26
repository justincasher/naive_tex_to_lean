# latex_to_ast.py

"""Parses LaTeX code into an Abstract Syntax Tree (AST) using pylatexenc v2.10.

This module provides functionality to convert a string containing LaTeX markup
into a structured node list representation (AST). This AST is suitable for
further processing, such as analysis or translation into other formats (e.g., Lean).

It relies specifically on pylatexenc version 2.10. Ensure this version is
installed (`pip install pylatexenc==2.10`).
"""

import sys
import logging
from typing import List, Optional, Any, TypeAlias

# Configure basic logging
# Levels: DEBUG, INFO, WARNING, ERROR, CRITICAL
# Use INFO for standard operational messages, DEBUG for detailed tracing.
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

# --- Dependency Check and Import ---
try:
    # pylatexenc v2.10 core classes are in pylatexenc.latexwalker
    from pylatexenc.latexwalker import (
        LatexWalker, LatexCharsNode, LatexMacroNode, LatexEnvironmentNode,
        LatexGroupNode, LatexMathNode, LatexCommentNode, LatexSpecialsNode,
        LatexWalkerParseError, get_default_latex_context_db, LatexNode
    )
    # Note: In pylatexenc v3.x, these classes moved to pylatexenc.latexnodes.*
    logging.debug("Successfully imported pylatexenc v2.10 components.")
except ImportError:
    logging.critical(
        "FATAL ERROR: Failed to import pylatexenc.latexwalker classes. "
        "Ensure pylatexenc v2.10 is installed (`pip install pylatexenc==2.10`)."
    )
    sys.exit(1) # Exit if the core dependency is missing

# Define LatexNode type alias for clarity in type hints
# Represents any node type from pylatexenc.latexwalker
LatexNodeType: TypeAlias = LatexNode


# --- Core Parsing Function ---

def parse_latex_to_ast_v210(
    latex_string: str,
    tolerant_parsing: bool = False
) -> Optional[List[LatexNodeType]]:
    """Parses a LaTeX string into an AST (nodelist) using pylatexenc v2.10.

    Utilizes pylatexenc.latexwalker.LatexWalker with the default LaTeX context
    database to parse the input string. It can optionally tolerate some parsing
    errors.

    Args:
        latex_string: The string containing the LaTeX code to be parsed.
        tolerant_parsing: If True, the parser attempts to recover from syntax
            errors instead of raising an exception immediately. Defaults to False.

    Returns:
        A list of LatexNode objects representing the root nodes of the parsed AST,
        or None if a critical parsing error occurs that prevents AST generation
        (especially if tolerant_parsing is False). Returns an empty list for
        an empty input string.
    """
    if not latex_string:
        logging.info("Input LaTeX string is empty. Returning empty nodelist.")
        return []

    logging.info(f"Attempting to parse LaTeX string (len={len(latex_string)} characters)...")

    # Use the default context DB for standard LaTeX definitions.
    # For custom LaTeX, a modified LatexContextDb would be needed.
    latex_context = get_default_latex_context_db()

    try:
        # Instantiate LatexWalker with the string and context.
        lw = LatexWalker(
            latex_string,
            latex_context=latex_context,
            tolerant_parsing=tolerant_parsing
        )

        # Parse the LaTeX string to get the node list (AST).
        # get_latex_nodes is the primary parsing method in v2.10.
        # It returns (nodelist, pos_end, len_parsed)
        nodelist, _, _ = lw.get_latex_nodes(pos=0)

        logging.info(f"Successfully parsed LaTeX into {len(nodelist)} top-level node(s).")
        return nodelist

    except LatexWalkerParseError as e:
        # Log the parsing error details clearly.
        logging.error(f"LaTeX Parsing Error: {e.msg}")
        if e.pos is not None:
            # Provide context around the error position for easier debugging.
            context_width = 25
            start = max(0, e.pos - context_width)
            end = min(len(latex_string), e.pos + context_width)
            # Represent the error position clearly in the context string
            context_str = f"{latex_string[start:e.pos]}<ERROR>{latex_string[e.pos:end]}"
            logging.error(f"  Position: {e.pos}")
            logging.error(f"  Near: ...{context_str}...")
            # Attempt to get line/column info
            try:
                # Need a LatexWalker instance for pos_to_lineno_colno
                # Create a temporary, non-tolerant one for this calculation
                temp_lw = LatexWalker(latex_string)
                lineno, colno = temp_lw.pos_to_lineno_colno(e.pos)
                logging.error(f"  Approx. Line: {lineno}, Column: {colno}")
            except Exception as le:
                 logging.error(f"  (Could not determine line/column number: {le})")
        return None # Indicate parsing failure

    except Exception as e:
        # Catch other unexpected errors during parsing.
        logging.exception(f"An unexpected error occurred during parsing: {e}")
        return None # Indicate failure

# --- AST Display Helper Function (for debugging/demonstration) ---

def _display_node_recursive(node: Optional[LatexNodeType], indent: int = 0) -> None:
    """Recursively prints details of a single AST node and its children.

    Internal helper function for display_ast_structure. Handles potential None
    nodes that might appear in argument lists (e.g., omitted optional args).

    Args:
        node: The LatexNode object (or None) to display.
        indent: The current indentation level for pretty-printing.
    """
    prefix = "  " * indent

    # Handle None nodes (e.g., missing optional arguments) gracefully
    if node is None:
        print(f"{prefix}<Node is None (Optional Arg Not Present?)>")
        return

    node_type = type(node).__name__
    # Provide basic info common to all nodes
    base_info = f"{prefix}Type={node_type}, Pos={node.pos}-{node.pos+node.len}"

    # Add type-specific details and handle children recursively
    if isinstance(node, LatexCharsNode):
        print(f"{base_info}, Chars={repr(node.chars)}")
    elif isinstance(node, LatexMacroNode):
        print(f"{base_info}, Macro='\\{node.macroname}'")
        # Display arguments if they exist (nodeargd holds parsed args info)
        if node.nodeargd and node.nodeargd.argnlist:
             print(f"{prefix}  Args ({len(node.nodeargd.argnlist)}):")
             for i, arg_node in enumerate(node.nodeargd.argnlist):
                 print(f"{prefix}    Arg {i+1}:")
                 _display_node_recursive(arg_node, indent + 3)
        # else: No need to print "Args: None", absence implies no args parsed
    elif isinstance(node, LatexEnvironmentNode):
        print(f"{base_info}, Env='{node.environmentname}'")
        # Display environment arguments if present
        if node.nodeargd and node.nodeargd.argnlist:
             print(f"{prefix}  Env Args ({len(node.nodeargd.argnlist)}):")
             for i, arg_node in enumerate(node.nodeargd.argnlist):
                 print(f"{prefix}    Env Arg {i+1}:")
                 _display_node_recursive(arg_node, indent + 3)
        # Display nodes within the environment body
        print(f"{prefix}  Body Content ({len(node.nodelist)} nodes):")
        for body_node in node.nodelist:
            _display_node_recursive(body_node, indent + 1)
    elif isinstance(node, LatexGroupNode):
        delimiters = node.delimiters if node.delimiters else ('{', '}') # Default if not specified
        print(f"{base_info}, Delimiters={delimiters}")
        # Display nodes within the group
        print(f"{prefix}  Group Content ({len(node.nodelist)} nodes):")
        for group_node in node.nodelist:
            _display_node_recursive(group_node, indent + 1)
    elif isinstance(node, LatexMathNode):
        # node.displaytype can be 'inline', 'display', or potentially other values
        # depending on how math mode was initiated.
        print(f"{base_info}, DisplayType='{node.displaytype}'")
        # Display the parsed nodes *inside* the math environment
        if node.nodelist:
             print(f"{prefix}  Parsed Math Content ({len(node.nodelist)} nodes):")
             for math_content_node in node.nodelist:
                 _display_node_recursive(math_content_node, indent + 1)
        # else: No need to print "(Empty)", absence implies empty list
    elif isinstance(node, LatexCommentNode):
        # Display the comment content, including the initial '%'
        print(f"{base_info}, Comment='%{node.comment}'")
    elif isinstance(node, LatexSpecialsNode):
         # Specials chars like alignment tabs (&), math shifts ($), super/subscripts (^, _)
         print(f"{base_info}, Specials={repr(node.specials_chars)}")
         # Display arguments if they exist (e.g., for superscript/subscript)
         if node.nodeargd and node.nodeargd.argnlist:
             print(f"{prefix}  Args ({len(node.nodeargd.argnlist)}):")
             for i, arg_node in enumerate(node.nodeargd.argnlist):
                 print(f"{prefix}    Arg {i+1}:")
                 _display_node_recursive(arg_node, indent + 3)
    else:
        # Fallback for any other node types encountered
        print(f"{base_info} (Node Type: {type(node)}, Value: {node})")


def display_ast_structure(nodelist: List[LatexNodeType]) -> None:
    """Displays the structure of the parsed LaTeX AST (nodelist) to stdout.

    Iterates through the top-level nodes and calls a recursive helper
    to print the details of each node and its children in a hierarchical format.
    Useful for debugging and understanding the parser's output.

    Args:
        nodelist: The list of LatexNode objects representing the AST, typically
                  the direct output of `parse_latex_to_ast_v210`.
    """
    print("\n--- AST Structure Start ---")
    if not nodelist:
        print("(Nodelist is empty or None)")
    else:
        for i, top_level_node in enumerate(nodelist):
            print(f"\n--- Top Level Node {i} ---") # Use 0-based index consistent with list indexing
            _display_node_recursive(top_level_node, indent=0)
    print("\n--- AST Structure End ---")


# --- Example Usage ---

if __name__ == "__main__":
    # This block runs only when the script is executed directly.
    # It serves as a demonstration and basic test of the parsing function.

    # --- Example 1: Inline Math ---
    print("\n\n=== Running Example: Inline Math ===")
    LATEX_INLINE_MATH = r"Consider $E = mc^2$ and $a^2 + b^2 = c^2$."
    print(f"Input LaTeX:\n{LATEX_INLINE_MATH}")
    ast_inline = parse_latex_to_ast_v210(LATEX_INLINE_MATH)
    if ast_inline is not None:
        display_ast_structure(ast_inline)
    else:
        logging.error("Example failed: Could not parse inline math.")
    print("-" * 60)

    # --- Example 2: Display Math ---
    print("\n\n=== Running Example: Display Math ===")
    # Using \[ ... \]
    LATEX_DISPLAY_MATH = r"The integral is \[ \int_a^b f(x)\,dx = F(b) - F(a) \]"
    print(f"Input LaTeX:\n{LATEX_DISPLAY_MATH}")
    ast_display = parse_latex_to_ast_v210(LATEX_DISPLAY_MATH)
    if ast_display is not None:
        display_ast_structure(ast_display)
    else:
        logging.error("Example failed: Could not parse display math.")
    print("-" * 60)

    # --- Example 3: Equation Environment ---
    print("\n\n=== Running Example: Equation Environment ===")
    LATEX_EQUATION = r"""
    Text before.
    \begin{equation}
    \label{eq:lorentz}
    \gamma = \frac{1}{\sqrt{1 - v^2/c^2}} % comment inside
    \end{equation}
    Text after.
    """
    print(f"Input LaTeX:\n{LATEX_EQUATION}")
    ast_equation = parse_latex_to_ast_v210(LATEX_EQUATION)
    if ast_equation is not None:
        display_ast_structure(ast_equation)
    else:
        logging.error("Example failed: Could not parse equation environment.")
    print("-" * 60)

    # --- Example 4: Align Environment ---
    print("\n\n=== Running Example: Align Environment ===")
    LATEX_ALIGN = r"""
    Multiple lines:
    \begin{align}
    a &= b + c \\ % line break
    d &= e + f + g \label{eq:align2}
    \end{align}
    """
    print(f"Input LaTeX:\n{LATEX_ALIGN}")
    ast_align = parse_latex_to_ast_v210(LATEX_ALIGN)
    if ast_align is not None:
        display_ast_structure(ast_align)
    else:
        logging.error("Example failed: Could not parse align environment.")
    print("-" * 60)

    # --- Example 5: Math with Nested Elements ---
    print("\n\n=== Running Example: Math with Nested Elements ===")
    LATEX_NESTED_MATH = r"Equation $x_{i+1} = \sqrt[3]{\sin( \theta_i^2 + \{ \frac{\pi}{2} \} )}$"
    print(f"Input LaTeX:\n{LATEX_NESTED_MATH}")
    ast_nested_math = parse_latex_to_ast_v210(LATEX_NESTED_MATH)
    if ast_nested_math is not None:
        display_ast_structure(ast_nested_math)
    else:
        logging.error("Example failed: Could not parse nested math.")
    print("-" * 60)

    # --- Example 6: Tolerant Parsing Demo (Optional) ---
    # print("\n\n=== Running Example: Tolerant Parsing (Error Expected) ===")
    # LATEX_WITH_ERROR = r"Some text \textbf{bold} and \anUndefinedMacro then more text."
    # print(f"Input LaTeX with error:\n{LATEX_WITH_ERROR}")
    # ast_tolerant = parse_latex_to_ast_v210(LATEX_WITH_ERROR, tolerant_parsing=True)
    # if ast_tolerant is not None:
    #     logging.warning("Tolerant parsing generated an AST despite the error.")
    #     display_ast_structure(ast_tolerant)
    # else:
    #     # This might happen if the error is too severe even for tolerant mode
    #     logging.error("Example failed: Tolerant parsing could not generate AST.")
    # print("-" * 60)

    # --- Example 7: Parser Error Demo (Strict Parsing) ---
    print("\n\n=== Running Example: Parser Error (Strict Parsing) ===")
    LATEX_WITH_SYNTAX_ERROR = r"Text with {unmatched brace."
    print(f"Input LaTeX with error:\n{LATEX_WITH_SYNTAX_ERROR}")
    ast_error = parse_latex_to_ast_v210(LATEX_WITH_SYNTAX_ERROR, tolerant_parsing=False)
    if ast_error is None:
        logging.info("Example succeeded: Parser correctly returned None on error.")
    else:
        # This shouldn't happen with tolerant_parsing=False for this error
        logging.error("Example failed: Parser did NOT return None on error.")
        display_ast_structure(ast_error)
    print("-" * 60)

    # --- Example 8: Cosine Formula with Sqrt (Potential Parser Issue) ---
    print("\n\n=== Running Example: Cosine Formula with Sqrt ===")
    LATEX_COSINE_FORMULA = r"$\frac{\mathbf{v} \cdot \mathbf{w}}{\sqrt{\mathbf{v} \cdot \mathbf{v}} \sqrt{\mathbf{w} \cdot \mathbf{w}}}$"
    print(f"Input LaTeX:\n{LATEX_COSINE_FORMULA}")
    # Parse only the math content to isolate the issue
    ast_cosine = parse_latex_to_ast_v210(LATEX_COSINE_FORMULA)
    if ast_cosine is not None:
        print("Displaying AST for the entire line:")
        display_ast_structure(ast_cosine)
        # Optionally, you could try parsing *just* the denominator if needed,
        # but parsing the whole math expression is usually best first.
    else:
        logging.error("Example failed: Could not parse cosine formula.")
    print("-" * 60)