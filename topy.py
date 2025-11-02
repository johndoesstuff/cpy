import re, sys

TOKEN_SPEC = [
    ('FUNC',    r'\bfunc\b'),
    ('COMMENT', r'/\*.*?\*/'),
    ('NUMBER',  r'\b\d+(\.\d+)?\b'),
    ('STRING',  r'\".*?\"|\'.*?\''),
    ('OP',      r'[:=+\-*/(){}\.,<>%\[\]@!|]'),
    ('NAME',    r'\b\w+\b'),
    ('WS',      r'\s+'),
]

token_regex = '|'.join(f'(?P<{name}>{regex})' for name, regex in TOKEN_SPEC)
pattern = re.compile(token_regex, re.DOTALL)

def c_like_tokenize(code):
    for m in pattern.finditer(code):
        kind = m.lastgroup
        value = m.group()
        yield kind, value

def tok_topy(tokens):
    for kind, value in tokens:
        if kind == 'FUNC':
            yield 'def'
        elif kind == 'NAME' and value == 'def':
            yield 'func'
        elif kind == 'COMMENT':
            # remove /* */ and convert to #
            comment_text = value[2:-2]
            yield f"#{comment_text}"
        else:
            yield value

def c_untokenize(tokens):
    return ''.join(tokens)

def main():
    if len(sys.argv) < 2:
        print("Usage: python topy.py <filename>")
        sys.exit(1)

    filename = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None


    # read
    with open(filename, 'r', encoding='utf-8') as f:
        code = f.read()

    # tokenize, convert, and untokenize
    tokens = c_like_tokenize(code)
    py_tokens = tok_topy(tokens)
    py_code = c_untokenize(py_tokens)

    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(py_code)
    else:
        print(py_code)


if __name__ == "__main__":
    main()
