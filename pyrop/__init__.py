"""
Imperative-style railway-oriented programming in Python
"""
__version__ = "1.0.0"

from ._catch import Failure, Success, Try, catch  # noqa: F401
from ._either import (  # noqa: F401
    Either,
    EitherException,
    EitherMonad,
    Left,
    Right,
    monadic,
    monadic_method,
)
from ._option import Nothing, Option, Some  # noqa: F401
