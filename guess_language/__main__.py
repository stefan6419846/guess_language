"""Guess the natural language of a text
"""

import argparse
import sys

import guess_language


def parse_args():
    parser = argparse.ArgumentParser(
        description=__doc__.strip(),
        prog="{} -m {}".format(sys.executable, "guess_language")
    )
    parser.add_argument("--encoding", dest="encoding", help="input encoding")
    parser.add_argument("--no-enchant", dest="use_enchant",
                        action="store_false", help="don't use enchant")
    return parser.parse_args()


def main():
    args = parse_args()
    encoding = (args.encoding if args.encoding
                else sys.stdin.encoding if sys.stdin.isatty() else "utf-8")
    with open(sys.stdin.fileno(), encoding=encoding) as f:
        text = "\n".join(f.readlines())
    guess_language.USE_ENCHANT = args.use_enchant
    tag = guess_language.guess_language(text)
    print(tag)
    return 0 if tag else 1


if __name__ == "__main__":
    sys.exit(main())
