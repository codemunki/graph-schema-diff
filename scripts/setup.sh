#!/bin/bash

VENV=".venv"

# Cleanup previous installations
deactivate
rm -rf $VENV

python3 -m venv $VENV
source $VENV/bin/activate

# Install python bindings for llama cpp
CMAKE_ARGS="-DGGML_CUDA=on" pip install llama-cpp-python

# Install remaining requirements.txt
pip install -r requirements.txt

# Download required models (can take some time)
./models/download-models.sh
