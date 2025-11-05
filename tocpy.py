import tokenize_rt, re, sys, tokenize
from io import BytesIO

def read_python_file(filename, encoding):
    with open(filename, 'rb') as f:
        f.seek(0)
        return f.read().decode(encoding)

# convert token stream to c-like tokens
def tok_toc(tokens):
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

        # replace def with func
        if tok.name == 'NAME' and tok.src == "def":
            yield tok._replace(src="func")
        elif tok.name == 'NAME' and tok.src == "func": # avoid namespace collisions
            yield tok._replace(src="def")

        # lowercase true and false
        elif tok.name == 'NAME' and tok.src == "True":
            yield tok._replace(src="true")
        elif tok.name == 'NAME' and tok.src == "true": # avoid namespace collisions
            yield tok._replace(src="True")
        elif tok.name == 'NAME' and tok.src == "False":
            yield tok._replace(src="false")
        elif tok.name == 'NAME' and tok.src == "false": # avoid namespace collisions
            yield tok._replace(src="False")

        # logic
        elif tok.name == 'NAME' and tok.src == "and":
            yield tok._replace(src="&&")
        elif tok.name == 'NAME' and tok.src == "or":
            yield tok._replace(src="||")
        elif tok.name == 'NAME' and tok.src == "is":
            if (next_token and next_token.name == 'NAME' and next_token.src == 'not'):
                i = j
                yield tok._replace(src="!==")
            else:
                yield tok._replace(src="===")
        elif tok.name == 'NAME' and tok.src == "not":
            yield tok._replace(src="!")

        # None -> NULL
        elif tok.name == 'NAME' and tok.src == "None":
            yield tok._replace(src="NULL")
        elif tok.name == 'NAME' and tok.src == "NULL": # avoid namespace collisions
            yield tok._replace(src="None")

        # break elif into else and if
        elif tok.name == 'NAME' and tok.src == "elif":
            yield tok._replace(src="else if")

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

