"""Phone-number normalization.

Arabic keyboards produce Arabic-Indic digits (٠١٢…) and Persian layouts produce
Extended Arabic-Indic (۰۱۲…). Phone number is our login identifier, so a value typed
with one digit set must match one stored with another. We canonicalize EVERYTHING to
ASCII 0-9 at every entry point (register, login, model save).
"""

# 20 source chars -> 20 target chars (char-for-char)
_DIGIT_MAP = str.maketrans(
    '٠١٢٣٤٥٦٧٨٩'   # Arabic-Indic       U+0660..U+0669
    '۰۱۲۳۴۵۶۷۸۹',  # Extended/Persian   U+06F0..U+06F9
    '0123456789'
    '0123456789'
)


def normalize_phone(value):
    """Translate Arabic/Persian digits to ASCII and trim surrounding whitespace.
    Returns the value unchanged if it is None/empty."""
    if not value:
        return value
    return value.translate(_DIGIT_MAP).strip()
