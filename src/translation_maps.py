# translation_maps.py

"""
Contains constant mappings used for LaTeX to Lean translation.
Includes symbol maps, font maps, and default environment mappings.
"""

from typing import Dict

# --- Symbol Substitution Map ---
SYMBOL_MAP: Dict[str, str] = {
    # --- Greek Lowercase ---
    'alpha': 'α', 'beta': 'β', 'gamma': 'γ', 'delta': 'δ', 'epsilon': 'ε',
    'zeta': 'ζ', 'eta': 'η', 'theta': 'θ', 'iota': 'ι', 'kappa': 'κ',
    'lambda': 'λ', 'mu': 'μ', 'nu': 'ν', 'xi': 'ξ', 'omicron': 'ο',
    'pi': 'π', 'rho': 'ρ', 'sigma': 'σ', 'tau': 'τ', 'upsilon': 'υ',
    'phi': 'φ', 'chi': 'χ', 'psi': 'ψ', 'omega': 'ω',
    # --- Greek Variants ---
    'varepsilon': 'ɛ', 'vartheta': 'ϑ', 'varpi': 'ϖ', 'varrho': 'ϱ',
    'varsigma': 'ς', 'varphi': 'ϕ',
    # --- Greek Uppercase ---
    'Gamma': 'Γ', 'Delta': 'Δ', 'Theta': 'Θ', 'Lambda': 'Λ', 'Xi': 'Ξ',
    'Pi': 'Π', 'Sigma': 'Σ', 'Upsilon': 'Υ', 'Phi': 'Φ', 'Psi': 'Ψ',
    'Omega': 'Ω',

    # --- Relations ---
    'in': '∈', 'ni': '∋', 'notin': '∉', 'owns': '∋', # \owns is same as \ni
    'subset': '⊂', 'supset': '⊃', 'subseteq': '⊆', 'supseteq': '⊇',
    'subsetneq': '⊊', 'supsetneq': '⊋', 'sqsubset': '⊏', 'sqsupset': '⊐',
    'sqsubseteq': '⊑', 'sqsupseteq': '⊒',
    'leq': '≤', 'le': '≤', 'geq': '≥', 'ge': '≥',
    'll': '≪', 'gg': '≫',
    'prec': '≺', 'succ': '≻', 'preceq': '≼', 'succeq': '≽',
    'equiv': '≡', 'approx': '≈', 'simeq': '≃', 'sim': '∼', 'asymp': '≍',
    'cong': '≅', 'neq': '≠', 'ne': '≠', 'doteq': '≐',
    'propto': '∝',
    'models': '⊨', 'vdash': '⊢', 'dashv': '⊣',
    'perp': '⊥', 'parallel': '∥',
    'mid': '∣', 'nmid': '∤',

    # --- Set Theory & Logic ---
    'cup': '∪', 'cap': '∩', 'setminus': '∖', 'emptyset': '∅',
    'varnothing': '⌀', # Alternative empty set
    'bigcup': '⋃', 'bigcap': '⋂', 'bigsqcup': '⨆', 'bigsqcap': '⨅',
    'forall': '∀', 'exists': '∃', 'nexists': '∄',
    'neg': '¬', 'lnot': '¬',
    'land': '∧', 'wedge': '∧', 'lor': '∨', 'vee': '∨',
    'top': '⊤', 'bot': '⊥', # \bot is same as \perp
    'therefore': '∴', 'because': '∵',

    # --- Arrows ---
    'implies': '→', 'impliedby': '←', 'iff': '↔', 'Leftrightarrow': '⇔',
    'to': '→', 'rightarrow': '→', 'longrightarrow': '⟶',
    'gets': '←', 'leftarrow': '←', 'longleftarrow': '⟵',
    'mapsto': '↦', 'longmapsto': '⟼',
    'leftrightarrow': '↔', 'longleftrightarrow': '⟷',
    'uparrow': '↑', 'downarrow': '↓', 'updownarrow': '↕',
    'Uparrow': '⇑', 'Downarrow': '⇓', 'Updownarrow': '⇕',
    'nearrow': '↗', 'searrow': '↘', 'swarrow': '↙', 'nwarrow': '↖',
    'rightharpoonup': '⇀', 'rightharpoondown': '⇁',
    'leftharpoonup': '↼', 'leftharpoondown': '↽',
    'upharpoonleft': '↿', 'upharpoonright': '↾',
    'downharpoonleft': '⇃', 'downharpoonright': '⇂',
    'rightleftharpoons': '⇌', 'leftrightharpoons': '⇋', # Often used for equilibrium
    'hookrightarrow': '↪', 'hookleftarrow': '↩',

    # --- Operators & Functions (Output as text) ---
    'inf': 'inf', 'sup': 'sup', 'lim': 'lim', 'liminf': 'liminf',
    'limsup': 'limsup', 'max': 'max', 'min': 'min', 'log': 'log',
    'ln': 'ln', 'exp': 'exp', 'sin': 'sin', 'cos': 'cos', 'tan': 'tan',
    'sec': 'sec', 'csc': 'csc', 'cot': 'cot', 'arcsin': 'arcsin',
    'arccos': 'arccos', 'arctan': 'arctan', 'sinh': 'sinh', 'cosh': 'cosh',
    'tanh': 'tanh', 'coth': 'coth', 'det': 'det', 'gcd': 'gcd', 'Pr': 'Pr',
    'dim': 'dim', 'ker': 'ker', 'deg': 'deg', 'arg': 'arg', 'hom': 'hom',
    'Hom': 'Hom', 'End': 'End', 'Aut': 'Aut', 'im': 'im', # For image of a map
    'mod': 'mod', # E.g., a \mod n
    'injlim': 'injlim', 'projlim': 'projlim', 'varinjlim': 'varinjlim',
    'varprojlim': 'varprojlim',
    'ad': 'ad',

    # --- Calculus & Large Operators ---
    'sum': '∑', 'prod': '∏', 'coprod': '∐', # Coproduct
    'int': '∫', 'iint': '∬', 'iiint': '∭', 'oint': '∮',
    'oiint': '∯', 'oiiint': '∰', # Surface/Volume integrals (requires amsmath)
    'partial': '∂', 'nabla': '∇',

    # --- Dots & Misc Symbols ---
    'dots': '…', 'ldots': '…', 'cdots': '⋯', 'vdots': '⋮', 'ddots': '⋱',
    'infty': '∞', 'pm': '±', 'mp': '∓', 'times': '×', 'div': '÷',
    'cdot': '·', 'ast': '*', 'star': '⋆', 'circ': '∘', 'bullet': '∙',
    'oplus': '⊕', 'ominus': '⊖', 'otimes': '⊗', 'oslash': '⊘', 'odot': '⊙',
    # 'circ': '∘', # Already present # Degree symbol or composition
    'angle': '∠', 'measuredangle': '∡', 'triangle': '△',
    'prime': "'", 'hbar': 'ℏ', 'wp': '℘', # Weierstrass p
    'ell': 'ℓ', # Script l
    'imath': 'ı', # Dotless i
    'jmath': 'ȷ', # Dotless j
    'Re': 'Re', # Real part
    'Im': 'Im', # Imaginary part
    'aleph': 'ℵ', 'beth': 'ℶ', 'gimel': 'ℷ', 'daleth': 'ℸ', # Hebrew letters
    'clubsuit': '♣', 'diamondsuit': '♢', 'heartsuit': '♡', 'spadesuit': '♠',
    'surd': '√', # Square root symbol itself (sqrt macro handles arguments)
    'blacksquare': '■', 'square': '□', 'diamond': '◇',

    # --- Internal Use ---
    'label': '', # Labels handled by environment logic
}

# --- Font Mapping Dictionaries ---
BLACKBOARD_BOLD_MAP: Dict[str, str] = {
    'A': '𝔸', 'B': '𝔹', 'C': 'ℂ', 'D': '𝔻', 'E': '𝔼', 'F': '𝔽', 'G': '𝔾',
    'H': 'ℍ', 'I': '𝕀', 'J': '𝕁', 'K': '𝕂', 'L': '𝕃', 'M': '𝕄', 'N': 'ℕ',
    'O': '𝕆', 'P': 'ℙ', 'Q': 'ℚ', 'R': 'ℝ', 'S': '𝕊', 'T': '𝕋', 'U': '𝕌',
    'V': '𝕍', 'W': '𝕎', 'X': '𝕏', 'Y': '𝕐', 'Z': 'ℤ',
}

SCRIPT_MAP: Dict[str, str] = {
    'A': '𝒜', 'B': 'ℬ', 'C': '𝒞', 'D': '𝒟', 'E': 'ℰ', 'F': 'ℱ', 'G': '𝒢',
    'H': 'ℋ', 'I': 'ℐ', 'J': '𝒥', 'K': '𝒦', 'L': 'ℒ', 'M': 'ℳ', 'N': '𝒩',
    'O': '𝒪', 'P': '𝒫', 'Q': '𝒬', 'R': 'ℛ', 'S': '𝒮', 'T': '𝒯', 'U': '𝒰',
    'V': '𝒱', 'W': '𝒲', 'X': '𝒳', 'Y': '𝒴', 'Z': '𝒵',
}

# --- Unicode Subscript Map ---
SUBSCRIPT_MAP: Dict[str, str] = {
    "0": "₀", "1": "₁", "2": "₂", "3": "₃", "4": "₄", "5": "₅",
    "6": "₆", "7": "₇", "8": "₈", "9": "₉",
    "a": "ₐ", "e": "ₑ", "h": "ₕ", "i": "ᵢ", "j": "ⱼ", "k": "ₖ",
    "l": "ₗ", "m": "ₘ", "n": "ₙ", "o": "ₒ", "p": "ₚ", "r": "ᵣ",
    "s": "ₛ", "t": "ₜ", "u": "ᵤ", "v": "ᵥ", "x": "ₓ",
    "+": "₊", "-": "₋", "−": "₋", "=": "₌", "(": "₍", ")": "₎",
    "β": "ᵦ", "γ": "ᵧ", "ρ": "ᵨ", "φ": "ᵩ", "χ": "ᵪ",
}

# --- Default Environment Mapping Dictionary ---
# This defines the standard translations. Custom ones from the preamble will be merged.
DEFAULT_LATEX_ENV_TO_LEAN_KEYWORD: Dict[str, str] = {
    'theorem': 'theorem',
    'proposition': 'theorem', # Often propositions are proven like theorems in Lean
    'lemma': 'lemma',
    'corollary': 'corollary',
    'definition': 'def',    # Map definition environments to Lean's 'def'
    'example': 'example',
    'remark': 'remark',
    # Note: 'proof', 'align', 'align*' are handled specially by logic, not just mapping.
}