import tokenize_rt, re, sys, tokenize
from io import BytesIO

def read_python_file(filename, encoding):
    with open(filename, 'rb') as f:
        f.seek(0)
        return f.read().decode(encoding)

def swap_keywords(tok, swaps):
    # swap keywords bidirectionally
    if tok.name != 'NAME':
        return tok

    src = tok.src
    for orig, repl in swaps.items():
        if src == orig:
            return tok._replace(src=repl)
        elif src == repl:
            return tok._replace(src=orig)  # avoid namespace collision
    return tok

# convert token stream to c-like tokens
def tok_toc(tokens):
    keyword_swaps = {
        "def": "func",
        "class": "struct",
        "import": "include",
        "from": "using",
        "True": "true",
        "False": "false",
        "None": "NULL",
        "elif": "else if",
        "and": "&&",
        "or": "||",
        "not": "!"
    }
    fstring_level = 0;
    tokens = list(tokens)
    i = 0
    while i < len(tokens):
        tok = tokens[i]

        next_token = None
        j = i + 1
        while j < len(tokens):
            nt = tokens[j]
            if nt.name != 'UNIMPORTANT_WS':
                next_token = nt
                break
            j += 1


        if tok.name == 'FSTRING_START':
            fstring_level += 1
        elif tok.name == 'FSTRING_END':
            fstring_level -= 1

        if fstring_level > 0:
            i += 1
            yield tok
            continue

        tok = swap_keywords(tok, keyword_swaps)

        if tok.name == 'NAME' and tok.src == "is":
            if (next_token and next_token.name == 'NAME' and next_token.src == 'not'):
                i = j
                yield tok._replace(src="!==")
            else:
                yield tok._replace(src="===")
        elif tok.name == 'COMMENT':
            # // is floor div
            comment_text = tok.src[1:]
            comment_text = comment_text.replace("*/", "\\*/");
            yield tok._replace(src=f"/*{comment_text} */") # whitespace after to avoid (# \) -> (/* \*/) -> (# ->)
        else:
            yield tok

        i += 1
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

