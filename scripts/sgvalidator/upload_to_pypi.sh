#!/usr/bin/env bash
# publishing instructions here: https://packaging.python.org/tutorials/packaging-projects/
# NOTE: If you see HTTPError: 400 Client Error: File already exists, it means you probably haven't updated the version
rm -r dist/*
python3 -m pip install --user --upgrade twine setuptools wheel
python3 setup.py sdist bdist_wheel
<<<<<<< HEAD
python3 -m twine upload dist/*
=======
python3 -m twine upload dist/*
>>>>>>> origin/master
