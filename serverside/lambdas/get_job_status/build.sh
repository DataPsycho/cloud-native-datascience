#!/bin/bash

jupyter nbconvert --to script nb-dev-get-job-status.ipynb
mv nb-dev-get-job-status.py get_job_status.py
