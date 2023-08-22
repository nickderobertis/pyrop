from typing import Union

import pytest

from pyrop import Failure, Success, catch


def test_catch_wraps_success():
    @catch[ValueError]()
    def _func() -> int:
        return 1

    assert _func() == Success(1)


@pytest.mark.anyio
async def test_catch_wraps_async_success():
    @catch[ValueError]()
    async def _func() -> int:
        return 1

    assert (await _func()) == Success(1)


def test_catch_multiple_wraps_success():
    @catch[Union[ValueError, NotImplementedError]]()
    def _func() -> int:
        return 1

    assert _func() == Success(1)


def test_catch_wraps_failure():
    error = ValueError("test error")

    @catch[ValueError]()
    def _func() -> int:
        raise error

    assert _func() == Failure(error)


@pytest.mark.anyio
async def test_catch_wraps_async_failure():
    error = ValueError("test error")

    @catch[ValueError]()
    async def _func() -> int:
        raise error

    assert (await _func()) == Failure(error)


def test_catch_multiple_wraps_failure():
    error = ValueError("test error")

    @catch[Union[ValueError, NotImplementedError]]()
    def _func() -> int:
        raise error

    assert _func() == Failure(error)


def test_catch_does_not_catch_other_exceptions():
    error = TypeError("test error")

    @catch[ValueError]()
    def _func() -> int:
        raise error

    with pytest.raises(TypeError):
        _func()


@pytest.mark.anyio
async def test_catch_does_not_catch_other_async_exceptions():
    error = TypeError("test error")

    @catch[ValueError]()
    async def _func() -> int:
        raise error

    with pytest.raises(TypeError):
        await _func()


def test_catch_multiple_does_not_catch_other_exceptions():
    error = TypeError("test error")

    @catch[Union[ValueError, NotImplementedError]]()
    def _func() -> int:
        raise error

    with pytest.raises(TypeError):
        _func()


def test_catch_rejects_non_error_types():
    with pytest.raises(TypeError):

        @catch[None]()
        def _func() -> int:
            raise ValueError("test error")
