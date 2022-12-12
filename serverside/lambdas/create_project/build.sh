#!/bin/bash

jupyter nbconvert --to script nb-dev-create-project.ipynb
mv nb-dev-create-project.py create_project.py
echo creating pyfile: create_project.py
