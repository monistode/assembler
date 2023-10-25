"""A parser for an immediate argument"""
from dataclasses import dataclass
import re

from monistode_binutils_shared.relocation import SymbolRelocationParams

from ..exceptions import ParserError


@dataclass
class Address:
    """An immediate argument"""

    length_in_chars: int
    value: int
    asint: int
    n_bits: int
    symbols: tuple[SymbolRelocationParams, ...] = ()


class AddressParser:
    """A parser for an immediate argument"""

    def __init__(self, n_bits: int) -> None:
        """Initialize the parser

        Args:
            n_bits (int): The number of bits in the immediate
        """
        self.n_bits = n_bits

    def attempt_scan(self, line: str, offset: int) -> Address | None:
        """Attempt to scan an immediate argument from the line

        Args:
            line (str): The line to parse
            offset (int): The offset to start parsing from

        Returns:
            Immediate | None: The parsed immediate, or None if the line does not
        """
        length = self._attempt_scan_decimal(line, offset)
        if length is not None:
            return self._parse(line, offset, length)
        length = self._attempt_scan_hexadecimal(line, offset)
        if length is not None:
            return self._parse(line, offset, length)
        length = self._attempt_scan_binary(line, offset)
        if length is not None:
            return self._parse(line, offset, length)
        return None

    def _attempt_scan_decimal(self, line: str, offset: int) -> int | None:
        """Attempt to scan a decimal immediate from the line

        Args:
            line (str): The line to parse
            offset (int): The offset to start parsing from

        Returns:
            int | None: The length of the immediate in characters, or None if the
                line does not contain a decimal immediate
        """
        result = re.match(r"\d+", line[offset:])
        if result is None:
            return None
        return result.end()

    def _attempt_scan_hexadecimal(self, line: str, offset: int) -> int | None:
        """Attempt to scan a hexadecimal immediate from the line

        Args:
            line (str): The line to parse
            offset (int): The offset to start parsing from

        Returns:
            int | None: The length of the immediate in characters, or None if the
                line does not contain a hexadecimal immediate
        """
        result = re.match(r"0x[\da-fA-F]+", line[offset:])
        if result is None:
            return None
        return result.end()

    def _attempt_scan_binary(self, line: str, offset: int) -> int | None:
        """Attempt to scan a binary immediate from the line

        Args:
            line (str): The line to parse
            offset (int): The offset to start parsing from

        Returns:
            int | None: The length of the immediate in characters, or None if the
                line does not contain a binary immediate
        """
        result = re.match(r"0b[01]+", line[offset:])
        if result is None:
            return None
        return result.end()

    def _parse(self, line: str, offset: int, length: int) -> Address:
        """Parse an address from the line

        Args:
            line (str): The line to parse
            offset (int): The offset to start parsing from
            length (int): The length of the immediate in characters

        Returns:
            Address: The parsed immediate
        """
        value = int(line[offset : offset + length], base=0)
        if value >= 2**self.n_bits:
            raise ParserError(
                f"Immediate value {value} is too large for {self.n_bits}-bit immediate"
            )
        if value < 0:
            raise ParserError(
                f"Immediate value {value} is too small for {self.n_bits}-bit immediate"
            )
        return Address(
            length_in_chars=length + 1,
            value=value,
            asint=value,
            n_bits=self.n_bits,
        )