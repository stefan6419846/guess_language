import sys
from .guess_language import guess_language


def main():
    for arg in sys.argv[1:]:
        print(guess_language(arg))


if __name__ == "__main__":
    sys.exit(main())
