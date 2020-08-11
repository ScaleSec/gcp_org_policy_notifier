#!/bin/bash

source test.env

venv_name="temp_venv"

if ! [ -d $venv_name ]; then
  python3 -m venv $venv_name
  pip install -r src/requirements.txt > /dev/null
fi

source $venv_name/bin/activate
python -m unittest discover -s tests