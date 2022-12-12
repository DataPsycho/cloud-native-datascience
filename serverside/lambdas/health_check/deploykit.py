import os
import logging
from zipfile import ZipFile

import boto3
from dotenv import load_dotenv

assert load_dotenv('../../../.env')

logging.basicConfig(
    format='%(asctime)s [%(levelname)s] %(name)s - %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S',
)
logger = logging.getLogger(__name__)


SESSION = boto3.session.Session()
S3_CLEINT = SESSION.client('s3')
LAMBDA_CLIENT = SESSION.client('lambda')


def add_py_files(writter: ZipFile) -> None:
    for file in os.listdir('microkit'):
        if ".py" in file:
            logger.info(f"{file} file added")
            writter.write(os.path.join('microkit', file))
    for file in os.listdir():
        if file.endswith('.py') and 'deploykit' not in file:
            logger.info(f"{file} file added")
            writter.write(file)
    logger.info("Pyfile zipped!")


def build_package(filename, add_external_package=False):
    with ZipFile(filename, 'w') as zf:
        add_py_files(zf)
    logger.info("Package Zipped")


def upload_package(filename: str, bucket: str, key: str):
    S3_CLEINT.upload_file(
        Filename=filename,
        Bucket=bucket,
        Key=key,
        ExtraArgs={'ServerSideEncryption': 'aws:kms'}
    )
    logger.info(f"Zipfile Uploaded into s3://{bucket}/{key}")


def deploy_pacakge(
        function_name: str, handler: str, desc: str, env_vars: dict, code_info: dict, timeout=180, memory_size=512
):
    try:
        LAMBDA_CLIENT.create_function(
            FunctionName=function_name,
            Runtime="python3.8",
            Role=os.environ["LAMBDA_ARN"],
            Handler=f"{handler}.handler",
            Description=desc,
            Code=code_info,
            PackageType="Zip",
            Publish=True,
            Timeout=timeout,
            MemorySize=memory_size,
            Environment=env_vars,
            Tags={"project": "doc_translation"}
        )
        logger.info("Lambda Created")
    except InterruptedError as e:
        raise InterruptedError(f"Could not create lambda function: {e}")


def update_package_code(function_name: str, bucket: str, key: str):
    try:
        LAMBDA_CLIENT.update_function_code(
            FunctionName=function_name,
            S3Bucket=bucket,
            S3Key=key,
            Publish=True,
        )
        logger.info("Lambda Code Updated")
    except InterruptedError as e:
        raise InterruptedError(f"Could not create lambda function: {e}")


def update_env_vars(function_name: str, envvars: dict):
    try:
        LAMBDA_CLIENT.update_function_configuration(
            FunctionName=function_name,
            Environment=envvars
        )
        logger.info("Environ Variables Updated")
    except InterruptedError as e:
        raise InterruptedError(f"Could not update lambda function: {e}")
