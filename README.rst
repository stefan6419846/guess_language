guess_language – Guess the natural language of a text
=====================================================


Example usage
-------------

>>> from guess_language import guess_language
>>> guess_language("Ces eaux regorgent de renégats et de voleurs.")
'fr'
>>> guess_language("Tienes que seguir tu corazón.")
'es'
>>> guess_language("いいえ！忍者がいます")
'ja'
>>> not guess_language("??")
True


If your text is less than 20 characters long,
you need `PyEnchant <http://packages.python.org/pyenchant>`_
and the appropriate dictionaries installed:

>>> guess_language("Hello, World!")
'en'


Installation
------------

To install the package, use::

  $ pip install .

Prerequisites
-------------

- `Python 3.9+ <https://www.python.org>`_
- `PyEnchant <https://pyenchant.github.io/pyenchant/>`_ (optional)
- `lib3to2 <https://bitbucket.org/amentajo/lib3to2>`_

This is a maintained/modern fork of
`guess-language-spirit <https://github.com/hiddenspirit/guess_language>`_,
which itself is a Python 3 version of
`guess-language <http://code.google.com/p/guess-language>`_
with further improvements.
