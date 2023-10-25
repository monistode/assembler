"""A command in an assembly source file."""
from dataclasses import dataclass
from typing import Generic, TypeVar

from .arguments import Argument


T = TypeVar("T", bound=Argument, covariant=True)


@dataclass
class Command(Generic[T]):
    """A command in an assembly source file."""

    name: str
    args: tuple[T, ...]
