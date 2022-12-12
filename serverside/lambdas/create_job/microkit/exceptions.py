import json
import typing as t


class ContentNotFoundError(Exception):
    """Exception class to handle database operation error when inserting data or updating data"""

    def __init__(self, message=None):
        self.message = self.create_message(message)
        super().__init__(self.message)

    def create_message(self, custom_msg: t.Optional[str] = None):
        if custom_msg:
            return custom_msg
        return "File not found in the requested location"


class ParameterMissingError(Exception):
    """Exception raised for errors in the input salary.

    Attributes:
        expected, requested
    """

    def __init__(self, expected, requested) -> None:
        """Init for the ParameterMissingError class"""
        self.expected = expected
        self.requested = requested
        self.message = self.create_message()
        super().__init__(self.message)

    def create_message(self) -> str:
        """Create error message from the validation"""
        missing_fields = []
        for item in self.expected:
            if item not in self.requested:
                missing_fields.append(item)
        return "Following field are requered to query the api: {}".format(", ".join(missing_fields))


class ParameterValueError(Exception):
    def __init__(self, expected: list, requested: str):
        self.expected = expected
        self.requested = requested
        self.message = self.create_message()
        super().__init__(self.message)

    def create_message(self):
        return "{} is not a valid query parameter for the request. The Valid parameters are: {}".format(self.requested, ", ".join(self.expected))


class DataBaseOperationError(Exception):
    """Exception class to handle database operation error when inserting data or updating data"""

    def __init__(self, message=None):
        self.message = self.create_message(message)
        super().__init__(self.message)

    def create_message(self, custom_msg: t.Optional[str] = None):
        if custom_msg:
            return custom_msg
        return "Could not peform database operation at the moment."


class JobInitError(Exception):
    """Exception class to handle Stepfunction Job initiation error when starting a job"""

    def __init__(self, message=None):
        self.message = self.create_message(message)
        super().__init__(self.message)

    def create_message(self, custom_msg: t.Optional[str] = None):
        if custom_msg:
            return custom_msg
        return "Could create a new job at the moment."


def query_parameter_ok(expected: t.List, requested: t.Dict) -> bool:
    """Check if the query parameters are properly provided, when request is a dictionary"""
    for item in expected:
        if item not in requested:
            raise ParameterMissingError(expected=expected, requested=requested)
    return True


def parameter_value_ok(expected: t.List, requested: str) -> bool:
    """Test if the parameter values are any valid field, when requeste is a single field"""
    if requested not in expected:
        raise ParameterValueError(expected=expected, requested=requested)
    return True


def create_response_from_exception(exception: Exception, data: t.Union[t.Dict, t.List]) -> t.Dict:
    """Create a Response failed output for the api final request"""
    error_msg = {"errorType": "InternalServerError", "httpStatus": 500, "trace": str(exception)}
    resp = {"statusCode": 500, "data": data, "errorMessage": error_msg}
    return {"statusCode": 500, "body": json.dumps(resp)}


def create_response_from_param_exception(exception: Exception, data: t.Union[t.Dict, t.List]) -> t.Dict:
    """Create a Response failed output for the api final request"""
    error_msg = {"errorType": "ParameterError", "httpStatus": 403, "trace": str(exception)}
    resp = {"statusCode": 403, "data": data, "errorMessage": error_msg}
    return {"statusCode": 403, "body": json.dumps(resp)}


def create_response_from_not_found_exception(exception: Exception, data: t.Union[t.Dict, t.List]) -> t.Dict:
    """Create a Response failed output for the api final request"""
    error_msg = {"errorType": "FileNotFoundError", "httpStatus": 404, "trace": str(exception)}
    resp = {"statusCode": 404, "data": data, "errorMessage": error_msg}
    return {"statusCode": 404, "body": json.dumps(resp)}


