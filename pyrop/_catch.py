import inspect
import types
from functools import cached_property, wraps
from typing import (
    Awaitable,
    Callable,
    Generic,
    TypeVar,
    Union,
    cast,
    get_args,
    overload,
)

from typing_extensions import ParamSpec

from pyrop._either import Either, Left, Right

_OldUnionType = type(Union[int, str])

UnionTypes: tuple[type, ...]
try:
    # Python 3.10+
    UnionTypes = (types.UnionType, _OldUnionType)  # type: ignore[attr-defined]
except AttributeError:
    # Python 3.9
    UnionTypes = (_OldUnionType,)

E = TypeVar("E", bound=BaseException)
T = TypeVar("T")
R = TypeVar("R", covariant=True)
P = ParamSpec("P")

Failure = Left
Success = Right
Try = Either[E, R]


class catch(Generic[T]):
    @cached_property
    def _exception_type(self) -> T:
        return get_args(self.__orig_class__)[0]  # type: ignore[attr-defined]

    def _create_exceptions(self) -> tuple[type[BaseException], ...]:
        if isinstance(self._exception_type, UnionTypes):
            exceptions = get_args(self._exception_type)
        elif issubclass(self._exception_type, BaseException):  # type: ignore[arg-type]
            exceptions = (self._exception_type,)
        else:
            raise TypeError(f"Expected an exception type, got {self._exception_type}.")
        return exceptions

    @overload
    def __call__(  # type: ignore[misc]
        self, func: Callable[P, Awaitable[R]]
    ) -> Callable[P, Awaitable[Either[T, R]]]:
        ...

    @overload
    def __call__(self, func: Callable[P, R]) -> Callable[P, Either[T, R]]:
        ...

    def __call__(
        self, func: Union[Callable[P, R], Callable[P, Awaitable[R]]]
    ) -> Union[Callable[P, Either[T, R]], Callable[P, Awaitable[Either[T, R]]]]:
        exceptions = self._create_exceptions()

        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> Either[T, R]:
            try:
                result = cast(R, func(*args, **kwargs))
                return Success(result)
            except exceptions as e:
                return Failure(cast(T, e))

        if not inspect.iscoroutinefunction(func):
            return wrapper

        @wraps(func)
        async def wrapper_async(*args: P.args, **kwargs: P.kwargs) -> Either[T, R]:
            try:
                return Success(await func(*args, **kwargs))
            except exceptions as e:
                return Failure(cast(T, e))

        return wrapper_async
