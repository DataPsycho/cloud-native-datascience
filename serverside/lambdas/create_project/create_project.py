#!/usr/bin/env python
# coding: utf-8

# In[1]:


import json
import typing as t

import boto3

from domainmodel import Project
from microkit.exceptions import (
    DataBaseOperationError,
    ParameterMissingError,
    create_response_from_exception,
    create_response_from_param_exception,
    query_parameter_ok,
)
from microkit.logger import get_logger
from microkit.orm import DynamoOrm
from microkit.utils import DecimalEncoder, collect_cet_now, load_env_vars, return_by_status_code

# In[2]:


# In[3]:


LOGGER = get_logger(str(__name__))
ENV_VARS = load_env_vars()


# In[4]:


SESSION = boto3.session.Session()
DYNAMODB_RESOURCE = SESSION.resource('dynamodb')
DYNAMO_TABLE = DYNAMODB_RESOURCE.Table(ENV_VARS.db)


# In[5]:


def process_request(payload: t.Dict) -> t.Dict:
    """ Process the Request into Success of Failure category based on status
    param: request: request data to send to dynamodb
    """
    attribute = Project.from_attribute_data(
        name=payload["name"],
        updated_by=payload["updated_by"],
        updated_at=collect_cet_now()
    )
    orm_handler = DynamoOrm(data=attribute, table=DYNAMO_TABLE)
    if orm_handler.get_item()["status"] == 500:
        response = orm_handler.put_item()
        return return_by_status_code(response)
    else:
        raise DataBaseOperationError


# In[6]:


def handler(event, context):
    """Handler function for the API gateway"""
    param_list = ["name", "updated_by"]
    try:
        request = json.loads(event["body"])
        query_parameter_ok(param_list, request)
        resp = process_request(payload=request)
        return {"statusCode": resp["status"], "body": json.dumps(resp, cls=DecimalEncoder)}
    except ParameterMissingError as e:
        LOGGER.info(e)
        return create_response_from_param_exception(exception=e, data={})
    except Exception as e:
        LOGGER.info(e)
        return create_response_from_exception(exception=e, data={})

