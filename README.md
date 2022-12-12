# Cloud Native Data Science Product
The repository contains a fully featured cloud native NLP product build with AWS stack. Following AWS service is being heavily used in the Product development:
- ApiGateway, Lambda for backend api
- Dynamodb as database storage
- Step Function as a BatchJob scheduler
- Sagemaker Processing Job as batch job container
- S3 for large file storage

## Roles and Policies:
To be able to make the whole application work following roles and policies needed to be created and added into the environment variables.
Here is the Environment variable list:

```shell
export BUCKET="<your-bucket>"
export DB_NAME="<your-database>"
export BATCH_JOB_BUCKET="<bucket-for-sagemaker-processing-job>"
export SAGEMAKER_ARN="<sagemaker-arn-to-initiate-processing-job>"
export LAMBDA_ARN="<arn for lambda role>"
export STEP_FUNCTION_ARN="<step function role arn>"
export SFN_WORKFLOW_ARN="step function workflow arn"
export API_GATEWAY_ARN="<api gateway role arn for cloud watch>"
export API_URL="<url for the api>"
```

## Policies for the Roles:
The policies for the roles are loosely defined, you should be more strict while adding policies into the roles.

- SAGEMAKER_ARN:
  - s3FullAccess
  - DynamoDBFullAccess
  - StepFunctionFullAccess
  - Lambda_FullAccess
- LAMBDA_ARN:
  - s3FullAccess
  - APIGatewayInvokeFullAccess
  - LambdaExecute
  - StepFunctionFullAccess
- STEP_FUNCTION_ARN:
  - LambdaRole
  - Lambda_FullAccess
  - CloudWatchEventsFullAccess
  - Custom Pass role from Step Function to Sagemaker

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "VisualEditor0",
            "Effect": "Allow",
            "Action": [
                "events:PutTargets",
                "events:DescribeRule",
                "events:PutRule"
            ],
            "Resource": [
                "arn:aws:events:*:*:rule/StepFunctionsGetEventsForSageMakerTrainingJobsRule",
                "arn:aws:events:*:*:rule/StepFunctionsGetEventsForSageMakerTransformJobsRule",
                "arn:aws:events:*:*:rule/StepFunctionsGetEventsForSageMakerTuningJobsRule",
                "arn:aws:events:*:*:rule/StepFunctionsGetEventsForECSTaskRule",
                "arn:aws:events:*:*:rule/StepFunctionsGetEventsForBatchJobsRule"
            ]
        },
        {
            "Sid": "VisualEditor1",
            "Effect": "Allow",
            "Action": "iam:PassRole",
            "Resource": "*",
            "Condition": {
                "StringEquals": {
                    "iam:PassedToService": "sagemaker.amazonaws.com"
                }
            }
        },
        {
            "Sid": "VisualEditor2",
            "Effect": "Allow",
            "Action": [
                "batch:DescribeJobs",
                "batch:SubmitJob",
                "batch:TerminateJob",
                "lambda:InvokeFunction",
                "sagemaker:CreateEndpoint",
                "sagemaker:CreateEndpointConfig",
                "sagemaker:CreateHyperParameterTuningJob",
                "sagemaker:CreateModel",
                "sagemaker:CreateProcessingJob",
                "sagemaker:CreateTrainingJob",
                "sagemaker:CreateTransformJob",
                "sagemaker:DeleteEndpoint",
                "sagemaker:DeleteEndpointConfig",
                "sagemaker:DescribeHyperParameterTuningJob",
                "sagemaker:DescribeProcessingJob",
                "sagemaker:DescribeTrainingJob",
                "sagemaker:DescribeTransformJob",
                "sagemaker:ListProcessingJobs",
                "sagemaker:ListTags",
                "sagemaker:StopHyperParameterTuningJob",
                "sagemaker:StopProcessingJob",
                "sagemaker:StopTrainingJob",
                "sagemaker:StopTransformJob",
                "sagemaker:UpdateEndpoint",
                "sns:Publish",
                "sqs:SendMessage"
            ],
            "Resource": "*"
        }
    ]
}
```
**This is not a good example of adding role where I have full access everytime please use more restricted access, this is just for demo purpose.**
- API_GATEWAY_ARN:
  - APIGatewayPushToCloudWatchLogs
  - Lambda_FullAccess

# ClientSide
The client side is written in Streamlit which can be found at the clientside directory.

# Serverside
The serverside is written as http api with each endpoint has its own pure python script deployed as lambda.
