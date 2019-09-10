install:
	pip3 install --user -e .

format:
	black .

clean:
	rm -rf ./__pycache__ *.egg-info
