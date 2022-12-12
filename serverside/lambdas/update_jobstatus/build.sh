#!/bin/bash

jupyter nbconvert --to script nb-dev-update-jobstatus.ipynb
mv nb-dev-update-jobstatus.py update_jobstatus.py
echo creating pyfile: update_jobstatus.py
