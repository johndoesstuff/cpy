import re, sys, tokenize
from io import BytesIO

TOKEN_SPEC = [
    ('NUMBER',  r'\b\d+(\.\d+)?\b'),
    ('STRINGM',  r'((?<!\\)(?:\\\\)*\"\"\"[\s\S]*?(?<!\\)(?:\\\\)*\"\"\")|((?<!\\)(?:\\\\)*\'\'\'[\s\S]*?(?<!\\)(?:\\\\)*\'\'\')'),
    ('STRINGD',  r'\"(?:\\\n|\\.|[^\"\\])*\"'),
    ('STRING',  r'\'(?:\\\n|\\.|[^\'\\])*\''),
    ('COMMENT', r'/\*(?:[^*\\]|\\.|(?:\*+(?!/)))*\*/'),
    ('AND',     r'&&'),
    ('OR',      r'\|\|'),
    ('IS',      r'==='),
    ('ISNOT',   r'!=='),
    ('NEQ',     r'!='),
    ('NOT',     r'!'),
    ('OP',      r'[:=+\-*/(){}\.,<>%\[\]@!\|\~?\^\\&;]'),
    ('NAME',    r'\b\w+\b'),
    ('WS',      r'\s+'),
]

token_regex = '|'.join(f'(?P<{name}>{regex})' for name, regex in TOKEN_SPEC)
pattern = re.compile(token_regex, re.DOTALL)

encoding = None

def get_file_encoding(filename):
    global encoding
    with open(filename, 'rb') as f:
        encoding, _ = tokenize.detect_encoding(f.readline)
        return encoding

def read_python_file(filename):
    global encoding
    with open(filename, 'rb') as f:
        src_bytes = f.read()

    # try to detect encoding
    if encoding is None:
        try:
            encoding, _ = tokenize.detect_encoding(BytesIO(src_bytes).readline)
        except (SyntaxError, LookupError):
            encoding = 'utf-8'

    # latin1 fallback if utf-8 fails
    try:
        return src_bytes.decode(encoding)
    except UnicodeDecodeError:
        encoding = 'latin1'
        return src_bytes.decode('latin1')

def c_like_tokenize(code):
    for m in pattern.finditer(code):
        kind = m.lastgroup
        value = m.group()
        yield kind, value

def swap_keywords(kind, value, swaps):
    # swap keywords bidirectionally
    if kind != 'NAME':
        return value

    for orig, repl in swaps.items():
        if value == orig:
            return repl
        elif value == repl:
            return orig
    return value


def tok_topy(tokens):
    keyword_swaps = {
        "func":    "def",
        "struct":  "class",
        "include": "import",
        "using":   "from",
        "true":    "True",
        "false":   "False",
        "NULL":    "None",
    }
    tokens = list(tokens)
    i = 0
    while i < len(tokens):
        kind, value = tokens[i]

        # find next non-whitespace token
        next_kind = next_value = None
        j = i + 1
        while j < len(tokens):
            nk, nv = tokens[j]
            if nk != 'WS':  # or 'WHITESPACE'
                next_kind, next_value = nk, nv
                break
            j += 1
        
        value = swap_keywords(kind, value, keyword_swaps)

        # logic
        if kind == 'AND':
            yield 'and'
        elif kind == 'OR':
            yield 'or'
        elif kind == 'IS':
            yield 'is'
        elif kind == 'ISNOT':
            yield 'is not'
        elif kind == 'NOT':
            yield 'not'

        # else if goes back to elif
        elif kind == 'NAME' and value == 'else':
            if next_kind == 'NAME' and next_value == 'if':
                yield 'elif'
                i = j  # skip over the 'if' token
            else:
                yield 'else'

        # strip comments
        elif kind == 'COMMENT':
            comment_text = value[2:-3].replace("\\*/", "*/")
            yield f"#{comment_text}"
        else:
            yield value

        i += 1

def c_untokenize(tokens):
    code_str = ''.join(tokens)
    return code_str


def main():
    global encoding
    if len(sys.argv) < 2:
        print("Usage: python topy.py <filename>")
        sys.exit(1)

    filename = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None

    # read
    encoding = get_file_encoding(filename)
    code = read_python_file(filename)

    # tokenize, convert, and untokenize
    tokens = c_like_tokenize(code)
    py_tokens = tok_topy(tokens)
    py_code = c_untokenize(py_tokens)

    if output_file:
        with open(output_file, 'w', encoding=encoding, errors='surrogateescape') as f:
            f.write(py_code)
    else:
        tokens = c_like_tokenize(code)
        for tok in tokens:
            print(tok)
        print(py_code)


if __name__ == "__main__":
    main()
