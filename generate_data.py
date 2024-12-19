"""
Generate the data subpackage
"""

import re
import shutil
import sys
from operator import itemgetter
from pathlib import Path


FOLDED_NAMES = {
    "Latin-1 Supplement": "Extended Latin",
    "Latin Extended-A": "Extended Latin",
    "IPA Extensions": "Extended Latin",
    "Hiragana": "Kana",
    "Katakana": "Kana",
    "Katakana Phonetic Extensions": "Kana",
}
MAX_BLOCKS = 0x2FA1F
BLOCK_RSHIFT = 4
PACKAGE_NAME = "guess_language"
SCRIPT_DIR = Path(__file__).parent
DATA_DIR = Path(SCRIPT_DIR, PACKAGE_NAME, "data")
BLOCKS_PATH = Path(DATA_DIR, "__init__.py")
MODELS_DIR = Path(DATA_DIR, "models")
TRIGRAMS_DIR = Path(SCRIPT_DIR, "trigrams")
BLOCKS_URL = "http://unicode.org/Public/UNIDATA/Blocks.txt"
BLOCKS_FN = "Blocks.txt"
ENCODING = "utf-8"
MAX_GRAMS = 300


def make_data_dir():
    for dir_path in [DATA_DIR, MODELS_DIR]:
        if not dir_path.exists():
            dir_path.mkdir(parents=True)
        init_path = dir_path / "__init__.py"
        init_path.touch()


def download_file(remote, local):
    from urllib.request import urlopen
    from contextlib import closing

    with closing(urlopen(remote)) as inf:
        with open(local, "wb") as ouf:
            while True:
                data = inf.read()
                if not data:
                    break
                ouf.write(data)


def build_blocks():
    blocks_path = SCRIPT_DIR / BLOCKS_FN

    if not blocks_path.exists():
        download_file(BLOCKS_URL, blocks_path)

    splitter = re.compile(r"^([0-9A-F]+)\.\.([0-9A-F]+);\s*(.*)$", re.I)

    with BLOCKS_PATH.open("w", newline="\n") as f:
        f.write(f"BLOCK_RSHIFT = {BLOCK_RSHIFT!r}\n")
        f.write(f"BLOCKS = [None] * {MAX_BLOCKS + 1 >> BLOCK_RSHIFT:#x}\n")

        for line in blocks_path.read_text().splitlines():
            if line.startswith("#"):
                continue

            m = splitter.match(line)

            if not m:
                continue

            start = int(m.group(1), 16)
            end = int(m.group(2), 16) + 1
            name = m.group(3)

            if all(not chr(n).isalpha() for n in range(start, end)):
                continue

            shifted_start = start >> BLOCK_RSHIFT
            shifted_end = end >> BLOCK_RSHIFT

            assert shifted_start << BLOCK_RSHIFT == start
            assert shifted_end << BLOCK_RSHIFT == end

            if name in FOLDED_NAMES:
                comment = name
                name = FOLDED_NAMES[name]
            else:
                comment = None

            s = "BLOCKS[{:#x}:{:#x}] = [{!r}] * {:#x}{}\n".format(
                shifted_start,
                shifted_end,
                name,
                shifted_end - shifted_start,
                "  # " + comment if comment else "",
            )
            f.write(s)

            if end >= MAX_BLOCKS:
                break


def build_models():
    line_re = re.compile(r"^(.{3})\s+(.*)$")
    consecutive_spaces_re = re.compile(r"\s{2,}", re.U)

    for model_path in sorted(TRIGRAMS_DIR.glob("*")):
        if model_path.is_dir():
            continue

        model = {}  # QHash<QString,int> model

        with model_path.open(encoding=ENCODING) as f:
            for n, line in enumerate(f):
                m = line_re.match(line)
                if m:
                    value = m.group(1)
                    assert not consecutive_spaces_re.search(value)
                    assert n == int(m.group(2))
                    model[value] = n
            assert len(model) == MAX_GRAMS

        path = MODELS_DIR / f"{model_path.name.lower()}.py"

        with path.open("w", encoding=ENCODING, newline="\n") as f:
            f.write("MODEL = {{\n")
            for k, v in sorted(model.items(), key=itemgetter(1)):
                f.write(f" {k!r}: {v!r},\n")
            f.write("}\n")


def generate_data(overwrite=False):
    if DATA_DIR.is_dir():
        if overwrite:
            shutil.rmtree(DATA_DIR)
        else:
            return

    make_data_dir()
    build_blocks()
    build_models()


def setup_hook(config):
    generate_data()


if __name__ == "__main__":
    sys.exit(generate_data(overwrite=True))
