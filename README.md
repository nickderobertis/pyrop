

[![](https://codecov.io/gh/nickderobertis/pyrop/branch/main/graph/badge.svg)](https://codecov.io/gh/nickderobertis/pyrop)
[![PyPI](https://img.shields.io/pypi/v/pyrop)](https://pypi.org/project/pyrop/)
![PyPI - License](https://img.shields.io/pypi/l/pyrop)
[![Documentation](https://img.shields.io/badge/documentation-pass-green)](https://nickderobertis.github.io/pyrop/)
![Tests Run on Ubuntu Python Versions](https://img.shields.io/badge/Tests%20Ubuntu%2FPython-3.9%20%7C%203.10-blue)
![Tests Run on Macos Python Versions](https://img.shields.io/badge/Tests%20Macos%2FPython-3.9%20%7C%203.10-blue)
![Tests Run on Windows Python Versions](https://img.shields.io/badge/Tests%20Windows%2FPython-3.9%20%7C%203.10-blue)
[![Github Repo](https://img.shields.io/badge/repo-github-informational)](https://github.com/nickderobertis/pyrop/)


#  pyrop

## Overview

Imperative-style railway-oriented programming in Python, 
including fully-typed errors. Supports sync and async 
functions and methods.

## Getting Started

Install `pyrop`:

```
pip install pyrop
```

A simple example:

```python
from pyrop import monadic, catch, EitherMonad, Left

catcher = catch[ValueError | TypeError]()

@catcher
def func_with_error():
    raise ValueError("This is an error")

@catcher
def success_func() -> int:
    return 1

@monadic
def func(do: EitherMonad[ValueError | TypeError]) -> int:
    value = do << success_func()
    print(f"Value is {value}")
    do << func_with_error()
    print("This will not execute")
    return value


res = func()
assert isinstance(res, Left)
assert isinstance(res.value, ValueError)

try:
    func().get()
except ValueError as e:
    print(f"Caught error: {e}")

assert func().map_left(lambda e: "Error occurred") == Left("Error occurred")
assert func().get_or_else(1) == 1
```

## Links

See the
[documentation here.](
https://nickderobertis.github.io/pyrop/
)

## Development Status

This project is currently in early-stage development. There may be
breaking changes often. While the major version is 0, minor version
upgrades will often have breaking changes.

## Developing

See the [development guide](
https://github.com/nickderobertis/pyrop/blob/main/DEVELOPING.md
) for development details.

## Author

Created by Nick DeRobertis. MIT License.

