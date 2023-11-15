#!/usr/bin/env bash

# This is to be run during the Docker build process to setup the devcontainer.

echo "Installing python packages ..."

python3 -m pip install -r requirements.txt
pip install --upgrade pip
rm requirements.txt

echo "Build commands complete"