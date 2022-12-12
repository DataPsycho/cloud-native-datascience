#!/usr/bin/env python
# coding: utf-8

# In[4]:


import json

import boto3

from microkit.exceptions import ParameterMissingError, create_response_from_exception, create_response_from_param_exception
from microkit.logger import get_logger
from microkit.utils import DecimalEncoder, load_env_vars, return_by_status_code

# In[5]:


LOGGER = get_logger(str(__name__))
ENV_VARS = load_env_vars()


# In[6]:


SESSION = boto3.session.Session()
DYNAMODB_RESOURCE = SESSION.resource('dynamodb')
DYNAMO_TABLE = DYNAMODB_RESOURCE.Table(ENV_VARS.db)


# In[7]:


def get_active_projects():
    """Get all active project by querying the Global Secondary Index"""
    resp = DYNAMO_TABLE.query(
        IndexName="ParentEntityIndex",
        KeyConditionExpression="parent_entity_type = (:val0)",
        FilterExpression="active = (:val1)",
        ExpressionAttributeValues={':val0': "proj", ':val1': True}

    )
    if 'Items' in resp and len(resp['Items']) > 0:
        status_code = resp["ResponseMetadata"]["HTTPStatusCode"]
        payload = {"status": status_code, "data": resp["Items"]}
        return return_by_status_code(payload)
    payload = {"status": 500, "data": []}
    return return_by_status_code(payload)


# In[8]:


def handler(event, context):
    """Handler function for the API gateway"""
    try:
        resp = get_active_projects()
        return {"statusCode": resp["status"], "body": json.dumps(resp, cls=DecimalEncoder)}
    except ParameterMissingError as e:
        LOGGER.info(e)
        return create_response_from_param_exception(exception=e, data=[])
    except Exception as e:
        LOGGER.info(e)
        return create_response_from_exception(exception=e, data=[])

