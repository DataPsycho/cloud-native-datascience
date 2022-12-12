#!/bin/bash

jupyter nbconvert --to script nb-dev-create-job.ipynb
mv nb-dev-create-job.py create_job.py
echo creating pyfile: create_job.py
