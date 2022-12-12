import logging
import typing as t

import pandas as pd
from app.domains.project import PostProjectPayload, Project
from app.usecases import CLIENT
from app.usecases.exceptions import UseCaseConversionException


def get_all_projects() -> t.List[Project]:
    path = "projects"
    result = CLIENT.get(path=path)
    if result.success:
        data = [Project(**item) for item in result.data]
        return data
    logging.info(result.trace)
    raise UseCaseConversionException(result.trace)


def get_project_as_list():
    projects = get_all_projects()
    project_list = [item.SK for item in projects]
    project_list = ["---"] + project_list
    return project_list


def get_project_as_table() -> pd.DataFrame:
    projects = get_all_projects()
    projects = [item.dict() for item in projects]
    df = pd.DataFrame(projects)
    col_list = ["SK", "name", "updated_by", "document", "active", "updated_at"]
    df = df[col_list]
    col_schema = {"SK": "pid"}
    df = df.rename(columns=col_schema)
    df = df.sort_values("updated_at", ascending=False)
    return df


def create_project(payload: PostProjectPayload) -> Project:
    path = "projects"
    result = CLIENT.post(path=path, body=payload.json())
    if result.success:
        return Project(**result.data)
    logging.info(result.trace)
    raise UseCaseConversionException(result.trace)


if __name__ == "__main__":
    get_all_projects()
    get_project_as_list()
    get_project_as_table()