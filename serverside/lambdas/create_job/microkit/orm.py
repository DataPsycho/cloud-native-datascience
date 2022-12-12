import dataclasses
import os

from boto3.dynamodb.table import TableResource
from botocore.exceptions import ClientError

from .datamodel import BaseDataModel
from .utils import add_s3_prefix


def create_path_from_source(resp: dict, source: str) -> str:
    """By given the response create the s3 path of the dictionary"""
    if resp["ResponseMetadata"]["HTTPStatusCode"] == 200:
        data = resp["Item"]
        if data["bucket"] and data["bucket_key"]:
            path = add_s3_prefix(os.path.join(data["bucket"], data["bucket_key"]))
            return path
        else:
            raise Exception(
                f"{source} location metadata is missing. ",
                f"You probably have not submitted any {source} for the project ",
                f"Or the {source} is not configured properly. ",
                "Please check if you have followed all the steps necessary to submit current request."
            )
    raise Exception("Could Not find metadata in database")


def get_model_artifact_path(resource: TableResource) -> str:
    resp = resource.get_item(Key={"PK": "artf#artifact", "SK": "model"})
    return create_path_from_source(resp, "Model")


def get_job_artifact_path(resource: TableResource, job_type: str) -> str:
    resp = resource.get_item(Key={"PK": "artf#artifact", "SK": f"job#{job_type}"})
    return create_path_from_source(resp, "Job")


def get_project_info_by_pid(resource: TableResource, pid: str) -> dict:
    resp = resource.get_item(Key={"PK": "proj#project", "SK": pid})
    if "Item" in resp:
        return resp
    return None


def get_dossier_path(resource: TableResource, pid: str) -> str:
    resp = get_project_info_by_pid(resource=resource, pid=pid)
    return create_path_from_source(resp, "Dossier")


def get_job_output_path(resource: TableResource, pid: str, job_type: str) -> str:
    resp = resource.get_item(Key={"PK": f"proj#{pid}", "SK": f"{job_type}#v0"})
    return create_path_from_source(resp, "Processing Job")


@dataclasses.dataclass
class DynamoOrm:
    """Handler composition for CRUD operation to dynamodb"""
    data: BaseDataModel
    table: TableResource

    def create_response(self, status: int, data=None):
        """Generic response creating method"""
        if data:
            return {"status": status, "data": data}
        return {"status": status, "data": self.data.to_dict()}

    def put_item(self):
        """Put item wrapper over dynamodb with conditional check"""
        try:
            response = self.table.put_item(
                Item=self.data.to_dict(),
                ConditionExpression="attribute_not_exists(PK) AND attribute_not_exists(SK)"
            )
            return self.create_response(response["ResponseMetadata"]["HTTPStatusCode"])
        except ClientError:
            return self.create_response(500)

    def get_item(self):
        """Get item wrapper for dynamo db"""
        response = self.table.get_item(
            Key={"PK": self.data.PK, "SK": self.data.SK}
        )
        if "Item" not in response:
            return self.create_response(500)
        return self.create_response(response["ResponseMetadata"]["HTTPStatusCode"], response["Item"])

    def get_item_begins_with(self, pattern: str):
        """Get item wrapper for dynamo db"""
        response = self.table.query(
            KeyConditionExpression="PK = (:val0) AND begins_with (SK, :val1)",
            ExpressionAttributeValues={':val0': self.data.PK, ":val1": pattern}
        )
        if "Items" not in response:
            return self.create_response(500)
        if len(response["Items"]) == 0:
            return self.create_response(500)
        return self.create_response(response["ResponseMetadata"]["HTTPStatusCode"], response["Items"])

    def get_item_by_index_begins_with(self, index: str, hash_key: dict, range_pattern: dict):
        """Get item wrapper for dynamo db"""
        pk = hash_key["name"]
        sk = range_pattern["name"]
        response = self.table.query(
            IndexName="JobStatusIndex",
            KeyConditionExpression=f"{pk} = (:val0) AND begins_with ({sk}, :val1)",
            ExpressionAttributeValues={':val0': hash_key["value"], ":val1": range_pattern["pattern"]}
        )
        if "Items" not in response:
            return self.create_response(500)
        if len(response["Items"]) == 0:
            return self.create_response(500)
        return self.create_response(response["ResponseMetadata"]["HTTPStatusCode"], response["Items"])

    def update_item(self, *args):
        """Update item wrapper for dynamodb"""
        for arg in args:
            if not hasattr(self.data, arg):
                raise AttributeError(f"Addribute {arg} does not exist")

        expression_deck = ", ".join([f"{item} = :val{i}" for i, item in enumerate(args)])
        exp = f"SET {expression_deck}"
        value_map = {f":val{i}": self.data.to_dict()[arg] for i, arg in enumerate(args)}
        try:
            response = self.table.update_item(
                Key={
                    "PK": self.data.PK,
                    "SK": self.data.SK
                },
                UpdateExpression=exp,
                ExpressionAttributeValues=value_map,
                ConditionExpression="attribute_exists(PK) AND attribute_exists(SK)"

            )
            return self.create_response(response["ResponseMetadata"]["HTTPStatusCode"])
        except ClientError:
            return self.create_response(500)

    def delete_item(self):
        try:
            response = self.table.delete_item(
                Key={
                    "PK": self.data.PK,
                    "SK": self.data.SK
                },
                ConditionExpression="attribute_exists(PK) AND attribute_exists(SK)"
            )
            return self.create_response(response["ResponseMetadata"]["HTTPStatusCode"])
        except ClientError:
            return self.create_response(500)

    def update_all(self):
        """Put item wrapper over dynamodb with conditional check"""
        try:
            response = self.table.put_item(
                Item=self.data.to_dict()
            )
            return self.create_response(response["ResponseMetadata"]["HTTPStatusCode"])
        except ClientError:
            return self.create_response(500)
