import tokenize_rt, re, sys, tokenize
from io import BytesIO

def read_python_file(filename, encoding):
    with open(filename, 'rb') as f:
        f.seek(0)
        return f.read().decode(encoding)

# convert token stream to c-like tokens
def tok_toc(tokens):
    fstring_level = 0;
    for tok in tokens:
        if tok.name == 'FSTRING_START':
            fstring_level += 1
        elif tok.name == 'FSTRING_END':
            fstring_level -= 1

        if fstring_level > 0:
            yield tok
            continue

        if tok.name == 'NAME' and tok.src == "def":
            yield tok._replace(src="func")
        elif tok.name == 'NAME' and tok.src == "func": # avoid namespace collisions
            yield tok._replace(src="def")
        elif tok.name == 'NAME' and tok.src == "elif":
            yield tok._replace(src="else if")
        elif tok.name == 'COMMENT':
            # // is floor div
            comment_text = tok.src[1:]
            comment_text = comment_text.replace("*/", "\\*/");
            yield tok._replace(src=f"/*{comment_text} */") # whitespace after to avoid (# \) -> (/* \*/) -> (# ->)
        else:
            yield tok
    return tokens

def main():
    if len(sys.argv) < 2:
        print("Usage: python tocpy.py <filename>")
        sys.exit(1)

    filename = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None

    # read
    with open(filename, 'rb') as f:
        encoding, _ = tokenize.detect_encoding(f.readline)
        f.seek(0)
        src_bytes = f.read()
        src = src_bytes.decode(encoding)

    # tokenize, convert, and untokenize
    tokens = tokenize_rt.src_to_tokens(src)
    tokens_c = list(tok_toc(tokens))
    c_like = tokenize_rt.tokens_to_src(tokens_c)

    if output_file:
        with open(output_file, 'w', encoding=encoding, errors='surrogateescape') as f:
            f.write(c_like)
    else:
        for tok in tokens:
            print(tok)
        print(c_like)

if __name__ == "__main__":
    main()

