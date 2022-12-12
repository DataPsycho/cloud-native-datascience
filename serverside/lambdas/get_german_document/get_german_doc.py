#!/usr/bin/env python
# coding: utf-8

# In[32]:


import json
import os
import typing as t

import boto3

from domainmodel import Job
from microkit.exceptions import (
    ContentNotFoundError,
    DataBaseOperationError,
    ParameterMissingError,
    create_response_from_exception,
    create_response_from_not_found_exception,
    create_response_from_param_exception,
    query_parameter_ok,
)
from microkit.logger import get_logger
from microkit.orm import DynamoOrm
from microkit.utils import DecimalEncoder, bytes_to_base64_str, load_env_vars, return_by_status_code

# In[6]:


# In[9]:


ENV_VARS = load_env_vars()
LOGGER = get_logger(str(__name__))
JOBTYPE = "job1"


# In[10]:


SESSION = boto3.session.Session()
DYNAMODB_RESOURCE = SESSION.resource('dynamodb')
DYNAMO_TABLE = DYNAMODB_RESOURCE.Table(ENV_VARS.db)

BUCKET_NAME = os.environ['BUCKET']
S3_CLEINT = SESSION.client('s3')
S3_RESOURCE = SESSION.resource("s3")


# # Steps
# 1. If As for Latest
#     - Query job1 Data using on Given Project ID
#     - If there is no german file in the location through filenot found
#     - If there is review file read it as binary
#     - Convert the file into base 64
#     - return to the User
# 2. If ask for previous versions
#     - Get the Specific version by Querying the Data
#     - Follow the same review check steps

# In[11]:


def get_item_from_db(job: Job) -> Job:
    """Get Item from a database by given a Job dataclass template"""
    handler = DynamoOrm(job, DYNAMO_TABLE)
    resp = handler.get_item()
    if resp["status"] == 200:
        new_data = Job.from_dict(resp["data"])
        return new_data
    raise ContentNotFoundError(f"Unable to find job metadata from the database for project: {job.PK}, version: {job.SK}")


# In[12]:


def get_version0(pid: str) -> Job:
    """Get the version 0 pointer of the job by given a projectid"""
    pk = f"proj#{pid}"
    sk = f"{JOBTYPE}#v0"
    template = Job(pk, sk)
    return get_item_from_db(template)


# In[13]:


def get_latest_version(pid: str) -> Job:
    """Get the lates version of the job info from version poiner"""
    v0_template = get_version0(pid)
    if v0_template:
        sk = f"{JOBTYPE}#{v0_template.version_pointer}"
        latest_item = Job(PK=v0_template.PK, SK=sk)
        return get_item_from_db(latest_item)
    raise DataBaseOperationError(f"Content not found for PID: {pid}")


# In[33]:


def get_object_paths(metadata: Job) -> t.Dict:
    """Get the path of the object from s3 from metadata bucket and key"""
    try:
        repo = S3_CLEINT.list_objects_v2(Bucket=metadata.bucket, Prefix=metadata.bucket_key)
        if "Contents" in repo:
            key = repo["Contents"][0]["Key"]
            return {"output": key}
        else:
            raise ContentNotFoundError(
                f"Missing files in the file storage for project: {metadata.pid}, "
                f"job type: {metadata.entity_type} and version: {metadata.version}"
            )
    except Exception as e:
        LOGGER.info(e)
        raise ContentNotFoundError("Unable to read resource from the file storege, may be key is not vaid.")


# In[34]:


def read_docx_from_s3(metadata: Job) -> str:
    """Read docx file as bytes from s3"""
    try:
        key_store = get_object_paths(metadata=metadata)
        review_key = key_store["output"]
        handler = S3_RESOURCE.Object(bucket_name=metadata.bucket, key=review_key)
        data = handler.get()['Body'].read()
        return bytes_to_base64_str(data)
    except Exception as e:
        LOGGER.info(e)
        raise ContentNotFoundError("Unable to read resource from the file storege, may be file does not exist yet.")


# In[36]:


def process_request(pid: str, version=None) -> t.Dict:
    """Then acting main function which handle the whole process from the payload inputs"""
    # TODO: Add functionality to request any last 3 successful version
    _ = version
    try:
        metadata = get_latest_version(pid=pid)
        data = read_docx_from_s3(metadata=metadata)
        resp = {"status": 200, "data": {"content": data, "query": metadata.to_dict()}}
        return return_by_status_code(resp)
    except ContentNotFoundError as e:
        LOGGER.info(e)
        raise e
    except Exception as e:
        LOGGER.info(e)
        raise e


# In[37]:


def handler(event, context):
    """Handler function for the API gateway"""
    param_list = ["pid", "version"]
    query_param = event.get("queryStringParameters", {})
    try:
        query_parameter_ok(expected=param_list, requested=query_param)
        resp = process_request(pid=query_param["pid"], version=query_param["version"])
        return {"statusCode": resp["status"], "body": json.dumps(resp, cls=DecimalEncoder)}
    except ParameterMissingError as e:
        return create_response_from_param_exception(exception=e, data={})
    except ContentNotFoundError as e:
        return create_response_from_not_found_exception(exception=e, data={})
    except Exception as e:
        return create_response_from_exception(exception=e, data={})

