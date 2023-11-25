"""A generic argument for a command"""

from typing import Protocol, TypeVar


class Argument(Protocol):
    """A candidate for the function argument"""

    length_in_chars: int
    type_name: str


T_co = TypeVar("T_co", bound=Argument, covariant=True)


class ArgumentParser(Protocol[T_co]):
    """A parser for a specific argument type"""

    type_name: str

    def attempt_scan(self, line: str, offset: int) -> T_co | None:
        """Attempt to scan the argument from the line

        Args:
            line (str): The line to scan
            offset (int): The offset to start scanning from
        """
