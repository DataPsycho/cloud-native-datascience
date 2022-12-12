#!/bin/bash

source ../../../.env

aws s3 rm s3://$BUCKET/artifacts/jobs/doc-translation --recursive
aws s3 cp translation/ s3://$BUCKET/artifacts/jobs/doc-translation/ --recursive