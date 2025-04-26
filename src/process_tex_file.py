# process_tex_file.py

"""
Reads a LaTeX (*.tex) file, parses it into an Abstract Syntax Tree (AST),
applies command substitutions (e.g., \newcommand, \DeclareMathOperator) to the AST,
analyses the original preamble string to discover ``\newtheorem`` environments,
combines these with default environment mappings, extracts the AST corresponding
to the document body, translates this body AST using the combined map via
``ast_to_lean.latex_to_lean_symbols``, and writes the output.

Relies on pylatexenc v2.10 for parsing and AST manipulation.
"""

from __future__ import annotations

import argparse
import logging
import re
import sys
from pathlib import Path
import copy # Needed for DEFAULT_LATEX_ENV_TO_LEAN_KEYWORD.copy()
from typing import List, Optional, Dict, Union, TYPE_CHECKING

# --- Imports from Local Modules ---
# Fail hard if any core component is missing.
try:
    # For Parsing LaTeX to AST (v2.10) and Node Types
    from latex_to_ast import (
        parse_latex_to_ast_v210,
        LatexNodeType, # Type alias for LatexNode base class
        LatexEnvironmentNode # Need this specific type for body extraction
    )
except ImportError as e:
    print(f"FATAL ERROR: Cannot import from 'latex_to_ast.py'. Ensure it exists and pylatexenc v2.10 is installed. Error: {e}", file=sys.stderr)
    sys.exit(1)

try:
    # For Applying Substitutions to the AST
    from ast_substitutions import apply_substitutions_iteratively
except ImportError as e:
    print(f"FATAL ERROR: Cannot import from 'ast_substitutions.py'. Ensure it exists. Error: {e}", file=sys.stderr)
    sys.exit(1)

try:
    # For Translating the AST to Lean-like text
    from ast_to_lean import latex_to_lean_symbols
    # Default environment map
    from translation_maps import DEFAULT_LATEX_ENV_TO_LEAN_KEYWORD
except ImportError as e:
    print(f"FATAL ERROR: Cannot import from 'ast_to_lean.py' or 'translation_maps.py'. Error: {e}", file=sys.stderr)
    sys.exit(1)

try:
    # For processing \newtheorem definitions from the preamble string
    from process_preamble import extract_newtheorem_mappings
except ImportError as e:
    print(f"FATAL ERROR: Cannot import from 'process_preamble.py'. Error: {e}", file=sys.stderr)
    sys.exit(1)


# --- Helper Functions ---

def _split_preamble_and_body(tex: str) -> tuple[str, str]:
    """Return (preamble_string, body_string_for_reference_only).

    Finds the preamble based on the first ``\begin{document}``.
    The returned body string is NOT used for main translation anymore,
    but the preamble string IS used for environment mapping extraction.

    Args:
        tex: The full LaTeX source string.

    Returns:
        A tuple containing the preamble string and the body string.
        Returns ("", tex) if ``\begin{document}`` is not found.
    """
    # Use re.IGNORECASE for robustness against \BEGIN{document} etc.
    begin_match = re.search(r"\\begin\{document\}", tex, re.IGNORECASE)
    if not begin_match:
        logging.warning("No '\\begin{document}' found. Preamble processing might yield no results.")
        return "", tex # Treat all as body for reference, empty preamble

    preamble = tex[: begin_match.start()]
    rest = tex[begin_match.end() :]

    # Extract body string for potential reference, though not used for AST translation
    end_match = re.search(r"\\end\{document\}", rest, re.IGNORECASE)
    body = rest[: end_match.start()] if end_match else rest
    if not end_match:
        logging.warning("No matching '\\end{document}' found.")

    return preamble, body

def extract_document_body_nodelist(
    top_level_nodelist: List[LatexNodeType],
    logger: logging.Logger
) -> Optional[List[LatexNodeType]]:
    """Searches the top-level nodelist for the 'document' environment node.

    Args:
        top_level_nodelist: The list of nodes representing the full document AST
                           (potentially after substitutions).
        logger: Logger instance for reporting issues.

    Returns:
        The list of nodes representing the document body (content of the
        'document' environment), or None if the 'document' environment node
        cannot be reliably found or its content extracted.
    """
    logger.debug("Searching for 'document' environment node in top-level AST...")
    document_node_found: Optional[LatexEnvironmentNode] = None
    for node in top_level_nodelist:
        # Check if the node is an EnvironmentNode with the correct name
        if node and isinstance(node, LatexEnvironmentNode) and node.environmentname == 'document':
            if document_node_found is not None:
                # Handle the unlikely case of multiple document environments
                logger.warning(
                    "Multiple 'document' environments found in top-level AST "
                    "at pos %d and %d. Using the first one found.",
                    document_node_found.pos, node.pos
                )
                # Continue using the first one found, break if needed: break
            else:
                document_node_found = node
                logger.debug("Found 'document' environment node starting at pos %d.", node.pos)
                # Optionally break if you only ever want the first one: break

    if document_node_found:
        # The nodelist attribute holds the environment's body content
        if hasattr(document_node_found, 'nodelist') and isinstance(document_node_found.nodelist, list):
             logger.info("Extracted body nodelist from 'document' environment.")
             # Return the list of nodes constituting the body
             return document_node_found.nodelist
        else:
             logger.error(
                 "'document' environment node found at pos %d, but it lacks a valid "
                 "'nodelist' attribute containing its body.", document_node_found.pos
             )
             return None # Cannot extract body
    else:
        logger.error(
            "Could not find the 'document' environment node within the "
            "top-level nodes of the parsed AST."
        )
        return None # Document environment not found


# --- Main Application Logic ---

def main() -> None:
    """Parses command line arguments and orchestrates the LaTeX processing workflow."""
    parser = argparse.ArgumentParser(
        description="Translate LaTeX document body to Lean-like text, processing preamble for "
                    "environments and applying command substitutions to the AST.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument("input_tex_path", type=Path, help="Input .tex file")
    parser.add_argument("output_txt_path", type=Path, help="Output file (text)")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose INFO logging")
    parser.add_argument("--debug", action="store_true", help="Enable DEBUG level logging (very verbose)")
    parser.add_argument(
        "--tolerant-parsing",
        action="store_true",
        help="Attempt to tolerate LaTeX parsing errors (use with caution)."
    )

    args = parser.parse_args()

    # --- Setup Logging ---
    log_level = logging.WARNING
    if args.verbose:
        log_level = logging.INFO
    if args.debug:
        log_level = logging.DEBUG # Debug implies verbose

    logging.basicConfig(
        level=log_level,
        format="[%(asctime)s] %(name)-20s %(levelname)-8s: %(message)s",
        datefmt="%H:%M:%S"
    )
    # Get the logger for this main script
    logger = logging.getLogger(__name__)
    logger.info("Logging initialized at level: %s", logging.getLevelName(log_level))


    # --- Read Input File ---
    logger.info("Reading input file: %s", args.input_tex_path)
    try:
        tex_source = args.input_tex_path.read_text(encoding="utf-8")
        logger.info("Read %d characters from input file.", len(tex_source))
    except FileNotFoundError:
        logger.critical("Input file not found: %s", args.input_tex_path)
        sys.exit(1)
    except OSError as exc:
        logger.critical("Cannot read %s: %s", args.input_tex_path, exc)
        sys.exit(1)
    except Exception as exc:
        logger.exception("An unexpected error occurred reading the input file: %s", exc)
        sys.exit(1)


    # --- STEP 1: Parse Full LaTeX Source to AST (v2.10) ---
    logger.info("Parsing full LaTeX source file to AST...")
    initial_nodelist: Optional[List[LatexNodeType]] = None
    try:
        initial_nodelist = parse_latex_to_ast_v210(tex_source, tolerant_parsing=args.tolerant_parsing)
    except Exception as exc:
        logger.exception("An unexpected error occurred during initial AST parsing step: %s", exc)

    if initial_nodelist is None:
        logger.critical("Initial parsing failed (check logs for details). Cannot proceed.")
        sys.exit(1)
    logger.info("Initial parsing successful. Full AST has %d top-level nodes.", len(initial_nodelist))


    # --- STEP 2: Apply Command Substitutions to Full AST ---
    logger.info("Applying command substitutions to the full AST...")
    substituted_full_nodelist: Optional[List[LatexNodeType]] = None
    try:
        # Use the logger for the substitution module
        substitution_logger = logging.getLogger("ast_substitutions")
        substitution_logger.setLevel(logger.level) # Ensure logging level is consistent

        substituted_full_nodelist = apply_substitutions_iteratively(
            initial_nodelist, logger=substitution_logger
        )
        logger.info("Command substitution phase complete.")
    except Exception as exc:
        logger.exception("An unexpected error occurred during AST substitution: %s", exc)
        logger.critical("AST substitution failed. Aborting.")
        sys.exit(1)


    # --- STEP 3: Extract Document Body AST ---
    logger.info("Extracting document body AST from the substituted nodelist...")
    if substituted_full_nodelist is None:
         logger.critical("Substitution phase failed or produced None, cannot extract body.")
         sys.exit(1)
    # Use the helper function to find the document body
    body_nodelist = extract_document_body_nodelist(substituted_full_nodelist, logger)

    if body_nodelist is None:
        # Error message logged within the helper function
        logger.critical("Failed to extract document body AST. Cannot translate.")
        sys.exit(1)
    logger.info("Successfully extracted document body AST.")


    # --- STEP 4: Process Preamble String for Environment Mappings ---
    logger.info("Processing preamble string for custom environment mappings...")
    preamble, _ = _split_preamble_and_body(tex_source) # Still need original preamble string
    combined_env_map = DEFAULT_LATEX_ENV_TO_LEAN_KEYWORD.copy() # Start with defaults
    try:
        # Configure logger for preamble processing
        preamble_logger = logging.getLogger("process_preamble")
        preamble_logger.setLevel(logger.level)

        custom_newtheorem_map = extract_newtheorem_mappings(preamble, logger=preamble_logger)

        if custom_newtheorem_map:
            combined_env_map.update(custom_newtheorem_map)
            logger.info("Found and merged %d custom theorem-like environment mapping(s).", len(custom_newtheorem_map))
            logger.debug("Combined environment map: %s", combined_env_map)
        else:
            logger.info("No custom theorem-like environments found in preamble, using defaults.")
    except Exception as exc:
        logger.exception("An error occurred during preamble processing: %s. Proceeding with default/existing mappings.", exc)


    # --- STEP 5: Translate the *Extracted Body* AST ---
    logger.info("Translating the extracted *body* AST to Lean-like text...")
    translated: Optional[str] = None
    try:
        # Configure logger for translation process
        translation_logger = logging.getLogger("ast_to_lean")
        translation_logger.setLevel(logger.level)

        # Call the translator, passing ONLY the body nodelist
        translated = latex_to_lean_symbols(
            environment_map=combined_env_map,
            nodelist_in=body_nodelist, # Pass the extracted body AST
            tolerant_parsing=args.tolerant_parsing
        )
    except Exception as exc:
        logger.exception("An unexpected error occurred during translation: %s", exc)

    # --- STEP 6: Write Output ---
    if translated is None:
        logger.critical("Translation failed (check logs for details) – aborting.")
        sys.exit(1)

    logger.info("Translation successful. Writing output to %s", args.output_txt_path)
    try:
        # Ensure output directory exists before writing
        output_dir = args.output_txt_path.parent
        output_dir.mkdir(parents=True, exist_ok=True)
        logger.debug("Ensured output directory exists: %s", output_dir)

        args.output_txt_path.write_text(translated, encoding="utf-8")
        logger.info("Write complete.")
    except OSError as exc:
        logger.critical("Cannot write output file %s: %s", args.output_txt_path, exc)
        sys.exit(1)
    except Exception as exc:
        logger.exception("An unexpected error occurred writing the output file: %s", exc)
        sys.exit(1)

    # Final success message to console
    print(f"\nProcessing complete. Output written to {args.output_txt_path}")


# --- Script Execution Entry Point ---
if __name__ == "__main__":
    main()