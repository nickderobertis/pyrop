import pytest

from pyrop import EitherMonad, Left, Right, monadic, monadic_method


def test_monadic_wraps_success():
    @monadic
    def _func(do) -> int:
        return 1

    assert _func() == Right(1)


@pytest.mark.anyio
async def test_monadic_wraps_async_success():
    @monadic
    async def _func(do) -> int:
        return 1

    assert await _func() == Right(1)


def test_monadic_method_wraps_success():
    class TestClass:
        @monadic_method
        def _func(self, do) -> int:
            return 1

    assert TestClass()._func() == Right(1)


@pytest.mark.anyio
async def test_monadic_method_wraps_async_success():
    class TestClass:
        @monadic_method
        async def _func(self, do) -> int:
            return 1

    assert (await TestClass()._func()) == Right(1)


def test_monadic_wraps_failure():
    error = ValueError("test error")

    @monadic
    def _func(do) -> int:
        raise error

    assert _func() == Left(error)


@pytest.mark.anyio
async def test_monadic_wraps_async_failure():
    error = ValueError("test error")

    @monadic
    async def _func(do) -> int:
        raise error

    assert (await _func()) == Left(error)


def test_monadic_method_wraps_failure():
    error = ValueError("test error")

    class TestClass:
        @monadic_method
        def _func(self, do) -> int:
            raise error

    assert TestClass()._func() == Left(error)


@pytest.mark.anyio
async def test_monadic_method_wraps_async_failure():
    error = ValueError("test error")

    class TestClass:
        @monadic_method
        async def _func(self, do) -> int:
            raise error

    assert (await TestClass()._func()) == Left(error)


def test_monadic_do_statement_success():
    @monadic
    def _func(do: EitherMonad) -> int:
        x = do << Right(1)
        return x + 1

    assert _func() == Right(2)


@pytest.mark.anyio
async def test_monadic_do_statement_async_success():
    @monadic
    async def _func(do: EitherMonad) -> int:
        x = do << Right(1)
        return x + 1

    assert (await _func()) == Right(2)


def test_monadic_method_do_statement_success():
    class TestClass:
        @monadic_method
        def _func(self, do: EitherMonad) -> int:
            x = do << Right(1)
            return x + 1

    assert TestClass()._func() == Right(2)


@pytest.mark.anyio
async def test_monadic_method_do_statement_async_success():
    class TestClass:
        @monadic_method
        async def _func(self, do: EitherMonad) -> int:
            x = do << Right(1)
            return x + 1

    assert (await TestClass()._func()) == Right(2)


def test_monadic_do_statement_failure():
    error = ValueError("test error")
    should_not_change = "something"

    @monadic
    def _func(do: EitherMonad[ValueError]) -> int:
        nonlocal should_not_change

        x = do << Left(error)

        # Should not be executed
        should_not_change = "something else"
        return x + 1

    assert _func() == Left(error)
    assert should_not_change == "something"


@pytest.mark.anyio
async def test_monadic_do_statement_async_failure():
    error = ValueError("test error")
    should_not_change = "something"

    @monadic
    async def _func(do: EitherMonad[ValueError]) -> int:
        nonlocal should_not_change

        x = do << Left(error)

        # Should not be executed
        should_not_change = "something else"
        return x + 1

    assert (await _func()) == Left(error)
    assert should_not_change == "something"


def test_monadic_method_do_statement_failure():
    error = ValueError("test error")
    should_not_change = "something"

    class TestClass:
        @monadic_method
        def _func(self, do: EitherMonad[ValueError]) -> int:
            nonlocal should_not_change

            x = do << Left(error)

            # Should not be executed
            should_not_change = "something else"
            return x + 1

    assert TestClass()._func() == Left(error)
    assert should_not_change == "something"


@pytest.mark.anyio
async def test_monadic_method_do_statement_async_failure():
    error = ValueError("test error")
    should_not_change = "something"

    class TestClass:
        @monadic_method
        async def _func(self, do: EitherMonad[ValueError]) -> int:
            nonlocal should_not_change

            x = do << Left(error)

            # Should not be executed
            should_not_change = "something else"
            return x + 1

    assert (await TestClass()._func()) == Left(error)
    assert should_not_change == "something"
