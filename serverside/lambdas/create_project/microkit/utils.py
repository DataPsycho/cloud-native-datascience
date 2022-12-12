import base64
import decimal
import json
import os
import re
import typing as t
import unicodedata
from collections import namedtuple
from datetime import datetime, timedelta, timezone

REGEX_COLLECTION = [
    {"pattern": re.compile(r" +"), "replace_with": "-"},  # multi_space_replacer
    {"pattern": re.compile(r"[^0-9a-zA-Z-]"), "replace_with": ""},  # special_character_replacer
]
EnvVars = namedtuple("EnvVars", "bucket, db")
EnvVarsExtras = namedtuple("EnvVarsExtras", "sfn_arn")


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


def collect_cet_now() -> str:
    """Convert current machine time into CET time"""
    off_set = 2
    utc_now = datetime.now(tz=timezone.utc)
    result = utc_now + timedelta(hours=off_set)
    return result.strftime("%Y-%m-%dT%H:%M:%S")


def collect_utc_date() -> str:
    return datetime.now(tz=timezone.utc).date().strftime("%Y-%m-%d")


def create_local_path(filename: str) -> str:
    if os.environ["LAMBDA_RUNTIME_ENV"] == "local":
        return f"temp/{filename}"
    return f"/tmp/{filename}"


class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            try:
                return int(o)
            except BaseException:
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
    new_number = int(re.search("\\d+", current_pointer).group()) + 1
    new_version = re.sub("\\d+", str(new_number), current_pointer)
    return new_version


def add_s3_prefix(path: str) -> str:
    """Add prefix to a s3 code"""
    return f"s3://{path}"


def return_by_status_code(response: t.Dict, error=None) -> t.Dict:
    """Return any database operation result based on status code"""
    if response["status"] == 200:
        response["error"] = None
        return response
    if error:
        response["error"] = error
        return response
    response["error"] = "ClientError: Could not get/post the data into database"
    return response


def bytes_to_base64_str(byte_data: bytes) -> str:
    """Convert bytes to base 64"""
    b64_encoded_byte = base64.b64encode(byte_data)
    b64_encoded_str = b64_encoded_byte.decode("utf-8")
    return b64_encoded_str


def create_metacomposit(attr_list: t.List[str]) -> str:
    """Combining the component from a list into a string separeted by #"""
    attr_list_flatten = []
    for attr in attr_list:
        if isinstance(attr, list):
            attr_list_flatten.extend(attr)
        else:
            attr_list_flatten.append(attr)
    attr_list_flatten = [convert_to_internal_convention(x) for x in attr_list_flatten]
    metacomposit = "#".join(attr_list_flatten)
    return metacomposit


def load_env_vars() -> EnvVars:
    if os.environ["LAMBDA_RUNTIME_ENV"] == 'local':
        from dotenv import load_dotenv  # isort:skip
        assert load_dotenv('../../../.env')  # isort:skip
        return EnvVars(os.environ['BUCKET'], os.environ['DB_NAME'])
    return EnvVars(os.environ['BUCKET'], os.environ['DB_NAME'])


def load_extra_env_vars() -> EnvVarsExtras:
    if os.environ["LAMBDA_RUNTIME_ENV"] == 'local':
        from dotenv import load_dotenv  # isort:skip
        assert load_dotenv('../../../.env')  # isort:skip
        return EnvVarsExtras(os.environ['SFN_WORKFLOW_ARN'])
    return EnvVarsExtras(os.environ['SFN_WORKFLOW_ARN'])