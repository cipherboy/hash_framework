check:
	python3 -c 'import hash_framework'
	python3 -m pytest

install:
	pip3 install --user -e .

format:
	black .

clean:
	rm -rf ./__pycache__ *.egg-info
