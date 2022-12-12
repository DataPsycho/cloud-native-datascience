#!/usr/bin/env python
# coding: utf-8

# In[1]:


import json
import typing as t

import boto3

from domainmodel import ExecutonSchemaJob, Job, Project
from microkit.exceptions import (
    ContentNotFoundError,
    DataBaseOperationError,
    JobInitError,
    ParameterMissingError,
    create_response_from_exception,
    create_response_from_not_found_exception,
    create_response_from_param_exception,
    query_parameter_ok,
)
from microkit.logger import get_logger
from microkit.orm import DynamoOrm, get_job_artifact_path, get_model_artifact_path
from microkit.utils import DecimalEncoder, collect_cet_now, load_env_vars, load_extra_env_vars

# In[2]:


# In[ ]:


LOGGER = get_logger(str(__name__))
ENV_VARS = load_env_vars()
ENV_VARS_EXTRAS = load_extra_env_vars()


# In[ ]:


SESSION = boto3.session.Session()
S3_CLEINT = SESSION.client('s3')
DYNAMODB_RESOURCE = SESSION.resource('dynamodb')
DYNAMO_TABLE = DYNAMODB_RESOURCE.Table(ENV_VARS.db)
S3_RESOURCE = SESSION.resource("s3")


# In[ ]:


# Env Specific to the lambda
SFN_CLIENT = SESSION.client('stepfunctions')
WORKFLOW_ARN = ENV_VARS_EXTRAS.sfn_arn
JOBTYPE = "job1"


# # Create A New Job

# In[ ]:


def has_required_files(pid: str) -> str:
    pk = "proj#project"
    sk = pid
    template = Project(PK=pk, SK=sk, name='', updated_by='', updated_at='')
    handler = DynamoOrm(template, DYNAMO_TABLE)
    resp = handler.get_item()
    if resp["status"] == 200:
        try:
            new_data = Project.from_dict(resp["data"])
            resource = S3_RESOURCE.Object(bucket_name=new_data.bucket, key=new_data.bucket_key)
            resource.load()
            return f"s3://{new_data.bucket}/{new_data.bucket_key}"
        except Exception as e:
            LOGGER.info(e)
            raise ContentNotFoundError(f"Document not found for the project: {sk}")
    raise DataBaseOperationError(f"Metadata for the following key does not exist {pk}:{sk}")


# In[ ]:


def put_version_0(pid: str, entity_type: str, requested_by: str) -> t.Dict:
    """
    Create a new version zero for a project when no job has been initiated
    :param pid: Project ID for which to create a job
    :param entity_type: Job Type to create
    :param requested_by: The 521 requested the job
    """
    job = Job.from_v0(pid, entity_type)
    job.set_run(0)
    job.set_requested_by(requested_by)
    dynamo_handler = DynamoOrm(job, DYNAMO_TABLE)
    resp = dynamo_handler.put_item()
    if resp["status"] == 200:
        return resp
    raise DataBaseOperationError("Can not put version 0")


# In[ ]:


def query_version_0(pid: str, entity_type: str) -> Job:
    """
    Query the current status of version 0 from the given project id
    :param pid: Project ID for which to create a job
    :param entity_type: Job Type to create
    """
    job = Job.from_v0(pid, entity_type)
    dynamo_handler = DynamoOrm(job, DYNAMO_TABLE)
    resp = dynamo_handler.get_item()
    if resp["status"] == 200:
        return Job.from_dict(resp["data"])
    return None


# In[ ]:


def update_db_with_job_rejected(resp: t.Dict):
    """Update dynamodb with job rejected
    param: resp: A Dict searizable object for the job
    """
    try:
        data = resp["data"]
        data["status"] = "rejected"
        data["finished_at"] = collect_cet_now()
        job = Job.from_dict(data)
        handler = DynamoOrm(job, DYNAMO_TABLE)
        db_resp = handler.update_all()
        resp["data"] = db_resp["data"]
        resp["status"] = 500
        return resp
    except Exception as e:
        LOGGER.info(e)
        raise DataBaseOperationError(e)


# In[ ]:


def create_new_job(pid: str, job_type: str, requested_by: str):
    """
    Create a new job from the given project id
    :param pid: Project ID for which to create a job
    :param job_type: Job Type to create
    :param requested_by: The 521 requested the job
    """
    try:
        version_0_job = query_version_0(pid, job_type)
        if version_0_job:
            new_run = version_0_job.run + 1
            new_version = f"v{new_run}"
            job = Job.from_attribute_data(pid, job_type, new_version, requested_by)
            job.set_run(new_run)
            handler = DynamoOrm(job, DYNAMO_TABLE)
            resp = handler.put_item()
            if resp["status"] == 200:
                version_0_job.set_run(new_run)
                v0_handler = DynamoOrm(version_0_job, DYNAMO_TABLE)
                v0_handler.update_all()
            return resp
        resp = put_version_0(pid, job_type, requested_by)
        return resp
    except Exception as e:
        LOGGER.info(e)
        raise DataBaseOperationError(e)


# In[ ]:


def get_running_jobs_by_project(pid: str, entity_type: str):
    """Get all the running jobs if there is any"""
    version0_job = query_version_0(pid, entity_type)
    if version0_job is None:
        return []
    hash_info = {"name": "parent_entity_pid", "value": version0_job.parent_entity_pid}
    range_info = {"name": "status_jid", "pattern": "running"}
    handler = DynamoOrm(version0_job, DYNAMO_TABLE)
    resp = handler.get_item_by_index_begins_with(
        index="JobStatusIndex",
        hash_key=hash_info,
        range_pattern=range_info
    )
    if resp["status"] == 200:
        return resp["data"]
    return []


# In[ ]:


def lunch_step_function(exec_schema: ExecutonSchemaJob) -> None:
    """Lunch a step function from all the inputs
    :param ExecutonSchemaJob instance for Job type 2
    """
    try:
        _ = SFN_CLIENT.start_execution(
            stateMachineArn=WORKFLOW_ARN,
            input=json.dumps(exec_schema.to_dict())
        )
        return None
    except Exception as e:
        LOGGER.info(e)
        raise JobInitError("Can not initialize the job.")


# In[ ]:


def process_request(payload: t.Dict, job_type: str) -> t.Dict:
    """
    Then acting main function which handle the whole process from the payload inputs
    param: payload: request payload
    param: jobtype: Type of the job it start to initiate
    """

    pid = payload["sk"]
    requested_by = payload["requested_by"]

    # Check if the document is added
    doc_uri = has_required_files(pid=pid)

    # Check if any previous job is running
    running_jobs = get_running_jobs_by_project(pid, job_type)
    if len(running_jobs) > 0:
        job_info = ", ".join([f"{item['PK']} : {item['SK']}" for item in running_jobs])
        error = JobInitError(f"There is already job running for that project {job_info}")
        raise error

    # Now create new job
    resp = create_new_job(pid, job_type=JOBTYPE, requested_by=requested_by)
    if resp["status"] == 200:
        try:
            data = resp["data"]
            job_repo = Job.from_dict(data)
            exec_schema = ExecutonSchemaJob(
                SOURCE_TO_TRANSLATE=doc_uri,
                DESTINATION_OUTPUT=job_repo.get_s3_path(),
                SOURCE_MODEL_ARTIFACT=get_model_artifact_path(resource=DYNAMO_TABLE),
                job_pk=job_repo.PK,
                job_sk=job_repo.SK,
                input_code=get_job_artifact_path(resource=DYNAMO_TABLE, job_type=JOBTYPE)
            )
            exec_schema.reset_job_name(suffix=job_repo.jid)
            lunch_step_function(exec_schema=exec_schema)
        except Exception as e:
            _ = update_db_with_job_rejected(resp)
            raise e
    return resp


# In[ ]:


def handler(event, context):
    """Handler function for the API gateway
    :param event: Query Event
    :param context: Metadata about the Lambda
    """
    param_list = ["sk", "requested_by"]
    try:
        request = json.loads(event["body"])
        query_parameter_ok(expected=param_list, requested=request)
        resp = process_request(request, job_type=JOBTYPE)
        return {"statusCode": resp["status"], "body": json.dumps(resp, cls=DecimalEncoder)}
    except ParameterMissingError as e:
        LOGGER.info(e)
        return create_response_from_param_exception(exception=e, data={})
    except JobInitError as e:
        LOGGER.info(e)
        return create_response_from_exception(exception=e, data={})
    except DataBaseOperationError as e:
        LOGGER.info(e)
        return create_response_from_exception(exception=e, data={})
    except FileNotFoundError as e:
        LOGGER.info(e)
        return create_response_from_not_found_exception(exception=e, data={})
    except Exception as e:
        LOGGER.info(e)
        return create_response_from_exception(exception=e, data={})

