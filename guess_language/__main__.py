"""Command-line script for guess_language
"""
import argparse
import sys

import guess_language


def parse_args():
    parser = argparse.ArgumentParser(
        description=guess_language.__doc__.strip())
    parser.add_argument("--encoding", dest="encoding")
    parser.add_argument("--no-enchant", dest="use_enchant",
                        action="store_false")
    return parser.parse_args()


def main():
    args = parse_args()
    encoding = (args.encoding if args.encoding
                else sys.stdin.encoding if sys.stdin.isatty() else "utf-8")
    with open(sys.stdin.fileno(), encoding=encoding) as f:
        text = "\n".join(f.readlines())
    guess_language.USE_ENCHANT = args.use_enchant
    print(guess_language.guess_language(text))


if __name__ == "__main__":
    sys.exit(main())
