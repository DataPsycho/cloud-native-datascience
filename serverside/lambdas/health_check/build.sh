#!/bin/bash

jupyter nbconvert --to script nb-dev-health-check.ipynb
mv nb-dev-health-check.py health_check.py
echo creating pyfile: health_check.py
