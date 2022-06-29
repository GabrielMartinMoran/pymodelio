#!/bin/bash

# exit when any command fails
set -e

tput setaf 6; printf "Running flake8 for linting checking\n"
tput sgr0; python -m flake8 .
tput setaf 2; printf "OK!\n\n"