import functools
import inspect
from abc import ABCMeta
from dataclasses import dataclass
from typing import (
    Any,
    Awaitable,
    Callable,
    Generic,
    NoReturn,
    Optional,
    Type,
    TypeVar,
    Union,
    cast,
    overload,
)

from typing_extensions import Concatenate, ParamSpec

A = TypeVar("A", covariant=True)
AV = TypeVar("AV", covariant=True)
AV2 = TypeVar("AV2", covariant=True)
AA = TypeVar("AA")

B = TypeVar("B", covariant=True)
BV = TypeVar("BV", covariant=True)
BV2 = TypeVar("BV2", covariant=True)
BB = TypeVar("BB")

C = TypeVar("C")
D = TypeVar("D")

E = TypeVar("E", covariant=True)
E_con = TypeVar("E_con", contravariant=True)

X = TypeVar("X", bound=BaseException)
P = ParamSpec("P")


@dataclass(frozen=True)
class EitherException(Generic[A], Exception):
    value: A
    message: str = ""

    def __str__(self) -> str:
        return self.message or str(self.value)


class Either(Generic[A, B], metaclass=ABCMeta):
    """Right-biased disjunction"""

    # New methods

    def get(self: "Either[AA, BB]") -> BB:
        return self.fold(lambda e: raise_exception_like(e), lambda a: a)

    def get_or_else(self: "Either[AA, BB]", default: C) -> Union[BB, C]:
        return self.fold(lambda e: default, lambda a: a)

    def or_else(self: "Either[AA, BB]", default: C) -> "Either[C, BB]":
        return self.fold(
            lambda e: Either.right(default),  # type: ignore[arg-type]
            lambda a: Either.right(a),
        )

    def either_fold(
        self,
        case_left: "Callable[[A], Either[AV, BV]]",
        case_right: "Callable[[B], Either[AV2, BV2]]",
    ) -> "Either[Union[AV, AV2], Union[BV, BV2]]":
        return self.match(lambda x: case_left(x.value), lambda y: case_right(y.value))

    # Below are methods from ziopy

    @staticmethod
    def left(value: C) -> "Either[C, NoReturn]":
        return Left(value)

    @staticmethod
    def right(value: C) -> "Either[NoReturn, C]":
        return Right(value)

    @staticmethod
    def from_union(
        value: Union[C, D], left_type: Type[C], right_type: Type[D]
    ) -> "Either[C, D]":
        if isinstance(value, left_type):
            return Either.left(value)
        elif isinstance(value, right_type):
            return Either.right(value)
        else:
            raise TypeError()

    @staticmethod
    def from_optional(value: Optional[C]) -> "Either[None, C]":
        if value is None:
            return Either.left(value)
        return Either.right(value)

    def to_left(self) -> "Left[A]":
        if not isinstance(self, Left):
            raise TypeError("to_left can only be called on an instance of Left.")
        return self

    def to_right(self) -> "Right[B]":
        if not isinstance(self, Right):
            raise TypeError("to_right can only be called on an instance of Right.")
        return self

    def match(
        self,
        case_left: "Callable[[Left[A]], C]",
        case_right: "Callable[[Right[B]], D]",
    ) -> Union[C, D]:
        if isinstance(self, Left):
            return case_left(self)
        elif isinstance(self, Right):
            return case_right(self)
        else:
            raise TypeError()

    def fold(
        self, case_left: "Callable[[A], C]", case_right: "Callable[[B], D]"
    ) -> Union[C, D]:
        return self.match(lambda x: case_left(x.value), lambda y: case_right(y.value))

    def swap(self) -> "Either[B, A]":
        return self.match(
            lambda left: Either.right(left.value),
            lambda right: Either.left(right.value),
        )

    def map(self, f: Callable[[B], C]) -> "Either[A, C]":
        return self.match(lambda left: left, lambda right: Either.right(f(right.value)))

    def map_left(self, f: Callable[[A], C]) -> "Either[C, B]":
        return self.match(lambda left: Either.left(f(left.value)), lambda right: right)

    def flat_map(self, f: "Callable[[B], Either[C, D]]") -> "Either[Union[A, C], D]":
        return self.match(lambda left: left, lambda right: f(right.value))

    def __lshift__(self, f: "Callable[[B], Either[C, D]]") -> "Either[Union[A, C], D]":
        return self.flat_map(f)

    def flatten(self: "Either[A, Either[C, D]]") -> "Either[Union[A, C], D]":
        return self.flat_map(lambda x: x)

    def require(
        self, predicate: Callable[[B], bool], to_error: Callable[[B], C]
    ) -> "Either[Union[A, C], B]":
        def _case_right(right: Right[B]) -> "Either[Union[A, C], B]":
            if predicate(right.value):
                return right
            return Either.left(to_error(right.value))

        return self.match(lambda left: left, _case_right)

    def asserting(
        self, predicate: Callable[[B], bool], to_error: Callable[[B], X]
    ) -> "Either[A, B]":
        def _case_right(right: Right[B]) -> "Either[A, B]":
            if not predicate(right.value):
                raise to_error(right.value)
            return right

        return self.match(lambda left: left, _case_right)

    def raise_errors(self: "Either[AA, BB]") -> "Either[NoReturn, BB]":
        def _case_left(error) -> NoReturn:
            if isinstance(error, Exception):
                raise error from error
            else:
                raise EitherException(value=error)

        return self.fold(_case_left, lambda x: Either.right(x))

    def tap(self, op: "Callable[[Either[A, B]], Any]") -> "Either[A, B]":
        op(self)
        return self

    def display(self, description: Optional[str] = None) -> "Either[A, B]":
        if description is not None:
            print(f"{description}:")
        return self.tap(print)

    def to_union(self) -> Union[A, B]:
        return self.match(lambda x: x.value, lambda y: y.value)

    def cast(self: "Either[AA, BB]", t: Type[C]) -> "Either[Union[AA, TypeError], C]":
        return self.flat_map(
            lambda b: Either.right(b)
            if isinstance(b, t)
            else Either.left(
                TypeError(
                    f"Unable to cast value {b} (of type {type(b).__name__}) as type {t.__name__}."
                )
            )
        )


@dataclass(frozen=True)
class Left(Generic[A], Either[A, NoReturn]):
    value: A


@dataclass(frozen=True)
class Right(Generic[B], Either[NoReturn, B]):
    value: B


def raise_exception_like(x: Any) -> NoReturn:
    if isinstance(x, BaseException):
        raise x
    elif x is None:
        raise EitherException(value=None, message=f"Expected Some, got None.")
    else:
        raise RuntimeError(str(x))


class EitherMonad(Generic[E_con]):
    def __lshift__(self, arg: Either[E_con, BB]) -> BB:
        return arg.fold(lambda e: raise_exception_like(e), lambda a: a)


@overload
def monadic_method(  # type: ignore[misc]
    func: Callable[Concatenate[AA, EitherMonad[E], P], Awaitable[A]]
) -> Callable[Concatenate[AA, P], Awaitable[Either[E, A]]]:
    ...


@overload
def monadic_method(
    func: Callable[Concatenate[AA, EitherMonad[E], P], A]
) -> Callable[Concatenate[AA, P], Either[E, A]]:
    ...


def monadic_method(
    func: Union[
        Callable[Concatenate[AA, EitherMonad[E], P], A],
        Callable[Concatenate[AA, EitherMonad[E], P], Awaitable[A]],
    ]
) -> Union[
    Callable[Concatenate[AA, P], Either[E, A]],
    Callable[Concatenate[AA, P], Awaitable[Either[E, A]]],
]:
    @functools.wraps(func)
    def _wrapper(self_arg: AA, *args: P.args, **kwargs: P.kwargs) -> Either[E, A]:
        try:
            result = cast(A, func(self_arg, EitherMonad(), *args, **kwargs))
            return Either.right(result)
        except Exception as e:
            return Either.left(cast(E, e))

    if not inspect.iscoroutinefunction(func):
        return _wrapper

    @functools.wraps(func)
    async def _wrapper_async(
        self_arg: AA, *args: P.args, **kwargs: P.kwargs
    ) -> Either[E, A]:
        try:
            return Either.right(await func(self_arg, EitherMonad(), *args, **kwargs))
        except Exception as e:
            return Either.left(cast(E, e))

    return _wrapper_async


@overload
def monadic(  # type: ignore[misc]
    func: Callable[Concatenate[EitherMonad[E], P], Awaitable[A]]
) -> Callable[P, Awaitable[Either[E, A]]]:
    ...


@overload
def monadic(
    func: Callable[Concatenate[EitherMonad[E], P], A]
) -> Callable[P, Either[E, A]]:
    ...


def monadic(  # type: ignore[misc]
    func: Union[
        Callable[Concatenate[EitherMonad[E], P], A],
        Callable[Concatenate[EitherMonad[E], P], Awaitable[A]],
    ]
) -> Union[Callable[P, Either[E, A]], Callable[P, Awaitable[Either[E, A]]]]:
    @functools.wraps(func)
    def _wrapper(*args: P.args, **kwargs: P.kwargs) -> Either[E, A]:
        try:
            result = cast(A, func(EitherMonad(), *args, **kwargs))
            return Either.right(result)
        except Exception as e:
            return Either.left(cast(E, e))

    if not inspect.iscoroutinefunction(func):
        return _wrapper

    @functools.wraps(func)
    async def _wrapper_async(*args: P.args, **kwargs: P.kwargs) -> Either[E, A]:
        try:
            return Either.right(await func(EitherMonad(), *args, **kwargs))
        except Exception as e:
            return Either.left(cast(E, e))

    return _wrapper_async
