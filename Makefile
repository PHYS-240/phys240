.PHONY: test docs serve clean

test:
	pytest -q

docs:
	sphinx-build -b html -W --keep-going -n docs docs/_build/html

serve: docs
	python3 -m http.server -d docs/_build/html 8000

clean:
	rm -rf docs/_build .pytest_cache __pycache__
