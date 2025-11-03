.PHONY: test
.PHONY: testtok

PY_FILES := $(shell cat test_files.txt)

test:
	@for file in $(PY_FILES); do \
		echo "Testing $$file..."; \
		cpy_file="$${file%.py}.cpy"; \
		round_file="$${file%.py}_round.py"; \
		python3 tocpy.py "$$file" "$$cpy_file"; \
		python3 topy.py "$$cpy_file" "$$round_file"; \
		diff -w "$$file" "$$round_file" || echo "Differences found in $$file"; \
	done

testtok:
	@for file in $(PY_FILES); do \
		echo "Testing default tokenizer on $$file..."; \
		round_file="$${file%.py}_round.py"; \
		python3 test_tokenize.py "$$file" "$$round_file"; \
		diff "$$file" "$$round_file" || echo "Differences found in $$file"; \
	done
