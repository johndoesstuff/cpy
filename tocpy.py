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
    block_starts = [
        'struct',
        'func',
        'if',
        'else',
        'else if',
        'for',
        'while',
        'try',
        'except',
        'finally',
        'with',
    ]
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
            continue

        tok = swap_keywords(tok, keyword_swaps)

        if tok.name == 'NAME' and tok.src == "is":
            if (next_token and next_token.name == 'NAME' and next_token.src == 'not'):
                tokens[i] = tok._replace(src="!==")
                del tokens[i+1:j+1]
            else:
                tokens[i] = tok._replace(src="===")
        elif tok.name == 'COMMENT':
            # // is floor div
            comment_text = tok.src[1:]
            comment_text = comment_text.replace("*/", "\\*/");
            tokens[i] = tok._replace(src=f"/*{comment_text} */") # whitespace after to avoid (# \) -> (/* \*/) -> (# ->)
        elif tok.name == 'INDENT':
            # we have indented, there must exist a : that has caused us to do this, replace it with {
            prev_colon = None
            j = i - 1
            while j >= 0:
                pt = tokens[j]
                if pt.name == 'OP':
                    prev_colon = pt
                    break
                j -= 1
            assert prev_colon.src == ':'
            tokens[j] = prev_colon._replace(src=" {")
            tokens[i] = tok
        elif tok.name == 'DEDENT':
            tokens[i] = tok._replace(src=tok.src+"} ")
        elif tok.name == 'NAME' and tok.src in block_starts: 
            # check for edge case where block is single lined
            # for example:
            #
            # func thing(): stuff
            #
            # will fail regular blocking because no indent/dedent tokens are produced
            # to solve this we check until next ':' token after a block keyword that
            # isnt nested in () and detect if an indent is created or if the block is inlined
            paren_depth = 0
            j = i + 1
            while j < len(tokens):
                nt = tokens[j]
                if nt.name == 'OP' and nt.src == '(':
                    paren_depth += 1
                elif nt.name == 'OP' and nt.src == ')':
                    paren_depth -= 1
                elif nt.name == 'OP' and nt.src == ':' and paren_depth == 0:
                    break
                j += 1
            colon_i = j

            # we are now at the colon after a block start, lets check if there
            # is a newline first, or a non-WS token first

            j += 1
            while j < len(tokens):
                nt = tokens[j]
                if nt.name != 'UNIMPORTANT_WS' and nt.name != 'COMMENT':
                    break
                j += 1
            next_nonwsi = j

            # if not triggered, after ':' we recieve a newline, all is good and we will
            # resolve this when we parse indent tokens
            if tokens[next_nonwsi].name != 'NEWLINE':
                while j < len(tokens):
                    nt = tokens[j]
                    if nt.name == 'NEWLINE':
                        break
                    j += 1
                next_nli = j
                # something has been found after : but before newline,
                # we need to wrap in {} up until newline
                if tokens[colon_i + 1].name == 'UNIMPORTANT_WS': # if ws before statement put { after ws
                    tokens[colon_i] = tokens[colon_i]._replace(src='') # delete colon
                    tokens[colon_i + 1] = tokens[colon_i + 1]._replace(src=tokens[colon_i + 1].src + '{') # delete colon
                else:
                    tokens[colon_i] = tokens[colon_i]._replace(src='{')
                tokens[next_nli] = tokens[next_nli]._replace(src='}' + tokens[next_nli].src)
            tokens[i] = tok

        else:
            tokens[i] = tok

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

