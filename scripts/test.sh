#!/bin/bash

source test.env

venv_name="temp_venv"


#TODO: source env vars, move this to bash script

python3 -m venv $venv_name
source $venv_name/bin/activate
pip install -r src/requirements.txt > /dev/null
python -m unittest discover -s tests
rm -rf $venv_name