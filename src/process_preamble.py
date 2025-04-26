# process_preamble.py

r"""
Extracts `\newtheorem` definitions from a LaTeX preamble string using regex.

This module specifically targets `\newtheorem` commands within a given string
(typically the LaTeX preamble) and extracts the mapping between the defined
environment name and its printed name (e.g., 'theorem' -> 'Theorem').

It uses regular expressions for this task and does *not* perform full AST parsing.
This approach is suitable for capturing standard `\newtheorem` definitions commonly
found in preambles but may not handle highly complex or unusual LaTeX constructions.

Functions exported
------------------
extract_newtheorem_mappings(preamble: str, logger: Optional[logging.Logger] = None) -> Dict[str, str]
    Parses the preamble string to find `\newtheorem` commands and returns a
    dictionary mapping the internal environment name to the printed name.
"""
from __future__ import annotations # Ensure compatibility with type hints

import logging
import re
from typing import Dict, Optional

# --- Regular Expression for \newtheorem ---
# Captures the environment name and the printed name.
# Handles optional * and optional counter reset argument [...] which are ignored.
_NEWTHEOREM_REGEX = re.compile(
    r"""
    \\newtheorem \s* (?:\* \s*)?         # Command, optional space, optional star and space
    \{ \s* (?P<env_name>[^}]+) \s* \}    # { environment_name } (allowing internal spaces)
    (?: \s* \[ [^\]]+ \] \s* )?         # Optional counter reset [...] - ignored
    \{ \s* (?P<printed>[^}]+) \s* \}    # { Printed Name } (allowing internal spaces)
    """,
    re.VERBOSE,  # Allow comments and ignore whitespace in the pattern
)


# --- Public Function ---

def extract_newtheorem_mappings(
    preamble: str,
    logger: Optional[logging.Logger] = None
) -> Dict[str, str]:
    r"""Parses the preamble string to find `\newtheorem` definitions via regex.

    Uses regular expressions to identify lines like:
    `\newtheorem{theorem}{Theorem}`
    `\newtheorem*{lemma}{Lemma}`
    `\newtheorem{corollary}[theorem]{Corollary}`

    It extracts the mapping from the internal environment name (e.g., 'theorem')
    to the text that is printed (e.g., 'Theorem'). This mapping is typically
    used to translate LaTeX environments like `\begin{theorem}` into corresponding
    keywords in another format (e.g., Lean's `theorem`).

    Args:
        preamble: The string containing the LaTeX preamble content.
        logger: An optional logging.Logger instance. If None, a default logger
                for this module will be used.

    Returns:
        A dictionary where keys are the defined environment names (str) and
        values are their corresponding printed names (str). Returns an empty
        dictionary if no `\newtheorem` definitions are found or if the input
        string is empty.
    """
    # Initialize logger if not provided
    if logger is None:
        logger = logging.getLogger(__name__)
        # Configure basic logging if the logger hasn't been configured elsewhere
        if not logger.hasHandlers():
            logging.basicConfig(level=logging.INFO, format='%(name)s - %(levelname)s: %(message)s')

    # Initialize dictionary to store mappings
    mappings: Dict[str, str] = {}

    if not preamble:
        logger.info("Preamble string is empty. No newtheorem definitions to extract.")
        return mappings

    logger.debug("Scanning preamble string for \\newtheorem definitions using regex...")

    # Iterate through all non-overlapping matches found by the regex
    match_count = 0
    for match in _NEWTHEOREM_REGEX.finditer(preamble):
        match_count += 1
        try:
            # Extract captured groups, stripping leading/trailing whitespace
            env_name = match.group("env_name").strip()
            printed_name = match.group("printed").strip()

            # Ensure both parts were captured and are non-empty
            if env_name and printed_name:
                if env_name in mappings:
                    # Log if an environment name is redefined within the preamble scan
                    logger.warning(
                        "Redefinition of newtheorem environment '%s' encountered "
                        "in preamble scan. Using the latest definition ('%s').",
                        env_name, printed_name
                    )
                mappings[env_name] = printed_name
                logger.debug("Found mapping via regex: '%s' -> '%s'", env_name, printed_name)
            else:
                # Log if extraction failed despite a pattern match (e.g., empty group content)
                logger.warning(
                    "Found \\newtheorem pattern matching '%s' but could not extract "
                    "valid env_name or printed_name.", match.group(0).strip()
                )
        except IndexError:
            # Should not happen with named groups, but included as a safeguard
            logger.error(
                "IndexError while processing regex match group for '%s'. Skipping this match.",
                match.group(0).strip(), exc_info=True
            )
        except Exception as e:
            # Catch any other unexpected errors during the processing of a single match
            logger.error(
                "Unexpected error processing regex match '%s': %s. Skipping this match.",
                match.group(0).strip(), e, exc_info=True
            )

    # Log summary after iterating through all potential matches
    if mappings:
        logger.info("Found %d valid \\newtheorem definition(s) via regex.", len(mappings))
    elif match_count > 0:
         logger.info("Found %d \\newtheorem patterns via regex, but none yielded valid mappings.", match_count)
    else:
        logger.info("No \\newtheorem patterns found in the preamble string via regex.")

    return mappings


# --- Example Usage (if run directly) ---
if __name__ == '__main__':
    # Configure logging specifically for direct execution example
    logging.basicConfig(level=logging.DEBUG, format='%(name)s - %(levelname)s: %(message)s')
    main_logger = logging.getLogger(__name__)

    # Example preamble content
    example_preamble = r"""
    \documentclass{article}
    \usepackage{amsmath, amsthm} % amsthm might define its own, but we look for \newtheorem

    % Standard definitions
    \newtheorem{theorem}{Theorem}[section] % With counter reset
    \newtheorem{lemma}[theorem]{Lemma}     % Sharing counter
    \newtheorem*{remark}{Remark}           % Starred version
    \newtheorem{corollary}{Corollary}       % Simple case
    \newtheorem{ defn }{Definition}        % With extra spaces

    % Some other commands that should be ignored by this module
    \newcommand{\R}{\mathbb{R}}
    \DeclareMathOperator{\id}{id}
    \newcommand{\Foo}{bar}

    % A potentially tricky case (if regex wasn't careful)
    % \newtheorem{problem}{Problem Session \number} % Body containing macro - NOT matched by current regex safely

    \begin{document} % Regex runs on whole string, but only \newtheorem matters
    Some text here.
    \end{document}
    """

    main_logger.info("--- Running Direct Example ---")
    main_logger.info("Input Preamble:\n%s", example_preamble)

    # Call the function to extract mappings
    found_mappings = extract_newtheorem_mappings(example_preamble, logger=main_logger)

    main_logger.info("--- Extracted Mappings ---")
    if found_mappings:
        # Pretty print the resulting dictionary
        import json
        main_logger.info(json.dumps(found_mappings, indent=2))
    else:
        main_logger.info("No mappings extracted.")

    main_logger.info("--- Direct Example Complete ---")