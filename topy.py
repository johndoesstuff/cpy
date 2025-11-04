import re, sys, tokenize

TOKEN_SPEC = [
    ('FUNC',    r'\bfunc\b'),
    ('NUMBER',  r'\b\d+(\.\d+)?\b'),
    ('STRINGM',  r'((?<!\\)(?:\\\\)*\"\"\"[\s\S]*?(?<!\\)(?:\\\\)*\"\"\")|((?<!\\)(?:\\\\)*\'\'\'[\s\S]*?(?<!\\)(?:\\\\)*\'\'\')'),
    ('STRINGD',  r'\"(?:\\\n|\\.|[^\"\\])*\"'),
    ('STRING',  r'\'(?:\\\n|\\.|[^\'\\])*\''),
    ('COMMENT', r'/\*(?:[^*\\]|\\.|(?:\*+(?!/)))*\*/'),
    ('OP',      r'[:=+\-*/(){}\.,<>%\[\]@!\|\~?\^\\&;]'),
    ('NAME',    r'\b\w+\b'),
    ('WS',      r'\s+'),
]

token_regex = '|'.join(f'(?P<{name}>{regex})' for name, regex in TOKEN_SPEC)
pattern = re.compile(token_regex, re.DOTALL)


def get_file_encoding(filename):
    with open(filename, 'rb') as f:
        encoding, _ = tokenize.detect_encoding(f.readline)
        return encoding

def read_python_file(filename, encoding):
    with open(filename, 'rb') as f:
        f.seek(0)
        return f.read().decode(encoding)

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
            comment_text = value[2:-3]
            # for handling cases like: (# */) -> (/* \*/*/) -> (# */)
            comment_text = comment_text.replace("\\*/", "*/")
            yield f"#{comment_text}"
        else:
            yield value

def c_untokenize(tokens):
    code_str = ''.join(tokens)
    return code_str


def main():
    if len(sys.argv) < 2:
        print("Usage: python topy.py <filename>")
        sys.exit(1)

    filename = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None

    # read
    encoding = get_file_encoding(filename)
    code = read_python_file(filename, encoding)

    # tokenize, convert, and untokenize
    tokens = c_like_tokenize(code)
    py_tokens = tok_topy(tokens)
    py_code = c_untokenize(py_tokens)

    if output_file:
        with open(output_file, 'w', encoding=encoding) as f:
            f.write(py_code)
    else:
        tokens = c_like_tokenize(code)
        for tok in tokens:
            print(tok)
        print(py_code)


if __name__ == "__main__":
    main()
