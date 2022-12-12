#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import json
import typing as t

import boto3

from domainmodel import Job
from microkit.exceptions import DataBaseOperationError, ParameterMissingError, query_parameter_ok
from microkit.logger import get_logger
from microkit.orm import DynamoOrm
from microkit.utils import DecimalEncoder, collect_cet_now, load_env_vars

# In[ ]:


# In[ ]:


LOGGER = get_logger(str(__name__))
ENV_VARS = load_env_vars()


# In[ ]:


SESSION = boto3.session.Session()
DYNAMODB_RESOURCE = SESSION.resource('dynamodb')
DYNAMO_TABLE = DYNAMODB_RESOURCE.Table(ENV_VARS.db)


# In[ ]:


def update_version_0_pointer(job: Job):
    """Update the pointer of the file location"""
    sk = f"{job.entity_type}#v0"
    job_info = Job.from_keys(pk=job.PK, sk=sk)
    dynamo_handler = DynamoOrm(job_info, DYNAMO_TABLE)
    resp = dynamo_handler.get_item()
    if resp["status"] == 200:
        v0_repo = Job.from_dict(resp["data"])
        v0_repo.bucket = job.bucket
        v0_repo.bucket_key = job.bucket_key
        v0_repo.finished_at = job.finished_at
        v0_repo.version_pointer = job.version
        dynamo_handler = DynamoOrm(v0_repo, DYNAMO_TABLE)
        resp = dynamo_handler.update_all()
        return resp
    else:
        raise DataBaseOperationError("Could not update the version0 with Dossier Job attribute")


# In[ ]:


def update_job(pk: str, sk: str, exec_status: str) -> t.Union[t.Dict, None]:
    """Update a Status of the Job by given data"""
    status = "completed"
    if exec_status == "TaskFailed":
        status = "failed"
    job_info = Job.from_keys(pk=pk, sk=sk)
    dynamo_handler = DynamoOrm(job_info, DYNAMO_TABLE)
    resp = dynamo_handler.get_item()
    if resp["status"] == 200:
        new_job_instance = Job.from_dict(resp["data"])
        data = new_job_instance.to_dict()
        data["status"] = status
        data["finished_at"] = collect_cet_now()
        updated_repo = Job.from_dict(data)
        dynamo_handler = DynamoOrm(updated_repo, DYNAMO_TABLE)
        resp = dynamo_handler.update_all()
        _ = update_version_0_pointer(updated_repo)
        return resp
    return None


# In[ ]:


def process_request(payload: t.Dict) -> t.Dict:
    """Then acting main function which handle the whole process from the payload inputs
    :param payload: A dictionary Payload from stepfunction to update the Jobs
    """

    pk = payload["inputs"]["job_pk"]
    sk = payload["inputs"]["job_sk"]
    exec_status = payload["execStatus"]
    resp = update_job(pk=pk, sk=sk, exec_status=exec_status)
    if resp:
        return resp
    raise DataBaseOperationError("From Process request can not update the Database.")


# In[ ]:


def handler(event, context):
    """Handler function for the API gateway"""
    param_list = ["inputs", "execStatus"]
    try:
        request = event
        query_parameter_ok(param_list, request)
        resp = process_request(payload=request)
        resp = json.loads(json.dumps(resp, cls=DecimalEncoder))
        return {"statusCode": 200, "data": resp["data"]}
    except ParameterMissingError as e:
        LOGGER.printlog(e)
        return {"statusCode": 500, "data": {}}
    except Exception as e:
        LOGGER.printlog(e)
        return {"statusCode": 500, "data": {}}

