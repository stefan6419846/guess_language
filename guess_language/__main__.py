"""Guess the natural language of a text
"""

import argparse
import os
import sys

import guess_language

DEFAULT_ENCODING = "utf-8"


def parse_args():
    parser = argparse.ArgumentParser(
        description=__doc__.strip(),
        prog="{} -m {}".format(os.path.basename(sys.executable),
                               "guess_language")
    )
    parser.add_argument("file", nargs="?", help="plain text file")
    parser.add_argument("--encoding", dest="encoding", help="input encoding")
    parser.add_argument("--disable-enchant", dest="use_enchant",
                        action="store_false", help="disable enchant")
    return parser.parse_args()


def main():
    args = parse_args()
    if args.file:
        file = args.file
        encoding = args.encoding if args.encoding else DEFAULT_ENCODING
    else:
        file = sys.stdin.fileno()
        encoding = args.encoding if args.encoding else sys.stdin.encoding
    with open(file, encoding=encoding) as f:
        text = "\n".join(f.readlines())
    guess_language.USE_ENCHANT = args.use_enchant
    tag = guess_language.guess_language(text)
    print(tag)
    return 0 if tag else 1


if __name__ == "__main__":
    sys.exit(main())
