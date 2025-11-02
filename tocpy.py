import tokenize, re
from io import BytesIO

code = b'''
def foo(x):
    # hello
    return x + 1
'''

# convert token stream to c-like tokens
def tok_toc(tokens):
    for tok in tokens:
        if tok.type == tokenize.NAME and tok.string == "def":
            yield tok._replace(string="func")
        elif tok.type == tokenize.COMMENT:
            # // is floor div
            comment_text = tok.string[1:].strip()
            yield tok._replace(string=f"/* {comment_text} */")
        else:
            yield tok
    return tokens


print(c_like)

def main():
    if len(sys.argv) < 2:
        print("Usage: python tocpy.py <filename>")
        sys.exit(1)

    filename = sys.argv[1]

    # read
    with open(filename, 'r', encoding='utf-8') as f:
        code = f.read()

    # tokenize, convert, and untokenize
    tokens = tokenize.tokenize(BytesIO(code).readline)
    tokens_c = tok_toc(tokens)
    c_like = tokenize.untokenize(tokens_c).decode('utf-8')

    print(c_like)

if __name__ == "__main__":
    main()

