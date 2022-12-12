#!/bin/bash

jupyter nbconvert --to script nb-dev-get-project.ipynb
mv nb-dev-get-project.py get_project.py
echo creating pyfile: get_project.py
