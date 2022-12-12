#!/usr/bin/env python
# coding: utf-8

# In[1]:


import json
import typing as t

import boto3

from domainmodel import Project
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
from microkit.utils import DecimalEncoder, load_env_vars

# In[15]:


# In[3]:


LOGGER = get_logger(str(__name__))
ENV_VARS = load_env_vars()


# In[5]:


SESSION = boto3.session.Session()
DYNAMODB_RESOURCE = SESSION.resource('dynamodb')
DYNAMO_TABLE = DYNAMODB_RESOURCE.Table(ENV_VARS.db)
S3_RESOURCE = SESSION.resource("s3")


# In[12]:


def get_item_from_db(project: Project) -> Project:
    """Get Item from a database by given a Job dataclass template"""
    handler = DynamoOrm(project, DYNAMO_TABLE)
    resp = handler.get_item()
    if resp["status"] == 200:
        new_data = project.from_dict(resp["data"])
        return new_data
    raise DataBaseOperationError("Unable to find Project metadata from the database.")


# In[7]:


def check_object(metadata: Project) -> bool:
    """Get the path of the object from s3 from metadata bucket and key"""
    try:
        resource = S3_RESOURCE.Object(bucket_name=ENV_VARS.bucket, key=metadata.bucket_key)
        resource.load()
        return True
    except Exception as e:
        LOGGER.info(e)
        raise ContentNotFoundError(f"Document not found for the project: {metadata.SK}")


# In[8]:


def process_request(pid: str) -> t.Dict:
    """Then acting main function which handle the whole process from the payload inputs"""
    pk = "proj#project"
    sk = pid
    template = Project(PK=pk, SK=sk, name='', updated_by='', updated_at='')
    metadata = get_item_from_db(template)
    file_exist = check_object(metadata=metadata)
    resp = {"status": 200, "data": {"added": file_exist}}
    return resp


# In[9]:


def handler(event, context):
    """Handler function for the API gateway"""
    default_data = {"added": False}
    param_list = ["pid"]
    query_param = event.get("queryStringParameters", {})
    try:
        query_parameter_ok(expected=param_list, requested=query_param)
        resp = process_request(pid=query_param["pid"])
        return {"statusCode": resp["status"], "body": json.dumps(resp, cls=DecimalEncoder)}
    except ParameterMissingError as e:
        LOGGER.info(e)
        return create_response_from_param_exception(exception=e, data={})
    except DataBaseOperationError as e:
        LOGGER.info(e)
        return create_response_from_exception(exception=e, data={})
    except ContentNotFoundError as e:
        LOGGER.info(e)
        return create_response_from_not_found_exception(exception=e, data={})
    except Exception as e:
        LOGGER.info(e)
        return create_response_from_exception(exception=e, data=default_data)

