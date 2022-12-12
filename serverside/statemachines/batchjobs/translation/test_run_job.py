from sagemaker.session import Session
from sagemaker.sklearn.processing import SKLearnProcessor
from sagemaker.processing import ProcessingInput, ProcessingOutput
from dotenv import load_dotenv
import os
from pathlib import Path

load_dotenv()

BASE_PATH = Path('/opt')
ML_PATH = BASE_PATH.joinpath("ml")
PROCESSING_PATH = ML_PATH.joinpath("processing")
INPUT_PATH = PROCESSING_PATH.joinpath("input")
OUTPUT_PATH = PROCESSING_PATH.joinpath("output")
EXECUTION_ROLE = os.environ["SAGEMAKER_ARN"]
BUCKET = os.environ["BUCKET"]


input_meta = [
    ProcessingInput(
        source=os.environ["TEST_DOC_INPUT_PATH"],
        destination=str(INPUT_PATH.resolve())
    )
]

output_meta = [
    ProcessingOutput(
        source=str(OUTPUT_PATH.resolve()),
        output_name='output',
        destination=os.environ["TEST_DOC_OUTPUT_PATH"]
    ),
]


sklearn_processor = SKLearnProcessor(
    framework_version='0.20.0',
    role=EXECUTION_ROLE,
    instance_type='ml.t3.medium',
    instance_count=1,
    sagemaker_session=Session(default_bucket=os.environ["BATCH_JOB_BUCKET"])
)

sklearn_processor.run(
    code='main.py',
    inputs=input_meta,
    outputs=output_meta,
    arguments=[
        "--bucket", BUCKET,
        "--file", "document.docx",
    ]
)