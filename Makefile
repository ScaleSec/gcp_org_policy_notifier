
venv:
	python3 -m venv venv3
	. venv3/bin/activate
	python -m pip install --upgrade pip
	pip install -r src/requirements.txt
	
test: 
	scripts/test.sh

deploy: venv
	terraform init
	terraform apply

.PHONY: all