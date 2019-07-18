#!/usr/bin/env bash
# publishing instructions here: https://packaging.python.org/tutorials/packaging-projects/
rm -r dist/*
python3 -m pip install --user --upgrade twine setuptools wheel
python3 setup.py sdist bdist_wheel
python3 -m twine upload dist/*
