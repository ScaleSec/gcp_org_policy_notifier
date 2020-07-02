
venv:
	python3 -m venv venv3
	. venv3/bin/activate
	python -m pip install --upgrade pip
	pip install -r src/requirements.txt
	
test: 
	python3 -m venv temp_venv
	. temp_venv/bin/activate
	pip install -r src/requirements.txt > /dev/null
	python -m unittest discover -s tests
	rm -rf temp_venv

deploy: venv
	terraform init
	terraform apply

.PHONY: all