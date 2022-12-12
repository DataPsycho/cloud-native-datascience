#!/bin/bash

#echo "=== Testing with MyPy ==="
#mypy --ignore-missing-imports --disallow-untyped-defs -p "clientside"


echo "=== Testing with Flake8 ==="
flake8 --max-line-length=150 \
  --ignore=F821,W292,E302,E305,W391,W503,W504