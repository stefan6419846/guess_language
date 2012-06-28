"""Guess the natural language of a text
"""
#   © 2012 spirit <hiddenspirit@gmail.com>
#   https://bitbucket.org/spirit/guess_language/
#
#   Original Python package:
#   Copyright (c) 2008, Kent S Johnson
#   http://code.google.com/p/guess-language/
#
#   Original C++ version for KDE:
#   Copyright (c) 2006 Jacob R Rideout <kde@jacobrideout.net>
#   http://websvn.kde.org/branches/work/sonnet-refactoring/common/nlp/guess_language.cpp?view=markup
#
#   Original Language::Guess Perl module:
#   Copyright (c) 2004-2006 Maciej Ceglowski
#   http://web.archive.org/web/20090228163219/http://languid.cantbedone.org/
#
#   Note: Language::Guess is GPL-licensed. KDE developers received permission
#   from the author to distribute their port under LGPL:
#   http://lists.kde.org/?l=kde-sonnet&m=116910092228811&w=2
#
#   This program is free software: you can redistribute it and/or modify it
#   under the terms of the GNU Lesser General Public License as published
#   by the Free Software Foundation, either version 3 of the License,
#   or (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty
#   of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#   See the GNU Lesser General Public License for more details.
#
#   You should have received a copy of the GNU Lesser General Public License
#   along with this program. If not, see <http://www.gnu.org/licenses/>.

import re
import unicodedata

from collections import defaultdict, namedtuple
from importlib import import_module

from .data import BLOCKS, BLOCK_RSHIFT


__all__ = ["guess_language", "guess_language_tag", "guess_language_name",
           "guess_language_id", "guess_language_info", "UNKNOWN"]

MIN_LENGTH = 20

BASIC_LATIN = [
    "en", "ceb", "ha", "so", "tlh", "id", "haw", "la", "sw", "eu",
    "nr", "nso", "zu", "xh", "ss", "st", "tn", "ts"
]
EXTENDED_LATIN = [
    "cs", "af", "pl", "hr", "ro", "sk", "sl", "tr", "hu", "az",
    "et", "sq", "ca", "es", "fr", "de", "nl", "it", "da", "is", "nb", "sv",
    "fi", "lv", "pt", "ve", "lt", "tl", "cy", "vi"
]
ALL_LATIN = BASIC_LATIN + EXTENDED_LATIN
CYRILLIC = ["ru", "uk", "kk", "uz", "mn", "sr", "mk", "bg", "ky"]
ARABIC = ["ar", "fa", "ps", "ur"]
DEVANAGARI = ["hi", "ne"]

# NOTE mn appears twice, once for mongolian script and once for CYRILLIC
SINGLETONS = [
    ("Armenian", "hy"),
    ("Hebrew", "he"),
    ("Bengali", "bn"),
    ("Gurmukhi", "pa"),
    ("Greek", "el"),
    ("Gujarati", "gu"),
    ("Oriya", "or"),
    ("Tamil", "ta"),
    ("Telugu", "te"),
    ("Kannada", "kn"),
    ("Malayalam", "ml"),
    ("Sinhala", "si"),
    ("Thai", "th"),
    ("Lao", "lo"),
    ("Tibetan", "bo"),
    ("Burmese", "my"),
    ("Georgian", "ka"),
    ("Mongolian", "mn-Mong"),
    ("Khmer", "km"),
]

PT = ["pt_BR", "pt_PT"]

NAME_MAP = {
    "ab": "Abkhazian",
    "af": "Afrikaans",
    "ar": "Arabic",
    "az": "Azeri",
    "be": "Byelorussian",
    "bg": "Bulgarian",
    "bn": "Bengali",
    "bo": "Tibetan",
    "br": "Breton",
    "ca": "Catalan",
    "ceb": "Cebuano",
    "cs": "Czech",
    "cy": "Welsh",
    "da": "Danish",
    "de": "German",
    "el": "Greek",
    "en": "English",
    "eo": "Esperanto",
    "es": "Spanish",
    "et": "Estonian",
    "eu": "Basque",
    "fa": "Farsi",
    "fi": "Finnish",
    "fo": "Faroese",
    "fr": "French",
    "fy": "Frisian",
    "gd": "Scots Gaelic",
    "gl": "Galician",
    "gu": "Gujarati",
    "ha": "Hausa",
    "haw": "Hawaiian",
    "he": "Hebrew",
    "hi": "Hindi",
    "hr": "Croatian",
    "hu": "Hungarian",
    "hy": "Armenian",
    "id": "Indonesian",
    "is": "Icelandic",
    "it": "Italian",
    "ja": "Japanese",
    "ka": "Georgian",
    "kk": "Kazakh",
    "km": "Cambodian",
    "ko": "Korean",
    "ku": "Kurdish",
    "ky": "Kyrgyz",
    "la": "Latin",
    "lt": "Lithuanian",
    "lv": "Latvian",
    "mg": "Malagasy",
    "mk": "Macedonian",
    "ml": "Malayalam",
    "mn": "Mongolian",
    "mr": "Marathi",
    "ms": "Malay",
    "nd": "Ndebele",
    "ne": "Nepali",
    "nl": "Dutch",
    "nn": "Nynorsk",
    "no": "Norwegian",
    "nso": "Sepedi",
    "pa": "Punjabi",
    "pl": "Polish",
    "ps": "Pashto",
    "pt": "Portuguese",
    "pt_PT": "Portuguese (Portugal)",
    "pt_BR": "Portuguese (Brazil)",
    "ro": "Romanian",
    "ru": "Russian",
    "sa": "Sanskrit",
    "sh": "Serbo-Croatian",
    "sk": "Slovak",
    "sl": "Slovene",
    "so": "Somali",
    "sq": "Albanian",
    "sr": "Serbian",
    "sv": "Swedish",
    "sw": "Swahili",
    "ta": "Tamil",
    "te": "Telugu",
    "th": "Thai",
    "tl": "Tagalog",
    "tlh": "Klingon",
    "tn": "Setswana",
    "tr": "Turkish",
    "ts": "Tsonga",
    "tw": "Twi",
    "uk": "Ukrainian",
    "uk": "Ukranian",
    "ur": "Urdu",
    "uz": "Uzbek",
    "ve": "Venda",
    "vi": "Vietnamese",
    "xh": "Xhosa",
    "zh": "Chinese",
    "zh_TW": "Traditional Chinese (Taiwan)",
    "zu": "Zulu",
}

IANA_MAP = {
    "ab": 12026,
    "af": 40,
    "ar": 26020,
    "az": 26030,
    "be": 11890,
    "bg": 26050,
    "bn": 26040,
    "bo": 26601,
    "br": 1361,
    "ca": 3,
    "ceb": 26060,
    "cs": 26080,
    "cy": 26560,
    "da": 26090,
    "de": 26160,
    "el": 26165,
    "en": 26110,
    "eo": 11933,
    "es": 26460,
    "et": 26120,
    "eu": 1232,
    "fa": 26130,
    "fi": 26140,
    "fo": 11817,
    "fr": 26150,
    "fy": 1353,
    "gd": 65555,
    "gl": 1252,
    "gu": 26599,
    "ha": 26170,
    "haw": 26180,
    "he": 26592,
    "hi": 26190,
    "hr": 26070,
    "hu": 26200,
    "hy": 26597,
    "id": 26220,
    "is": 26210,
    "it": 26230,
    "ja": 26235,
    "ka": 26600,
    "kk": 26240,
    "km": 1222,
    "ko": 26255,
    "ku": 11815,
    "ky": 26260,
    "la": 26280,
    "lt": 26300,
    "lv": 26290,
    "mg": 1362,
    "mk": 26310,
    "ml": 26598,
    "mn": 26320,
    "mr": 1201,
    "ms": 1147,
    "ne": 26330,
    "nl": 26100,
    "nn": 172,
    "no": 26340,
    "pa": 65550,
    "pl": 26380,
    "ps": 26350,
    "pt": 26390,
    "ro": 26400,
    "ru": 26410,
    "sa": 1500,
    "sh": 1399,
    "sk": 26430,
    "sl": 26440,
    "so": 26450,
    "sq": 26010,
    "sr": 26420,
    "sv": 26480,
    "sw": 26470,
    "ta": 26595,
    "te": 26596,
    "th": 26594,
    "tl": 26490,
    "tlh": 26250,
    "tn": 65578,
    "tr": 26500,
    "tw": 1499,
    "uk": 26510,
    "uk": 26520,
    "ur": 26530,
    "uz": 26540,
    "vi": 26550,
    "zh": 26065,
    "zh_TW": 22,
}

MODEL_ROOT = __package__ + ".data.models."
models = {}

LanguageInfo = namedtuple("LanguageInfo", ["tag", "id", "name"])


class UNKNOWN(str):
    def __bool__(self):
        return False


UNKNOWN = UNKNOWN("UNKNOWN")


def guess_language(text: str):
    """Return the language code, i.e. 'en'.
    """
    text = normalize(text)
    return _identify(text, find_runs(text)) or _identify_by_spellchecking(text)


def guess_language_info(text: str):
    """Return LanguageInfo(tag, id, name), i.e. ('en', 26110, 'English').
    """
    tag = guess_language(text)

    if tag is UNKNOWN:
        return LanguageInfo(UNKNOWN, UNKNOWN, UNKNOWN)

    id = _get_id(tag) #@ReservedAssignment
    name = _get_name(tag)
    return LanguageInfo(tag, id, name)


# An alias for guess_language
guess_language_tag = guess_language


def guess_language_id(text: str):
    """Return the language id, i.e. 26110.
    """
    lang = guess_language(text)
    return _get_id(lang)


def guess_language_name(text: str):
    """Return the language name, i.e. 'English'.
    """
    lang = guess_language(text)
    return _get_name(lang)


def _get_id(iana):
    return IANA_MAP.get(iana, UNKNOWN)


def _get_name(iana):
    return NAME_MAP.get(iana, UNKNOWN)


def find_runs(text):
    """Count the number of characters in each character block.
    """
    run_types = defaultdict(int)

    total_count = 0

    for c in text:
        if c.isalpha():
            block = BLOCKS[ord(c) >> BLOCK_RSHIFT]
            run_types[block] += 1
            total_count += 1

#    pprint(run_types)

    # return run types that used for 40% or more of the string
    # always return basic latin if found more than 15%
    # and extended additional latin if over 10% (for Vietnamese)
    relevant_runs = []
    for key, value in run_types.items():
        pct = value * 100 // total_count
        if pct >= 40:
            relevant_runs.append(key)
        elif key == "Basic Latin" and pct >= 15:
            relevant_runs.append(key)
        #elif key == "Latin Extended Additional" and pct >= 10:
            #relevant_runs.append(key)

    return relevant_runs


def _identify(sample, scripts):
    # if len(sample) < 3:
        # return UNKNOWN

    if "Hangul Syllables" in scripts or "Hangul Jamo" in scripts or \
            "Hangul Compatibility Jamo" in scripts or "Hangul" in scripts:
        return "ko"

    if "Greek and Coptic" in scripts:
        return "el"

    if "Kana" in scripts:
        return "ja"

    if "CJK Unified Ideographs" in scripts or "Bopomofo" in scripts or \
            "Bopomofo Extended" in scripts or "KangXi Radicals" in scripts:
        return "zh"

# This is in both Ceglowski and Rideout
# I can't imagine why...
#            or "Arabic Presentation Forms-A" in scripts
    if "Cyrillic" in scripts:
        return check(sample, CYRILLIC)

    if "Arabic" in scripts or "Arabic Presentation Forms-A" in scripts or \
            "Arabic Presentation Forms-B" in scripts:
        return check(sample, ARABIC)

    if "Devanagari" in scripts:
        return check(sample, DEVANAGARI)

    # Try languages with unique scripts
    for block_name, lang_name in SINGLETONS:
        if block_name in scripts:
            return lang_name

    #if "Latin Extended Additional" in scripts:
        #return "vi"

    if "Extended Latin" in scripts:
        latin_lang = check(sample, EXTENDED_LATIN)
        if latin_lang == "pt":
            return check(sample, PT)
        else:
            return latin_lang

    if "Basic Latin" in scripts:
        return check(sample, ALL_LATIN)

    return UNKNOWN


def check(sample, langs):
    if len(sample) < MIN_LENGTH:
        return UNKNOWN

    scores = []
    model = create_ordered_model(sample)  # QMap<int,QString>

    for key in langs:
        lkey = key.lower()

        try:
            known_model = models[lkey]
        except KeyError:
            try:
                known_model = import_module(MODEL_ROOT + lkey).model
            except ImportError:
                known_model = None
            models[lkey] = known_model

        if known_model:
            scores.append((distance(model, known_model), key))

    if not scores:
        return UNKNOWN

    # we want the lowest score, less distance = greater chance of match
    #pprint(sorted(scores))
    return min(scores)[1]


def create_ordered_model(content):
    """Create a list of trigrams in content sorted by frequency.
    """
    trigrams = defaultdict(int)  # QHash<QString,int>
    content = content.lower()

    for i in range(len(content) - 2):
        trigrams[content[i:i+3]] += 1

    return sorted(trigrams.keys(), key=lambda k: (-trigrams[k], k))


MAX_GRAMS = 300
CONSECUTIVE_SPACES_RE = re.compile(r"\s{2,}", re.U)


def distance(model, known_model):
    dist = 0

    for i, value in enumerate(model[:MAX_GRAMS]):
        if value in known_model:
            dist += abs(i - known_model[value])
        else:
            dist += MAX_GRAMS

    return dist


def normalize(s):
    """Convert to normalized string.

    Remove non-alpha characters and compress runs of spaces.
    """
    s = unicodedata.normalize("NFC", s)
    s = "".join(c if c.isalpha() else "'" if c in "'’" else " " for c in s)
    s = CONSECUTIVE_SPACES_RE.sub(" ", s)
    return s


try:
    import enchant
except ImportError:
    enchant = None

    def _identify_by_spellchecking(*args):
        return UNKNOWN
else:
    import locale

    def _identify_by_spellchecking(text, threshold=0.8, min_words=1,
                                   dictionaries={}):
        words = re.findall(r"[\w'’]+", text, re.U)

        if len(words) < min_words:
            return UNKNOWN

        max_score = 0
        max_tag = get_locale_language()

        for tag in list_enchant_languages():
            try:
                d = dictionaries[tag]
            except KeyError:
                d = dictionaries[tag] = enchant.Dict(tag)
            score = sum([1 for w in words if d.check(w)])
            if score > max_score:
                max_score = score
                max_tag = tag

        if max_score / len(words) < threshold:
            return UNKNOWN

        return max_tag if max_tag in NAME_MAP else max_tag.split("_")[0]

    def list_enchant_languages():
        """Get ordered list of enchant languages.

        locale_language, then en_US, then the rest.
        """
        global _enchant_languages

        if "_enchant_languages" not in globals():
            _enchant_languages = enchant.list_languages()

            for language in ["en_US", get_locale_language()]:
                for l in [language.split("_")[0], language]:
                    try:
                        index = _enchant_languages.index(l)
                    except ValueError:
                        pass
                    else:
                        _enchant_languages = (
                            [_enchant_languages[index]] +
                            _enchant_languages[:index] +
                            _enchant_languages[index+1:]
                        )

        return _enchant_languages

    def get_locale_language():
        """Get the language code for the current locale setting.
        """
        language = locale.getlocale()[0]
        if not language:
            locale.setlocale(locale.LC_ALL, "")
            language = locale.getlocale()[0]
        return language