import pytest

# Skip this module on Python < 3.10
try:
    eval("from typing import ParamSpec")
except SyntaxError:
    pytest.skip(allow_module_level=True, reason="These tests only run on Python 3.10+")

from pyrop import Failure, Success, catch


def test_catch_multiple_wraps_success():
    @catch[ValueError | NotImplementedError]()
    def _func() -> int:
        return 1

    assert _func() == Success(1)


def test_catch_multiple_wraps_failure():
    error = ValueError("test error")

    @catch[ValueError | NotImplementedError]()
    def _func() -> int:
        raise error

    assert _func() == Failure(error)


def test_catch_multiple_does_not_catch_other_exceptions():
    error = TypeError("test error")

    @catch[ValueError | NotImplementedError]()
    def _func() -> int:
        raise error

    with pytest.raises(TypeError):
        _func()
