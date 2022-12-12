import boto3
from dotenv import load_dotenv
import os

load_dotenv()

BUCKET = os.environ['BUCKET']
SESSION = boto3.session.Session()
DYNAMODB_RESOURCE = SESSION.resource('dynamodb')
DYNAMO_TABLE = DYNAMODB_RESOURCE.Table(os.environ['DB_NAME'])

artifact_data = {
    "PK": "artf#artifact",
    "SK": "model",
    "entity_type": "model",
    "parent_entity_type": "artifact",
    "bucket": BUCKET,
    "bucket_key": "models/v0.0.1/"
}
DYNAMO_TABLE.put_item(Item=artifact_data)

job_data = {
        "PK": "artf#artifact",
        "SK": "job#job1",
        "entity_type": "job",
        "parent_entity_type": "artifact",
        "bucket": BUCKET,
        "bucket_key": "artifacts/jobs/doc-translation/"
}

DYNAMO_TABLE.put_item(Item=job_data)
DYNAMO_TABLE.get_item(Key={"PK": "artf#artifact", "SK": "job#job1"})