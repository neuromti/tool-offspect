SHELL := /bin/bash #to be able to execute `source`

.PHONY: docs
docs:
	make -C docs clean html

.PHONY: build
build: clean
	python setup.py sdist bdist_wheel

.PHONY: clean
clean:
	rm -rf dist */*.egg-info *.egg-info  build
	rm -rf .env

.PHONY: test
test: build
	tests/runtest

.PHONY: upload
upload: build
	twine check dist/*
	twine upload dist/* --verbose

.PHONY: docs
docs:
	#rm -rf docs/source/_autosummary
	make -C docs clean html