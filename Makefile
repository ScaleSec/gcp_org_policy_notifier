
venv:
	python3 -m venv venv3
	venv3/bin/python -m pip install --upgrade pip
	venv3/bin/pip install -r src/requirements.txt
	
test: 
	scripts/test.sh

deploy: venv
	terraform init
	terraform apply

.PHONY: all