#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import base64
import json
import os
import typing as t

import boto3

from domainmodel import Project
from microkit.exceptions import (
    ContentNotFoundError,
    DataBaseOperationError,
    ParameterMissingError,
    create_response_from_exception,
    create_response_from_param_exception,
    query_parameter_ok,
)
from microkit.logger import get_logger
from microkit.orm import DynamoOrm, get_project_info_by_pid
from microkit.utils import DecimalEncoder, convert_to_internal_convention, create_local_path, load_env_vars

# In[ ]:


LOGGER = get_logger(str(__name__))
ENV_VARS = load_env_vars()


# In[ ]:


# BUCKET_NAME = os.environ['BUCKET']
SESSION = boto3.session.Session()
S3_CLEINT = SESSION.client('s3')
DYNAMODB_RESOURCE = SESSION.resource('dynamodb')
DYNAMO_TABLE = DYNAMODB_RESOURCE.Table(ENV_VARS.db)
S3_RESOURCE = SESSION.resource("s3")


# In[ ]:


BUCKET_KEY_PREFIX = "docstore/documents"
LOCAL_DOC_PATH = create_local_path("document.docx")


# # Steps:
# 1. Query The Database using the given SK
# 2. Create a Project object to update the the database
# 3. Save the new dossier in /tmp using the new dossier name for the previous step
# 4. upload the dossier into the location with given filename
# 5. If upload successful update the database with the new project init

# In[ ]:


def create_project_from_query(sk: str) -> Project:
    try:
        project_info = get_project_info_by_pid(DYNAMO_TABLE, sk)
        proj_init = Project.from_dict(project_info["Item"])
        return proj_init
    except Exception as e:
        LOGGER.info(e)
        raise DataBaseOperationError(f"Can not query the database to get information for the PID: {sk}")


# In[ ]:


def b64_str_to_docx(b64_str: str) -> None:
    """Convert base64 request data into binary data and save it to local directory"""
    bytes_stream = base64.b64decode(b64_str.encode("utf-8"))
    path = LOCAL_DOC_PATH
    with open(path, 'wb') as f:
        f.write(bytes_stream)


# In[ ]:


def remove_extension(text: str):
    return text.replace(".docx", "")

def add_extension(text: str):
    return text + ".docx"


# In[ ]:


def upload_to_s3(p: Project) -> None:
    """Upload new dictionary to the given bucket and bucket key"""
    try:
        S3_CLEINT.upload_file(
            Filename=LOCAL_DOC_PATH,
            Bucket=p.bucket,
            Key=p.bucket_key,
            ExtraArgs={"ServerSideEncryption": "aws:kms"}
        )
        os.remove(LOCAL_DOC_PATH)
        print(f"File uploaded to {p.bucket}/{p.bucket_key}")
    except Exception as e:
        LOGGER.info(e)
        raise ContentNotFoundError(e)


# In[ ]:


def update_project_data(proj: Project, sk: str, filename: str, updated_by: str) -> Project:
    """Update the project data using new dossier data"""
    filename = remove_extension(filename)
    filename = convert_to_internal_convention(filename.replace("_", "-")).replace("-", "_")
    filename = add_extension(filename)
    filepath = proj.SK.replace(':', '-')
    bucket_key = f"{os.path.join(BUCKET_KEY_PREFIX, filepath, 'document.docx')}"
    proj.set_doc(filename)
    proj.set_bucket(ENV_VARS.bucket)
    proj.set_bucket_key(bucket_key)
    proj.set_updated_by(updated_by)
    proj.set_updated_at()
    return proj


# In[ ]:


def update_dynamo_data(proj: Project) -> t.Dict:
    try:
        orm_handler = DynamoOrm(proj, DYNAMO_TABLE)
        resp = orm_handler.update_all()
        return resp
    except Exception as e:
        LOGGER.info(e)
        raise DataBaseOperationError


# In[ ]:


def process_request(request: t.Dict) -> t.Dict:
    resp = create_project_from_query(request["sk"])
    data = request["data"]
    b64_str_to_docx(data)
    new_project_data = update_project_data(
        proj=resp,
        sk=request["sk"],
        filename=request["doc"],
        updated_by=request["updated_by"]
    )
    upload_to_s3(new_project_data)
    orm_handler = DynamoOrm(new_project_data, DYNAMO_TABLE)
    resp = orm_handler.update_all()
    return resp


# In[ ]:


def handler(event, context):
    """Handler function for the API gateway"""
    param_list = ["sk", "doc", "data", "updated_by"]
    try:
        request = json.loads(event["body"])
        query_parameter_ok(param_list, request)
        resp = process_request(request=request)
        return {"statusCode": resp["status"], "body": json.dumps(resp, cls=DecimalEncoder)}
    except ParameterMissingError as e:
        LOGGER.info(e)
        return create_response_from_param_exception(exception=e, data={})
    except Exception as e:
        LOGGER.info(e)
        return create_response_from_exception(exception=e, data={})

