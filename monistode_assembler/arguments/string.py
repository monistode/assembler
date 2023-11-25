"""The text section argument protocol"""
from dataclasses import dataclass
import json

from monistode_binutils_shared.relocation import SymbolRelocationParams


@dataclass
class String:
    """A candidate for the data section argument"""

    type_name = "string"

    raw_string: str
    termination: bytes

    @property
    def length_in_chars(self) -> int:
        return len(self.raw_string)

    @property
    def asbytes(self) -> bytes:
        """The argument as bytes"""
        return (json.loads(self.raw_string) + self.termination).encode("utf-8")

    @property
    def symbols(self) -> tuple[SymbolRelocationParams, ...]:
        """The symbols in the argument"""
        return ()


class StringParser:
    """A parser for a specific argument type"""

    type_name = "string"

    def __init__(self, termination: bytes) -> None:
        self.termination = termination

    def attempt_scan(self, line: str, offset: int) -> String | None:
        """Attempt to scan the argument from the line

        Args:
            line (str): The line to scan
            offset (int): The offset to start scanning from
        """
        if line[offset] != '"':
            return None
        end = offset + 1
        while end < len(line):
            if line[end] == '"':
                break
            if line[end] == "\\":
                end += 1
            end += 1
        if end == len(line):
            return None
        return String(line[offset : end + 1], self.termination)
