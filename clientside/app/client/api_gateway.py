import logging
import typing as t
from dataclasses import dataclass

import requests
from requests import Response


@dataclass
class Result:
    data: t.Optional[dict] = None
    trace: t.Optional[str] = None
    success: t.Optional[bool] = True


class ApiError(Exception):
    pass


class Client:
    def __init__(self, api_url):
        self.api_url = api_url
        self.content_type = "application/json"
        self.header = {"Content-Type": self.content_type}

    def __create_url(self, path: str) -> str:
        return f"{self.api_url}/{path}"

    @staticmethod
    def convert_response_to_result(response: Response) -> Result:
        default_trace = "ApiError: No data from serverside."
        result = response.json()
        if response.status_code == 200:
            return Result(data=result["data"])
        try:
            error = result.get("errorMessage", {}).get("trace", default_trace)
            return Result(trace=error, success=False)
        except ApiError as e:
            logging.info(e)
            return Result(trace=default_trace, success=False)
        except Exception as e:
            logging.info(e)
            return Result(trace=default_trace, success=False)

    def get(self, path: str, query: t.Optional[dict] = None):
        url = self.__create_url(path)

        req = {"url": url, "headers": self.header}
        if query:
            req["params"] = query
        response = requests.get(**req)
        return self.convert_response_to_result(response)

    def post(self, path, body: dict):
        url = self.__create_url(path)
        response = requests.post(url=url, data=body, headers=self.header)
        return self.convert_response_to_result(response)


if __name__ == "__main__":
    import os

    from dotenv import load_dotenv
    load_dotenv()
    client = Client(api_url=os.environ["API_URL"])
    # result = client.get(path="projects")
    # print(result)
    # base_url = os.environ["API_URL"]
    # endpoint = "projects"
    # # Success resp
    # resp = requests.get(url=f"{base_url}/{endpoint}")
    # resp.json()
    # # Fail response
    # endpoint = "jobs"
    # resp = requests.get(url=f"{base_url}/{endpoint}")
    # client.convert_response_to_result(resp)
    #
    # # Success response
    # query = {"pid": os.environ["TEMP_PROJECT_NAME"], "status": "all"}
    # response = requests.get(url=f"{base_url}/{endpoint}", params=query)
    # client.convert_response_to_result(response)
