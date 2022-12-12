#!/bin/bash

jupyter nbconvert --to script nb-dev-get-german-doc.ipynb
mv nb-dev-get-german-doc.py get_german_doc.py
echo "pyfile created get_german_doc.py"

