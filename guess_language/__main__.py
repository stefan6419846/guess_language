"""Command-line script for guess_language
"""
import argparse
import sys

import guess_language


def parse_args():
    parser = argparse.ArgumentParser(
        description=guess_language.__doc__.strip())
    parser.add_argument("--encoding", dest="encoding")
    return parser.parse_args()


def main():
    args = parse_args()
    encoding = (args.encoding if args.encoding
                else sys.stdin.encoding if sys.stdin.isatty() else "utf-8")
    with open(sys.stdin.fileno(), encoding=encoding) as f:
        text = "\n".join(f.readlines())
    print(guess_language.guess_language(text))


if __name__ == "__main__":
    sys.exit(main())
