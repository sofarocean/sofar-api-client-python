#!/bin/bash -e
pip install twine
python setup.py sdist bdist_wheel
twine upload --repository-url https://test.pypi.org/legacy/ dist/*
pip install --index-url https://test.pypi.org/legacy/ --no-deps pysofar

