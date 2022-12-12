#!/usr/bin/env python
# coding: utf-8

# In[4]:


import json
import typing as t

import boto3

from microkit.exceptions import (
    DataBaseOperationError,
    ParameterMissingError,
    ParameterValueError,
    create_response_from_exception,
    parameter_value_ok,
    query_parameter_ok,
)
from microkit.logger import get_logger
from microkit.utils import DecimalEncoder, load_env_vars, return_by_status_code

# In[5]:


LOGGER = get_logger(str(__name__))
ENV_VARS = load_env_vars()


# In[6]:


SESSION = boto3.session.Session()
DYNAMODB_RESOURCE = SESSION.resource('dynamodb')
DYNAMO_TABLE = DYNAMODB_RESOURCE.Table(ENV_VARS.db)
QUERY_LIST = ['running', 'completed', 'failed', 'rejected', "all"]


# In[7]:


def get_job_info(pid: str, status: str):
    """Get Job log by job status and project id"""
    try:
        parent_entity_pid = f"job#{pid}"
        status_pattern = status
        if status != "all":
            resp = DYNAMO_TABLE.query(
                IndexName="JobStatusIndex",
                KeyConditionExpression="parent_entity_pid = (:val0) AND begins_with (status_jid, :val1)",
                ExpressionAttributeValues={":val0": parent_entity_pid, ":val1": status_pattern}
            )
            return {"status": 200, "data": resp["Items"]}
        else:
            resp = DYNAMO_TABLE.query(
                IndexName="JobStatusIndex",
                KeyConditionExpression="parent_entity_pid = (:val0)",
                ExpressionAttributeValues={":val0": parent_entity_pid}
            )
            return {"status": 200, "data": resp["Items"]}
    except Exception as e:
        LOGGER.printlog(e)
        raise DataBaseOperationError("Resoure not found in the database")


# In[8]:


def process_request(payload: t.Dict) -> t.Dict:
    """Then acting main function which handle the whole process from the payload inputs"""
    # Fill It up with your passion
    pid = payload["pid"]
    status = payload["status"]
    job_info = get_job_info(pid=pid, status=status)
    return return_by_status_code(job_info)


# In[9]:


def handler(event, context):
    """Handler function for the API gateway"""
    param_list = ["pid", "status"]
    query_param = event.get("queryStringParameters", {})
    try:
        query_parameter_ok(param_list, query_param)
        parameter_value_ok(QUERY_LIST, query_param["status"])
        resp = process_request(payload=query_param)
        return {"statusCode": resp["status"], "body": json.dumps(resp, cls=DecimalEncoder)}
    except ParameterMissingError as e:
        return create_response_from_exception(exception=e, data=[])
    except ParameterValueError as e:
        return create_response_from_exception(exception=e, data=[])
    except DataBaseOperationError as e:
        return create_response_from_exception(exception=e, data=[])
    except Exception as e:
        return create_response_from_exception(exception=e, data=[])

