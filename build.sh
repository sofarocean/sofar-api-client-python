#!/bin/bash -e
pip install twine
python setup.py sdist bdist_wheel
# For Test PyPi:
#twine upload --repository-url https://test.pypi.org/legacy/ dist/*
# For production PyPi:
twine upload dist/*
pip install --index-url https://test.pypi.org/legacy/ --no-deps pysofar

