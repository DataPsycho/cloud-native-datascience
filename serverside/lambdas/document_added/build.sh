#!/bin/bash

jupyter nbconvert --to script nb-dev-doc-added.ipynb
mv nb-dev-doc-added.py doc_added.py
echo creating pyfile: doc_added.py
