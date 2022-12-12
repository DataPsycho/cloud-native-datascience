import argparse
import logging
import os
import sys
import time
from pathlib import Path

import boto3

BASE_PATH = Path('/opt').joinpath("ml")
PROCESSING_PATH = BASE_PATH.joinpath("processing")
CODE_PATH_LOCAL = BASE_PATH.joinpath("code")
PKG_PATH = CODE_PATH_LOCAL.joinpath('src')
INPUT_PATH = PROCESSING_PATH.joinpath("input")
OUTPUT_PATH = PROCESSING_PATH.joinpath("output")
MODEL_PATH = PROCESSING_PATH.joinpath("model")

CODE_PREFIX_CLOUD = 'artifacts/jobs/doc-translation'
MODEL_PREFIX_CLOUD = "models/v0.0.1"


def get_logger():
    root = logging.getLogger()
    if root.handlers:
        for handler in root.handlers:
            root.removeHandler(handler)
    logging.basicConfig(
        format='%(asctime)s [%(levelname)s] %(name)s - %(message)s',
        level=logging.INFO,
        datefmt='%Y-%m-%d %H:%M:%S',
    )
    return logging.getLogger(__name__)


LOGGER = get_logger()


def download_all_files(bucket: str, prefix: str, local_dir: Path):
    # initiate s3 resource
    if not os.path.exists(local_dir):
        os.makedirs(local_dir)
    s3_resource = boto3.resource('s3')
    # select bucket
    my_bucket = s3_resource.Bucket(bucket)
    # download file into current directory
    for s3_object in my_bucket.objects.filter(Prefix=prefix):
        filename = s3_object.key.split('/')[-1]
        local_path = os.path.join(local_dir, filename)
        my_bucket.download_file(s3_object.key, local_path)
        LOGGER.info(f"File download from {s3_object.key} into {local_path}.")
    LOGGER.info("All Package file downloaded successfully in {}.".format(local_dir))


def add_modules_to_path():
    pkg_path_str = PKG_PATH.joinpath("requirements.txt").resolve()
    os.system(
        'pip install --upgrade -r {}'.format(str(pkg_path_str))
    )
    extend_path = str(CODE_PATH_LOCAL.resolve())
    sys.path.extend([extend_path])
    LOGGER.info(f' {extend_path} added to PYTHONPATH.')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--bucket')
    parser.add_argument('--file')
    args, _ = parser.parse_known_args()
    LOGGER.info('Received arguments {}'.format(args))

    download_all_files(args.bucket, CODE_PREFIX_CLOUD, PKG_PATH)
    download_all_files(args.bucket, MODEL_PREFIX_CLOUD, MODEL_PATH)

    add_modules_to_path()

    from src.pipeline import Pipeline

    st = time.time()

    pipeline = Pipeline(
        eng_file=INPUT_PATH.joinpath(args.file),
        ger_file=OUTPUT_PATH.joinpath(args.file),
        artifact_path=MODEL_PATH
    )
    pipeline.execute()

    et = time.time()
    elapsed_time = round((et - st)/60, 3)
    LOGGER.info({"execution_time": elapsed_time})


if __name__ == "__main__":
    main()
