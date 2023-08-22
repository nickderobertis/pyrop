"""
Imperative-style railway-oriented programming in Python
"""
__version__ = "1.0.0"

from .catch import Failure, Success, Try, catch  # noqa: F401
from .either import (  # noqa: F401
    Either,
    EitherException,
    EitherMonad,
    Left,
    Right,
    monadic,
    monadic_method,
)
from .option import Nothing, Option, Some  # noqa: F401
