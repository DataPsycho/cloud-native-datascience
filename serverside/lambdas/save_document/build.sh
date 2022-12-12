#!/bin/bash

jupyter nbconvert --to script nb-dev-save-dossier.ipynb
mv nb-dev-save-dossier.py save_docx.py
echo creating pyfile: save_docx.py
