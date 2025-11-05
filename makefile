.PHONY: test
.PHONY: testtok

PY_FILES := $(shell cat test_files.txt)
PY_ENC_FILES := $(shell cat test_encoding.txt)

test:
	@errors=0; \
	failed_files=""; \
	for file in $(PY_FILES); do \
		echo "Testing $$file..."; \
		cpy_file="$${file%.py}.cpy"; \
		round_file="$${file%.py}_round.py"; \
		python3 tocpy.py "$$file" "$$cpy_file"; \
		python3 topy.py "$$cpy_file" "$$round_file"; \
		if ! diff "$$file" "$$round_file"; then \
			errors=$$((errors + 1)); \
			failed_files="$$failed_files $$file"; \
		fi; \
	done; \
	echo ""; \
	echo "=============================="; \
	if [ $$errors -eq 0 ]; then \
		echo "All tests passed!"; \
	else \
		echo "$$errors/2152 test(s) failed."; \
		echo "Failed files:$$failed_files"; \
	fi

test_encoding:
	@errors=0; \
	failed_files=""; \
	for file in $(PY_ENC_FILES); do \
		echo "Testing $$file..."; \
		cpy_file="$${file%.py}.cpy"; \
		round_file="$${file%.py}_round.py"; \
		python3 tocpy.py "$$file" "$$cpy_file"; \
		python3 topy.py "$$cpy_file" "$$round_file"; \
		if ! diff "$$file" "$$round_file"; then \
			errors=$$((errors + 1)); \
			failed_files="$$failed_files $$file"; \
		fi; \
	done; \
	echo ""; \
	echo "=============================="; \
	if [ $$errors -eq 0 ]; then \
		echo "All tests passed!"; \
	else \
		echo "$$errors/2152 test(s) failed."; \
		echo "Failed files:$$failed_files"; \
	fi

testtok:
	@for file in $(PY_FILES); do \
		echo "Testing default tokenizer on $$file..."; \
		round_file="$${file%.py}_round.py"; \
		python3 test_tokenize.py "$$file" "$$round_file"; \
		diff "$$file" "$$round_file" || echo "Differences found in $$file"; \
	done

vim:
	mkdir -p ~/.vim/syntax
	sudo cp cpy.vim ~/.vim/syntax/cpy.vim
	mkdir -p ~/.vim/ftdetect
	echo "au BufRead,BufNewFile *.cpy set filetype=cpy" > ~/.vim/ftdetect/cpy.vim
