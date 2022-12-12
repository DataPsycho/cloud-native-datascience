import re
import unicodedata

REGEX_COLLECTION = [
    {"pattern": re.compile(r" +"), "replace_with": "_"},  # multi_space_replacer
    {"pattern": re.compile(r"[^0-9a-zA-Z_]"), "replace_with": ""},  # special_character_replacer
]


def remove_accents(input_str: str) -> str:
    """
    Remove Latin accents from the text
    :param input_str: Input string with german accent
    :return: String with removed accent
    """
    nfkd_form = unicodedata.normalize('NFKD', input_str)
    return u"".join([c for c in nfkd_form if not unicodedata.combining(c)])


def clean_text(text: str) -> str:
    """
    Convert text to internal convention
    :param text: Text string to convert
    :return: Converted string
    """
    text = remove_accents(text)
    for regex in REGEX_COLLECTION:
        text = regex["pattern"].sub(regex["replace_with"], text)  # type: ignore
    return remove_accents(text.lower())
