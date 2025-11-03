import sys
import tokenize
from io import BytesIO

def main():
    if len(sys.argv) < 2:
        print("Usage: python test_tokenize.py <filename> [output_file]")
        sys.exit(1)

    filename = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None

    with open(filename, "r", encoding="utf-8") as f:
        code = f.read()

    tokens = tokenize.tokenize(BytesIO(code.encode("utf-8")).readline)
    roundtrip_code = tokenize.untokenize(tokens).decode("utf-8")

    if output_file:
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(roundtrip_code)
    else:
        print(roundtrip_code)

if __name__ == "__main__":
    main()
