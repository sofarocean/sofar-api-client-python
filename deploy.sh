#!/bin/bash -e
twine upload dist/*
git add dist/
git commit --ammend --no-edit
git push origin master