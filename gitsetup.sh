#!/bin/bash -e
git remote remove origin
git remote add -f origin https://$GIT_SECRET:x-oauth-basic@github.com/wavespotter/sofar-api-client-python.git
git checkout master
git merge --no-edit staging
git config --local user.name $GIT_NAME
git config --local user.email $GIT_EMAIL