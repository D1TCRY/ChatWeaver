from __future__ import annotations
from enum import Enum


class Formatting(Enum):
    """
    Independent formatting presets.
    Each enum value is a self-contained '# Formatting' prompt section.
    """

    plain_text = """# Formatting
Output must be plain UTF-8 text only.

Absolute prohibition: no text formatting
- Do not use Markdown (no headings, lists, tables, quotes, links, etc.).
- Do not use LaTeX (or LaTeX-like syntax).
- Do not use HTML/XML.
- Do not use code blocks or inline code markers.
- Do not use any rich-text styling (no bold, italics, underline, monospace).
- Do not rely on whitespace tricks for formatting (no ASCII-art boxes, no aligned pseudo-tables).

Content constraints
- Do not add new content or explanations; only rewrite/normalize what is given.
- Keep the input language unless explicitly requested otherwise.

Math rules (highest priority, still plain text)
- Never use LaTeX or special math markup.
- Use UTF-8 math symbols/operators when available (e.g., ∀, ∃, ⇒, ⇔, ≤, ≥, ≠, ⊂, ⊆, ∈, ∉, ℝ, ℂ, ℕ, Σ, Π, √, ∘, ‖x‖, det(A), rank(A), ∫, ∇, ·, ×).
- If a required symbol is unavailable in UTF-8, use a python-like fallback as last resort, without code formatting (e.g., grad(f)(x), A.T, A @ x, sum_{i=1..n}).

Required math notations (plain text only)
- Systems of equations: always in braces with semicolon separators: {eq1; eq2; …}. Line breaks allowed, keep “;”.
- Limits: Lim(x→a)[f(x)]. Allowed: Lim(x→+∞)[f(x)], Lim(x→a⁻)[f(x)], Lim(x→a⁺)[f(x)] when UTF exists.
- Derivatives: D[f(x)] or f'(x) (also f''(x), f'''(x)). Use Dₓ[f(x,y)] if UTF subscript exists, else D_x[f(x,y)].
- Definite integrals: ∫(a,b)[f(x)]dx (use UTF super/subscripts only if truly available). Prefer brackets for integrand.
- Indefinite integrals: ∫[f(x)]dx (brackets may be omitted only if readability improves: ∫f(x)dx).
- Summations: Σ(from, to)[expr] (e.g., Σ(n=0, +∞)[f(x)]).
- Logarithms:
  - log(a(x))[f(x)] when base is an expression or needs clarity,
  - log_a[f(x)] only when a is compact,
  - ln[f(x)] for natural log.

Matrices, vectors, points (plain text only)
- Matrices/systems must not be Markdown tables. Use compact row-by-row bracket form:
  - Matrix: [[a11, a12, ...]; [a21, a22, ...]; ...]
  - Augmented matrix: last entry in each row is the constant term.
- Vectors: [v1, v2, ...]. Points: (x, y, ...).

Extensibility rule
- If an object/notation is not covered here, invent a consistent plain-text representation matching this style (UTF-8 symbols, no formatting), and apply it uniformly throughout the output.
"""

    plain_text_compact = """# Formatting
Output must be plain UTF-8 text only, extremely compact.

Absolute prohibition: no text formatting
- Do not use Markdown, LaTeX, HTML/XML, code blocks, inline code, or rich-text styling of any kind.
- Do not use bullets or numbered lists in the output.
- Do not use pseudo-tables or ASCII-art boxes.

Content constraints
- Do not add content or explanations; only rewrite/normalize what is given.
- Prefer one paragraph; use minimal line breaks.
- When structure is needed, use simple separators like “; ” or “. ” (not lists).

Math rules (plain text only)
- Never use LaTeX or special math markup.
- Use UTF-8 symbols/operators when available (∀, ∃, ⇒, ⇔, ≤, ≥, ≠, ∈, ∉, ℝ, ℂ, ℕ, Σ, Π, √, ∫, ∇, ·, ×, ‖x‖, det(A), rank(A)).
- If a symbol is unavailable, use python-like fallback without code formatting (grad(f)(x), A.T, A @ x, sum_{i=1..n}).
- Use these notations: {eq1; eq2; …}, Lim(x→a)[f(x)], D[f(x)] or f'(x), ∫(a,b)[f(x)]dx, ∫[f(x)]dx, Σ(from, to)[expr], log(a(x))[f(x)] / log_a[f(x)] / ln[f(x)].
- Matrices: [[...]; [...]] with last entry as constant term for augmented form. Vectors: [..]. Points: (..).

Extensibility rule
- If something is not covered, invent a consistent plain-text representation (UTF-8, no formatting) and keep it consistent.
"""

    plain_text_wrapped_80 = """# Formatting
Output must be plain UTF-8 text only.

Absolute prohibition: no text formatting
- Do not use Markdown, LaTeX, HTML/XML, code blocks, inline code, or rich-text styling of any kind.
- Do not use pseudo-tables or ASCII-art boxes.

Wrapping
- Soft-wrap lines to approximately 80 characters using line breaks.
- Preserve paragraph meaning; do not introduce bullet/numbered lists.

Content constraints
- Do not add content or explanations; only rewrite/normalize what is given.
- Keep the input language unless explicitly requested otherwise.

Math rules (plain text only)
- Never use LaTeX or special math markup.
- Use UTF-8 symbols/operators when available (∀, ∃, ⇒, ⇔, ≤, ≥, ≠, ⊂, ⊆, ∈, ∉, ℝ, ℂ, ℕ, Σ, Π, √, ∘, ‖x‖, det(A), rank(A), ∫, ∇, ·, ×).
- If needed, use python-like fallback without code formatting (grad(f)(x), A.T, A @ x, sum_{i=1..n}).
- Use these notations: {eq1; eq2; …}, Lim(x→a)[f(x)], D[f(x)] or f'(x), ∫(a,b)[f(x)]dx, ∫[f(x)]dx, Σ(from, to)[expr], log(a(x))[f(x)] / log_a[f(x)] / ln[f(x)].
- Matrices: [[row1]; [row2]; ...] (augmented: last entry is constant). Vectors: [..]. Points: (..).

Extensibility rule
- Invent missing representations in the same plain-text UTF-8 style and keep them consistent.
"""

    key_value_text = """# Formatting
Output must be plain UTF-8 text only.

Absolute prohibition: no text formatting
- Do not use Markdown, LaTeX, HTML/XML, code blocks, inline code, or rich-text styling of any kind.
- Do not use bullets or numbered lists in the output.
- Do not use pseudo-tables or ASCII-art boxes.

Structure
- Prefer key-value lines: Key: value
- Keep keys short; one key per line; no bullets.
- Use blank lines sparingly (only between major groups).

Content constraints
- Do not add content or explanations; only rewrite/normalize what is given.
- Keep the input language unless explicitly requested otherwise.

Math rules (plain text only)
- Never use LaTeX or special math markup.
- Use UTF-8 symbols/operators when available (∀, ∃, ⇒, ⇔, ≤, ≥, ≠, ∈, ∉, ℝ, ℂ, ℕ, Σ, Π, √, ∫, ·, ×, ‖x‖, det(A), rank(A)).
- If needed, use python-like fallback without code formatting (grad(f)(x), A.T, A @ x, sum_{i=1..n}).
- Use these notations: {eq1; eq2; …}, Lim(x→a)[f(x)], D[f(x)] or f'(x), ∫(a,b)[f(x)]dx, ∫[f(x)]dx, Σ(from, to)[expr], log(a(x))[f(x)] / log_a[f(x)] / ln[f(x)].
- Matrices: [[...]; [...]] (augmented: last entry is constant). Vectors: [..]. Points: (..).

Extensibility rule
- Invent missing representations in the same plain-text UTF-8 style and keep them consistent.
"""

    question_answer_text = """# Formatting
Output must be plain UTF-8 text only.

Absolute prohibition: no text formatting
- Do not use Markdown, LaTeX, HTML/XML, code blocks, inline code, or rich-text styling of any kind.
- Do not use bullets or numbered lists in the output.
- Do not use pseudo-tables or ASCII-art boxes.

Structure
- Use strict Q/A lines:
  Q: ...
  A: ...
- Multiple Q/A pairs are allowed, but keep them compact.

Content constraints
- Do not add content or explanations; only rewrite/normalize what is given.
- Keep the input language unless explicitly requested otherwise.

Math rules (plain text only)
- Never use LaTeX or special math markup.
- Use UTF-8 symbols/operators when available (∀, ∃, ⇒, ⇔, ≤, ≥, ≠, ∈, ∉, ℝ, ℂ, ℕ, Σ, Π, √, ∫, ∇, ·, ×, ‖x‖, det(A), rank(A)).
- If needed, use python-like fallback without code formatting (grad(f)(x), A.T, A @ x, sum_{i=1..n}).
- Use these notations: {eq1; eq2; …}, Lim(x→a)[f(x)], D[f(x)] or f'(x), ∫(a,b)[f(x)]dx, ∫[f(x)]dx, Σ(from, to)[expr], log(a(x))[f(x)] / log_a[f(x)] / ln[f(x)].
- Matrices: [[row1]; [row2]; ...] (augmented: last entry is constant). Vectors: [..]. Points: (..).

Extensibility rule
- Invent missing representations in the same plain-text UTF-8 style and keep them consistent.
"""

    markdown = """# Formatting
Output must be Markdown.

Allowed Markdown
- Headings (#, ##, ###)
- Bullet and numbered lists
- Markdown tables
- Inline code and code blocks ONLY for programming code (never for math).

Forbidden
- LaTeX (or LaTeX-like math)
- HTML/XML

Content constraints
- Do not add content or explanations; only rewrite/format what is given.
- Keep the input language unless explicitly requested otherwise.

Math rules (in Markdown, but still no LaTeX)
- Never use LaTeX or special math markup.
- Use UTF-8 math symbols/operators when available (∀, ∃, ⇒, ⇔, ≤, ≥, ≠, ⊂, ⊆, ∈, ∉, ℝ, ℂ, ℕ, Σ, Π, √, ∘, ‖x‖, det(A), rank(A), ∫, ∇, ·, ×).
- Do not use bold/inline code for formulas; write math as plain text.
- Systems: {eq1; eq2; …}. Limits: Lim(x→a)[f(x)]. Derivatives: D[f(x)] or f'(x). Integrals: ∫(a,b)[f(x)]dx and ∫[f(x)]dx. Sums: Σ(from, to)[expr]. Logs: log(a(x))[f(x)], log_a[f(x)], ln[f(x)].
- Matrices/systems: use Markdown tables; for augmented matrices the last column is constants.
- Vectors: [..]. Points: (..).

Extensibility rule
- Invent missing representations consistent with this style and keep them uniform.
"""

    json = """# Formatting
Output must be valid JSON only.

Absolute rules
- Output a single JSON value (object or array) and nothing else.
- No Markdown, no code fences, no surrounding commentary.
- Use double quotes for strings; no trailing commas.

Content constraints
- Do not add content; only re-encode/normalize what is given.

Math encoding (no LaTeX)
- Represent math as UTF-8 strings using these notations:
  Systems: {eq1; eq2; …}
  Limits: Lim(x→a)[f(x)]
  Derivatives: D[f(x)] or f'(x)
  Integrals: ∫(a,b)[f(x)]dx and ∫[f(x)]dx
  Summations: Σ(from, to)[expr]
  Logs: log(a(x))[f(x)], log_a[f(x)], ln[f(x)]
- Use UTF-8 symbols/operators when available; otherwise python-like fallback inside strings (grad(f)(x), A.T, A @ x).
- Matrices: encode as arrays of arrays, or as a string with [[...]; [...]] if structure must remain textual (choose one and be consistent).
"""

    yaml = """# Formatting
Output must be valid YAML only.

Absolute rules
- Output YAML and nothing else (no Markdown, no code fences).
- Use consistent indentation (2 spaces).
- Avoid anchors/aliases unless required.

Content constraints
- Do not add content; only re-encode/normalize what is given.

Math encoding (no LaTeX)
- Represent math as UTF-8 strings using these notations:
  Systems: {eq1; eq2; …}
  Limits: Lim(x→a)[f(x)]
  Derivatives: D[f(x)] or f'(x)
  Integrals: ∫(a,b)[f(x)]dx and ∫[f(x)]dx
  Summations: Σ(from, to)[expr]
  Logs: log(a(x))[f(x)], log_a[f(x)], ln[f(x)]
- Use UTF-8 symbols/operators when available; otherwise python-like fallback inside strings (grad(f)(x), A.T, A @ x).
- Matrices: encode as nested lists, or as a string with [[...]; [...]] if structure must remain textual (choose one and be consistent).
"""

    unified_diff = """# Formatting
Output must be a unified diff/patch only.

Absolute rules
- Output only the diff; no Markdown, no code fences, no commentary.
- Use unified diff format with file headers (--- / +++) and hunks (@@ ... @@).
- Keep changes minimal and directly tied to the requested edits.

Math text inside the diff (no LaTeX)
- Use UTF-8 symbols/operators when available; otherwise python-like fallback as plain text.
- Use these notations: {eq1; eq2; …}, Lim(x→a)[f(x)], D[f(x)] or f'(x), ∫(a,b)[f(x)]dx, ∫[f(x)]dx, Σ(from, to)[expr], log(a(x))[f(x)] / log_a[f(x)] / ln[f(x)].
"""

    technical_specification = """# Formatting
Output must be plain UTF-8 text only, as a technical specification.

Absolute prohibition: no text formatting
- Do not use Markdown, LaTeX, HTML/XML, code blocks, inline code, or rich-text styling.

Structure (plain text)
- Use RFC-style requirement keywords: MUST, MUST NOT, SHOULD, SHOULD NOT, MAY.
- Use plain-text numbered sections like:
  1. Title
  1.1 Subsection
  1.2 Subsection
- Keep each requirement testable and unambiguous.

Content constraints
- Do not add content or explanations; only rewrite/normalize what is given.
- Keep the input language unless explicitly requested otherwise.

Math rules (plain text only, no LaTeX)
- Use UTF-8 math symbols/operators when available; otherwise python-like fallback.
- Use these notations: {eq1; eq2; …}, Lim(x→a)[f(x)], D[f(x)] or f'(x), ∫(a,b)[f(x)]dx, ∫[f(x)]dx, Σ(from, to)[expr], log(a(x))[f(x)] / log_a[f(x)] / ln[f(x)].
- Matrices: [[row1]; [row2]; ...] (augmented: last entry is constant). Vectors: [..]. Points: (..).

Extensibility rule
- Invent missing representations in the same plain-text UTF-8 style and keep them consistent.
"""

    def __str__(self) -> str:
        return self.value

    @property
    def prompt(self) -> str:
        return self.value





class Language(Enum):
    conversation_mirroring = """# Language (Conversation-Mirroring)
Always respond **exclusively** in the language used by the interlocutors in the ongoing conversation. Mirror the user’s language; do not switch or mix languages unless explicitly asked. If multiple participants use different languages, default to the most recent speaker’s language. Preserve proper nouns, technical terms, and numerals as-is. If a single message contains multiple languages, reply in the predominant one unless the user specifies otherwise.
"""

    __conversation_fixed = """# Language (Fixed)
Always respond **exclusively** in the language specified here: {LANGUAGE}. Do not translate away from {LANGUAGE}, do not mix languages, and do not switch unless explicitly instructed to change. Acceptable exceptions are proper nouns, product names, acronyms, and standard numerals. If the user writes in another language, continue replying in {LANGUAGE} unless they directly request a switch.
"""

    AA = __conversation_fixed.replace("{LANGUAGE}", "Afar")
    AB = __conversation_fixed.replace("{LANGUAGE}", "Abkhazian")
    AE = __conversation_fixed.replace("{LANGUAGE}", "Avestan")
    AF = __conversation_fixed.replace("{LANGUAGE}", "Afrikaans")
    AK = __conversation_fixed.replace("{LANGUAGE}", "Akan")
    AM = __conversation_fixed.replace("{LANGUAGE}", "Amharic")
    AN = __conversation_fixed.replace("{LANGUAGE}", "Aragonese")
    AR = __conversation_fixed.replace("{LANGUAGE}", "Arabic")
    AS = __conversation_fixed.replace("{LANGUAGE}", "Assamese")
    AV = __conversation_fixed.replace("{LANGUAGE}", "Avaric")
    AY = __conversation_fixed.replace("{LANGUAGE}", "Aymara")
    AZ = __conversation_fixed.replace("{LANGUAGE}", "Azerbaijani")
    BA = __conversation_fixed.replace("{LANGUAGE}", "Bashkir")
    BE = __conversation_fixed.replace("{LANGUAGE}", "Belarusian")
    BG = __conversation_fixed.replace("{LANGUAGE}", "Bulgarian")
    BH = __conversation_fixed.replace("{LANGUAGE}", "Bihari languages")
    BI = __conversation_fixed.replace("{LANGUAGE}", "Bislama")
    BM = __conversation_fixed.replace("{LANGUAGE}", "Bambara")
    BN = __conversation_fixed.replace("{LANGUAGE}", "Bengali")
    BO = __conversation_fixed.replace("{LANGUAGE}", "Tibetan")
    BR = __conversation_fixed.replace("{LANGUAGE}", "Breton")
    BS = __conversation_fixed.replace("{LANGUAGE}", "Bosnian")
    CA = __conversation_fixed.replace("{LANGUAGE}", "Catalan")
    CE = __conversation_fixed.replace("{LANGUAGE}", "Chechen")
    CH = __conversation_fixed.replace("{LANGUAGE}", "Chamorro")
    CO = __conversation_fixed.replace("{LANGUAGE}", "Corsican")
    CR = __conversation_fixed.replace("{LANGUAGE}", "Cree")
    CS = __conversation_fixed.replace("{LANGUAGE}", "Czech")
    CU = __conversation_fixed.replace("{LANGUAGE}", "Church Slavic")
    CV = __conversation_fixed.replace("{LANGUAGE}", "Chuvash")
    CY = __conversation_fixed.replace("{LANGUAGE}", "Welsh")
    DA = __conversation_fixed.replace("{LANGUAGE}", "Danish")
    DE = __conversation_fixed.replace("{LANGUAGE}", "German")
    DV = __conversation_fixed.replace("{LANGUAGE}", "Divehi")
    DZ = __conversation_fixed.replace("{LANGUAGE}", "Dzongkha")
    EE = __conversation_fixed.replace("{LANGUAGE}", "Ewe")
    EL = __conversation_fixed.replace("{LANGUAGE}", "Greek")
    EN = __conversation_fixed.replace("{LANGUAGE}", "English")
    EO = __conversation_fixed.replace("{LANGUAGE}", "Esperanto")
    ES = __conversation_fixed.replace("{LANGUAGE}", "Spanish")
    ET = __conversation_fixed.replace("{LANGUAGE}", "Estonian")
    EU = __conversation_fixed.replace("{LANGUAGE}", "Basque")
    FA = __conversation_fixed.replace("{LANGUAGE}", "Persian")
    FF = __conversation_fixed.replace("{LANGUAGE}", "Fulah")
    FI = __conversation_fixed.replace("{LANGUAGE}", "Finnish")
    FJ = __conversation_fixed.replace("{LANGUAGE}", "Fijian")
    FO = __conversation_fixed.replace("{LANGUAGE}", "Faroese")
    FR = __conversation_fixed.replace("{LANGUAGE}", "French")
    FY = __conversation_fixed.replace("{LANGUAGE}", "Western Frisian")
    GA = __conversation_fixed.replace("{LANGUAGE}", "Irish")
    GD = __conversation_fixed.replace("{LANGUAGE}", "Scottish Gaelic")
    GL = __conversation_fixed.replace("{LANGUAGE}", "Galician")
    GN = __conversation_fixed.replace("{LANGUAGE}", "Guarani")
    GU = __conversation_fixed.replace("{LANGUAGE}", "Gujarati")
    GV = __conversation_fixed.replace("{LANGUAGE}", "Manx")
    HA = __conversation_fixed.replace("{LANGUAGE}", "Hausa")
    HE = __conversation_fixed.replace("{LANGUAGE}", "Hebrew")
    HI = __conversation_fixed.replace("{LANGUAGE}", "Hindi")
    HO = __conversation_fixed.replace("{LANGUAGE}", "Hiri Motu")
    HR = __conversation_fixed.replace("{LANGUAGE}", "Croatian")
    HT = __conversation_fixed.replace("{LANGUAGE}", "Haitian Creole")
    HU = __conversation_fixed.replace("{LANGUAGE}", "Hungarian")
    HY = __conversation_fixed.replace("{LANGUAGE}", "Armenian")
    HZ = __conversation_fixed.replace("{LANGUAGE}", "Herero")
    IA = __conversation_fixed.replace("{LANGUAGE}", "Interlingua")
    ID = __conversation_fixed.replace("{LANGUAGE}", "Indonesian")
    IE = __conversation_fixed.replace("{LANGUAGE}", "Interlingue")
    IG = __conversation_fixed.replace("{LANGUAGE}", "Igbo")
    II = __conversation_fixed.replace("{LANGUAGE}", "Sichuan Yi")
    IK = __conversation_fixed.replace("{LANGUAGE}", "Inupiaq")
    IO = __conversation_fixed.replace("{LANGUAGE}", "Ido")
    IS = __conversation_fixed.replace("{LANGUAGE}", "Icelandic")
    IT = __conversation_fixed.replace("{LANGUAGE}", "Italian")
    IU = __conversation_fixed.replace("{LANGUAGE}", "Inuktitut")
    JA = __conversation_fixed.replace("{LANGUAGE}", "Japanese")
    JV = __conversation_fixed.replace("{LANGUAGE}", "Javanese")
    KA = __conversation_fixed.replace("{LANGUAGE}", "Georgian")
    KG = __conversation_fixed.replace("{LANGUAGE}", "Kongo")
    KI = __conversation_fixed.replace("{LANGUAGE}", "Kikuyu")
    KJ = __conversation_fixed.replace("{LANGUAGE}", "Kuanyama")
    KK = __conversation_fixed.replace("{LANGUAGE}", "Kazakh")
    KL = __conversation_fixed.replace("{LANGUAGE}", "Kalaallisut")
    KM = __conversation_fixed.replace("{LANGUAGE}", "Central Khmer")
    KN = __conversation_fixed.replace("{LANGUAGE}", "Kannada")
    KO = __conversation_fixed.replace("{LANGUAGE}", "Korean")
    KR = __conversation_fixed.replace("{LANGUAGE}", "Kanuri")
    KS = __conversation_fixed.replace("{LANGUAGE}", "Kashmiri")
    KU = __conversation_fixed.replace("{LANGUAGE}", "Kurdish")
    KV = __conversation_fixed.replace("{LANGUAGE}", "Komi")
    KW = __conversation_fixed.replace("{LANGUAGE}", "Cornish")
    KY = __conversation_fixed.replace("{LANGUAGE}", "Kirghiz")
    LA = __conversation_fixed.replace("{LANGUAGE}", "Latin")
    LB = __conversation_fixed.replace("{LANGUAGE}", "Luxembourgish")
    LG = __conversation_fixed.replace("{LANGUAGE}", "Ganda")
    LI = __conversation_fixed.replace("{LANGUAGE}", "Limburgan")
    LN = __conversation_fixed.replace("{LANGUAGE}", "Lingala")
    LO = __conversation_fixed.replace("{LANGUAGE}", "Lao")
    LT = __conversation_fixed.replace("{LANGUAGE}", "Lithuanian")
    LU = __conversation_fixed.replace("{LANGUAGE}", "Luba-Katanga")
    LV = __conversation_fixed.replace("{LANGUAGE}", "Latvian")
    MG = __conversation_fixed.replace("{LANGUAGE}", "Malagasy")
    MH = __conversation_fixed.replace("{LANGUAGE}", "Marshallese")
    MI = __conversation_fixed.replace("{LANGUAGE}", "Maori")
    MK = __conversation_fixed.replace("{LANGUAGE}", "Macedonian")
    ML = __conversation_fixed.replace("{LANGUAGE}", "Malayalam")
    MN = __conversation_fixed.replace("{LANGUAGE}", "Mongolian")
    MR = __conversation_fixed.replace("{LANGUAGE}", "Marathi")
    MS = __conversation_fixed.replace("{LANGUAGE}", "Malay")
    MT = __conversation_fixed.replace("{LANGUAGE}", "Maltese")
    MY = __conversation_fixed.replace("{LANGUAGE}", "Burmese")
    NA = __conversation_fixed.replace("{LANGUAGE}", "Nauru")
    NB = __conversation_fixed.replace("{LANGUAGE}", "Norwegian Bokmål")
    ND = __conversation_fixed.replace("{LANGUAGE}", "North Ndebele")
    NE = __conversation_fixed.replace("{LANGUAGE}", "Nepali")
    NG = __conversation_fixed.replace("{LANGUAGE}", "Ndonga")
    NL = __conversation_fixed.replace("{LANGUAGE}", "Dutch")
    NN = __conversation_fixed.replace("{LANGUAGE}", "Norwegian Nynorsk")
    NO = __conversation_fixed.replace("{LANGUAGE}", "Norwegian")
    NR = __conversation_fixed.replace("{LANGUAGE}", "South Ndebele")
    NV = __conversation_fixed.replace("{LANGUAGE}", "Navajo")
    NY = __conversation_fixed.replace("{LANGUAGE}", "Nyanja")
    OC = __conversation_fixed.replace("{LANGUAGE}", "Occitan")
    OJ = __conversation_fixed.replace("{LANGUAGE}", "Ojibwa")
    OM = __conversation_fixed.replace("{LANGUAGE}", "Oromo")
    OR = __conversation_fixed.replace("{LANGUAGE}", "Odia")
    OS = __conversation_fixed.replace("{LANGUAGE}", "Ossetian")
    PA = __conversation_fixed.replace("{LANGUAGE}", "Panjabi")
    PI = __conversation_fixed.replace("{LANGUAGE}", "Pali")
    PL = __conversation_fixed.replace("{LANGUAGE}", "Polish")
    PS = __conversation_fixed.replace("{LANGUAGE}", "Pashto")
    PT = __conversation_fixed.replace("{LANGUAGE}", "Portuguese")
    PT_BR = __conversation_fixed.replace("{LANGUAGE}", "Portuguese (Brazilian)")
    QU = __conversation_fixed.replace("{LANGUAGE}", "Quechua")
    RM = __conversation_fixed.replace("{LANGUAGE}", "Romansh")
    RN = __conversation_fixed.replace("{LANGUAGE}", "Rundi")
    RO = __conversation_fixed.replace("{LANGUAGE}", "Romanian")
    RU = __conversation_fixed.replace("{LANGUAGE}", "Russian")
    RW = __conversation_fixed.replace("{LANGUAGE}", "Kinyarwanda")
    SA = __conversation_fixed.replace("{LANGUAGE}", "Sanskrit")
    SC = __conversation_fixed.replace("{LANGUAGE}", "Sardinian")
    SD = __conversation_fixed.replace("{LANGUAGE}", "Sindhi")
    SE = __conversation_fixed.replace("{LANGUAGE}", "Northern Sami")
    SG = __conversation_fixed.replace("{LANGUAGE}", "Sango")
    SI = __conversation_fixed.replace("{LANGUAGE}", "Sinhala")
    SK = __conversation_fixed.replace("{LANGUAGE}", "Slovak")
    SL = __conversation_fixed.replace("{LANGUAGE}", "Slovenian")
    SM = __conversation_fixed.replace("{LANGUAGE}", "Samoan")
    SN = __conversation_fixed.replace("{LANGUAGE}", "Shona")
    SO = __conversation_fixed.replace("{LANGUAGE}", "Somali")
    SQ = __conversation_fixed.replace("{LANGUAGE}", "Albanian")
    SR = __conversation_fixed.replace("{LANGUAGE}", "Serbian")
    SS = __conversation_fixed.replace("{LANGUAGE}", "Swati")
    ST = __conversation_fixed.replace("{LANGUAGE}", "Southern Sotho")
    SU = __conversation_fixed.replace("{LANGUAGE}", "Sundanese")
    SV = __conversation_fixed.replace("{LANGUAGE}", "Swedish")
    SW = __conversation_fixed.replace("{LANGUAGE}", "Swahili")
    TA = __conversation_fixed.replace("{LANGUAGE}", "Tamil")
    TE = __conversation_fixed.replace("{LANGUAGE}", "Telugu")
    TG = __conversation_fixed.replace("{LANGUAGE}", "Tajik")
    TH = __conversation_fixed.replace("{LANGUAGE}", "Thai")
    TI = __conversation_fixed.replace("{LANGUAGE}", "Tigrinya")
    TK = __conversation_fixed.replace("{LANGUAGE}", "Turkmen")
    TL = __conversation_fixed.replace("{LANGUAGE}", "Tagalog")
    TN = __conversation_fixed.replace("{LANGUAGE}", "Tswana")
    TO = __conversation_fixed.replace("{LANGUAGE}", "Tonga")
    TR = __conversation_fixed.replace("{LANGUAGE}", "Turkish")
    TS = __conversation_fixed.replace("{LANGUAGE}", "Tsonga")
    TT = __conversation_fixed.replace("{LANGUAGE}", "Tatar")
    TW = __conversation_fixed.replace("{LANGUAGE}", "Twi")
    TY = __conversation_fixed.replace("{LANGUAGE}", "Tahitian")
    UG = __conversation_fixed.replace("{LANGUAGE}", "Uighur")
    UK = __conversation_fixed.replace("{LANGUAGE}", "Ukrainian")
    UR = __conversation_fixed.replace("{LANGUAGE}", "Urdu")
    UZ = __conversation_fixed.replace("{LANGUAGE}", "Uzbek")
    VE = __conversation_fixed.replace("{LANGUAGE}", "Venda")
    VI = __conversation_fixed.replace("{LANGUAGE}", "Vietnamese")
    VO = __conversation_fixed.replace("{LANGUAGE}", "Volapük")
    WA = __conversation_fixed.replace("{LANGUAGE}", "Walloon")
    WO = __conversation_fixed.replace("{LANGUAGE}", "Wolof")
    XH = __conversation_fixed.replace("{LANGUAGE}", "Xhosa")
    YI = __conversation_fixed.replace("{LANGUAGE}", "Yiddish")
    YO = __conversation_fixed.replace("{LANGUAGE}", "Yoruba")
    ZA = __conversation_fixed.replace("{LANGUAGE}", "Zhuang")
    ZH = __conversation_fixed.replace("{LANGUAGE}", "Chinese")
    ZH_CN = __conversation_fixed.replace("{LANGUAGE}", "Chinese (Simplified)")
    ZH_TW = __conversation_fixed.replace("{LANGUAGE}", "Chinese (Traditional)")
    ZU = __conversation_fixed.replace("{LANGUAGE}", "Zulu")


class _ChatWeaverSystemRules:
    def __init__(self):
        self.__current: str = ""

        self.__default_rules: str = (
            "# Role and Objective\n"
            "You are a reliable, competent assistant. Provide correct, verifiable, and useful information that helps the user achieve practical goals.\n"
            "\n"
            "## Style\n"
            "- Kind, clear, and professional tone.\n"
            "- Adjust length and level of detail to the user's needs.\n"
            "- When helpful, include a brief explanation of your approach (max 2 sentences) without exposing internal reasoning.\n"
            "\n"
            "## Content Quality\n"
            "- Prefer accurate sources and established knowledge.\n"
            "- Be honest about uncertainty or limitations.\n"
            "\n"
            "## Safety and Ethics\n"
            "- Avoid content that could cause physical, emotional, or financial harm.\n"
            "- Respect copyright, laws, and applicable policies.\n"
            "- Do not provide dangerous instructions.\n"
            "\n"
            "## Completeness and Context\n"
            "- Provide coherent, self-contained answers that address the user's question and context.\n"
        )

        self.__formal_chat_rules: str = (
            "# Context\n"
            "Formal conversation with a respectful, professional, and punctual tone. Do not mention being an AI.\n"
            "\n"
            "## Objective\n"
            "Deliver clear, precise, and complete responses suitable for a professional register.\n"
            "\n"
            "## Style\n"
            "- Formal language, no slang.\n"
            "- Logical, concise structure.\n"
            "- If useful, add brief context (max 2 sentences) without exposing internal reasoning.\n"
        )

        self.__informal_chat_rules: str = (
            "# Context\n"
            "Informal, friendly chat. Do not mention being an AI.\n"
            "\n"
            "## Objective\n"
            "Keep the conversation lively with brief, natural, and engaging replies.\n"
            "\n"
            "## Style\n"
            "- Casual, straightforward tone.\n"
            "- Avoid unnecessary formalities.\n"
            "- When needed, provide a short clarification (1–2 sentences) without revealing internal reasoning.\n"
        )

        self.__formal_email_rules: str = (
            "# Context\n"
            "Formal email exchange. Do not mention being an AI.\n"
            "\n"
            "## Objective\n"
            "Write clear, professional, and complete emails.\n"
            "\n"
            "## Email Structure\n"
            "- Greeting: appropriate opening (e.g., “Dear …”, “Good morning …”).\n"
            "- Body: concise, well-organized content; state requests, decisions, or next steps.\n"
            "- Closing: suitable sign-off (e.g., “Kind regards,”) and signature.\n"
            "\n"
            "## Style\n"
            "- Respectful, professional tone.\n"
            "- Maximum clarity and courtesy.\n"
            "- Optional brief context (max 2 sentences) without exposing internal reasoning.\n"
        )

        self.__informal_email_rules: str = (
            "# Context\n"
            "Informal email between people with some familiarity. Do not mention being an AI.\n"
            "\n"
            "## Objective\n"
            "Write short, friendly, and direct emails that prioritize speed and clarity.\n"
            "\n"
            "## Email Structure\n"
            "- Greeting: simple and warm (e.g., \"Hi …\", \"Hey …\").\n"
            "- Body: 1–3 short paragraphs; get to the point; include requests/questions.\n"
            "- Closing: informal but polite (e.g., \"Thanks!\", \"Talk soon,\" \"Cheers\").\n"
            "- Signature: first name or brief sign-off consistent with the tone.\n"
            "\n"
            "## Style\n"
            "- Conversational, positive tone.\n"
            "- Short sentences; avoid unnecessary jargon.\n"
            "- Emojis only when appropriate and used sparingly.\n"
            "- Avoid walls of text: break lines between idea blocks.\n"
            "\n"
            "## Good Practices\n"
            "- Ask for clarifications lightly when needed.\n"
            "- Propose a clear next step (e.g., \"Does Tuesday work?\").\n"
            "- Confirm times or deadlines when relevant.\n"
            "- Avoid sensitive data; respect privacy and courtesy.\n"
        )

    # -------- DUNDER_METHODS --------
    def __str__(self) -> str:
        return "< ChatWeaverSystemRules >"

    def __repr__(self) -> str:
        return "ChatWeaverSystemRules"

    # -------- HELPERS --------
    def __modify_current_rules(self, formatting: Formatting | None = None, language: Language | None = Language.conversation_mirroring) -> None:
        if formatting is not None:
            self.__current += f"\n{formatting.value}"

        if language is not None:
            self.__current += f"\n{language.value}"

    # -------- PUBLIC METHODS --------
    def default(self, formatting: Formatting | None = None, language: Language | None = Language.conversation_mirroring) -> str:
        self.__current = str(self.__default_rules)
        self.__modify_current_rules(formatting, language)
        return self.__current

    def formal_chat(self, formatting: Formatting | None = None, language: Language | None = Language.conversation_mirroring) -> str:
        self.__current = str(self.__formal_chat_rules)
        self.__modify_current_rules(formatting, language)
        return self.__current

    def informal_chat(self, formatting: Formatting | None = None, language: Language | None = Language.conversation_mirroring) -> str:
        self.__current = str(self.__informal_chat_rules)
        self.__modify_current_rules(formatting, language)
        return self.__current

    def formal_email(self, formatting: Formatting | None = None, language: Language | None = Language.conversation_mirroring) -> str:
        self.__current = str(self.__formal_email_rules)
        self.__modify_current_rules(formatting, language)
        return self.__current

    def informal_email(self, formatting: Formatting | None = None, language: Language | None = Language.conversation_mirroring) -> str:
        self.__current = str(self.__informal_email_rules)
        self.__modify_current_rules(formatting, language)
        return self.__current


ChatWeaverSystemRules = _ChatWeaverSystemRules()

if __name__ == "__main__":
    print(ChatWeaverSystemRules)
    print(ChatWeaverSystemRules.default(formatting=Formatting.none, language=Language.IT))
