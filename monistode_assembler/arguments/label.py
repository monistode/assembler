"""A parser for a label in the text section"""
from dataclasses import dataclass
import re

from monistode_binutils_shared.relocation import (
    RelocationTargetSymbol,
    SymbolRelocationParams,
)

from .address import AddressParser


@dataclass
class Label:
    """A label in the text section"""

    length_in_chars: int
    n_bits: int
    symbols: tuple[SymbolRelocationParams, ...]
    value: int
    asint: int


class LabelParser:
    """A parser for a label"""

    def __init__(self, n_bits: int, relative: bool = False):
        """Initialize the parser

        Args:
            n_bits (int): The number of bits in the address
            relative (bool, optional): Whether the address is relative to the
                current address. Defaults to False.
        """
        self.n_bits = n_bits
        self.relative = relative

    def attempt_scan(self, line: str, offset: int) -> Label | None:
        """Attempt to scan a label from the line, taking into account the
        absolute and offset directives

        Args:
            line (str): The line to parse
            offset (int): The offset to start parsing from

        Returns:
            Label | None: The parsed label, or None if no label was found
        """
        match = re.match(r"ABSOLUTE\s+", line[offset:])
        if match is not None:
            offset += match.end()
            self.relative = False
        match = re.match(r"OFFSET\s+", line[offset:])
        if match is not None:
            offset += match.end()
            self.relative = True
        return self.attempt_scan_label(line, offset)

    def attempt_scan_label(self, line: str, offset: int) -> Label | None:
        """Attempt to scan a label from the line

        Args:
            line (str): The line to parse
            offset (int): The offset to start parsing from

        Returns:
            Label | None: The parsed label, or None if no label was found
        """
        # detect all ascii followed by either whitespace of a comma
        match = re.match(r"([a-zA-Z_][a-zA-Z0-9_]*)(?:\s|,|$)", line[offset:])
        if match is None:
            return None
        offset, n_offset_chars = self.attempt_scan_offset(line, offset + match.end())
        return Label(
            length_in_chars=match.end() + n_offset_chars,
            n_bits=self.n_bits,
            symbols=(
                SymbolRelocationParams(
                    RelocationTargetSymbol(match.group(1), "text"),
                    size=16,
                    offset=0,
                    relative=self.relative,
                ),
            ),
            value=offset,
            asint=offset,
        )

    def attempt_scan_offset(self, line: str, offset: int) -> tuple[int, int]:
        """Attempt to scan a label's offset

        Args:
            line (str): The line to parse
            offset (int): The offset to start parsing from

        Returns:
            int: The offset of the label and the number of characters parsed
        """
        # First we find a plus literal and all the whitespace after it
        match = re.match(r"^\s*\+\s*", line[offset:])
        if match is None:
            return 0, 0
        # Then we find the address
        address_parser = AddressParser(self.n_bits)
        address = address_parser.attempt_scan(line, offset + match.end())
        if address is None:
            return 0, 0
        return address.asint, match.end() + address.length_in_chars
