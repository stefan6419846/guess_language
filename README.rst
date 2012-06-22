guess_language – Guess the natural language of a text
=====================================================


Example usage
-------------

>>> from guess_language import guess_language
>>> guess_language("I’ve been feeling déjà vu all morning.")
'en'
>>> guess_language("Tienes que seguir tu corazón.")
'es'
>>> guess_language("いいえ！忍者がいます")
'ja'


This is basically my branch of `guess-language
<http://code.google.com/p/guess-language>`_, ported to Python 3
and optimized for my own needs. Speed has been much improved.
