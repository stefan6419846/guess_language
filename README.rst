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


Installation
------------

You can use `pip <http://www.pip-installer.org>`_ to install or uninstall::

  $ pip install guess_language-spirit

On Windows, you can use one of the MSI binary packages provided
on the `download page
<https://bitbucket.org/spirit/guess_language/downloads>`_.


Requirements
------------

- `Python 3.2+ <http://www.python.org>`_
  (or 2.7, using `lib3to2 <https://bitbucket.org/amentajo/lib3to2>`_)


This is basically my branch of `guess-language
<http://code.google.com/p/guess-language>`_, ported to Python 3
and optimized for my own needs. Speed has been much improved.
