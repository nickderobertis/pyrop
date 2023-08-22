from typing import TypeVar

from pyrop._either import Either, Right

T = TypeVar("T", covariant=True)

Nothing = Either.left(None)
Some = Right
Option = Either[None, T]
