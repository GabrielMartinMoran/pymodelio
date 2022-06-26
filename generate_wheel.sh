#!/bin/bash

# exit when any command fails
set -e

# linting trials application
rm -rf build
rm -rf dist
tput setaf 6; printf "Generating wheel file\n"
tput sgr0; python setup.py bdist_wheel
tput setaf 2; printf "Done!\n\n"