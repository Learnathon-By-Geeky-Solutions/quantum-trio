coverage:
	coverage run -m pytest
	coverage report
	coverage xml

test:
	pytest
