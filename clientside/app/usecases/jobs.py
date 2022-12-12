import logging
import typing as t

import pandas as pd
from app.domains.jobs import (GetJobStatusPayload, PostJobPayload,
                              TranslationJob)
from app.usecases import CLIENT
from app.usecases.exceptions import UseCaseConversionException


def get_jobs(payload: GetJobStatusPayload) -> t.List[TranslationJob]:
    path = "jobs"
    result = CLIENT.get(path=path, query=payload.dict())
    if result.success:
        return [TranslationJob(**item) for item in result.data]
    logging.info(result.trace)
    raise UseCaseConversionException(result.trace)


def get_jobs_as_table(payload: GetJobStatusPayload) -> pd.DataFrame:
    result = get_jobs(payload)
    col_list = ["pid", "version", "requested_by", "status", "requested_at", "finished_at"]
    df = pd.DataFrame([item.dict() for item in result])
    df = df[col_list]
    df = df.sort_values("requested_at", ascending=False)
    return df


def create_translation_job(payload: PostJobPayload):
    path = "jobs"
    result = CLIENT.post(path=path, body=payload.json())
    if result.success:
        return TranslationJob(**result.data)
    logging.info(result.trace)
    raise UseCaseConversionException(result.trace)


if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    import os
    _payload = GetJobStatusPayload(pid=os.environ["TEMP_PROJECT_NAME"])
    get_jobs(_payload)
    get_jobs_as_table(_payload)

    _payload = PostJobPayload(sk=os.environ["TEMP_PROJECT_NAME"])
    path = "jobs"
    result = CLIENT.post(path=path, body=_payload.json())
