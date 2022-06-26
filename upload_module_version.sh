#!/bin/bash

# exit when any command fails
set -e

# linting trials application
tput setaf 6; printf "Uploading module version\n"
tput sgr0; twine upload dist/*
tput setaf 2; printf "Done!\n\n"