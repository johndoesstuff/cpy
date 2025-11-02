test:
	python3 tocpy.py test.py test.cpy
	python3 topy.py test.cpy test_round.py
	diff test.py test_round.py
