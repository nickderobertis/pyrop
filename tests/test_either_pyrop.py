import pytest

from pyrop.either import Either, EitherException


def test_either_get():
    assert Either.right(1).get() == 1
    with pytest.raises(EitherException):
        Either.left(None).get()


def test_either_get_or_else():
    assert Either.right(1).get_or_else(2) == 1
    assert Either.left(None).get_or_else(2) == 2


def test_either_or_else():
    assert Either.right(1).or_else(2).get() == 1
    assert Either.left(None).or_else(2).get() == 2


def test_either_either_fold():
    assert (
        Either.right(1)
        .either_fold(lambda e: Either.right(2), lambda a: Either.right(3))
        .get()
        == 3
    )
    assert (
        Either.left(None)
        .either_fold(lambda e: Either.right(2), lambda a: Either.right(3))
        .get()
        == 2
    )
