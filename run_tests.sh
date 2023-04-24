#!/bin/bash

# exit when any command fails
set -e

./run_flake8.sh

tput setaf 6; printf "Running tests\n"
tput sgr0; python -m pytest tests --cov=. --cov-config=.coveragerc
tput setaf 2; printf "OK!\n\n"