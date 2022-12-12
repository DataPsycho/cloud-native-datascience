import typing as t
from datetime import timezone, datetime
import json
import decimal
import unicodedata
import re
import unicodedata


REGEX_COLLECTION = [
    {"pattern": re.compile(r" +"), "replace_with": "_"},  # multi_space_replacer
    {"pattern": re.compile(r"[^0-9a-zA-Z_]"), "replace_with": ""},  # special_character_replacer
]

def remove_accents(input_str: str) -> str:
    nfkd_form = unicodedata.normalize('NFKD', input_str)
    return u"".join([c for c in nfkd_form if not unicodedata.combining(c)])


def convert_to_internal_convention(text: str) -> str:
    text = remove_accents(text)
    for regex in REGEX_COLLECTION:
        text = regex["pattern"].sub(regex["replace_with"], text)
    return remove_accents(text.lower())


def collect_unix_utc_seconds() -> int:
    now = datetime.now(tz=timezone.utc).timestamp()
    return int(now)

def collect_utc_now() -> str:
    return datetime.now(tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%S")


def collect_utc_date() -> str:
    return datetime.now(tz=timezone.utc).date().strftime("%Y-%m-%d")


def create_local_path(filename: str) -> str:
    if os.environ["ENVIRON"] == "local":
        return f"temp/{filename}"
    return f"/tmp/{filename}"

class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            try:
                return int(o)
            except: 
                return str(o)
        return super(DecimalEncoder, self).default(o)


def all_field_provided(payload: t.Dict, required_list: t.List) -> t.Tuple[bool, str]:
    missing_list = []
    for item in required_list:
        if item not in payload:
            missing_list.append(item)
    if len(missing_list) > 0:
        return False, "Following Fields are missing {}".format(", ".join(missing_list))
    return True, "OK"


def increment_pointer(current_pointer: str) -> str:
    """Increase version of the pointer"""
    new_number = int(re.search("\d+", current_pointer).group()) + 1
    new_version = re.sub("\d+", str(new_number), current_pointer)
    return new_version