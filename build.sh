#!/bin/bash -e

# script to build & push pysofar to testing/production

pip="python3 -m pip"

usage() {
    echo "$(basename $0) [--test|--prod]"
    echo
    echo "supply --test to push to test.pypi.org"
    echo "supply --prod to push to production PyPI"
}

setup() {
    ${pip} install twine
    python3 setup.py sdist bdist_wheel
}

testing() {
    # For Test PyPi:
    # https://packaging.python.org/en/latest/guides/using-testpypi/
    #
    setup
    # password is the API token located in 1Password: search for test.pypi.org
    twine upload --username __token__ --repository testpypi dist/*
    ${pip} install --index-url https://test.pypi.org/simple/ --no-deps --upgrade pysofar
}

production() {
    # For production PyPi:
    setup
    twine upload dist/*
    ${pip} install --index-url https://test.pypi.org/legacy/ --no-deps pysofar
}

main() {
    # execute testing or production according to user wishes
    if [[ $1 = "--test" ]]
    then 
        testing
    elif [[ $1 = "--prod" ]]
    then 
        production
    else
        usage
    fi
}

# handle args
case $# in
    1) main $1;;
    *) usage; exit 1;;
esac

