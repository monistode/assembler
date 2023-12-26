"""A parser for a register with an offset in the text section"""
from __future__ import annotations
from dataclasses import dataclass
import re
from typing import TYPE_CHECKING

from monistode_binutils_shared.relocation import SymbolRelocationParams

from .address import Address, AddressParser
from .label import Label, LabelParser
from .regiser import RegisterParser

if TYPE_CHECKING:
    from monistode_assembler.description import RegisterGroup


@dataclass
class RegisterOffset:
    """An register with an offset"""

    type_name = "register_offset"

    length_in_chars: int
    address: int
    register: int
    asint: int
    n_bits: int
    symbols: tuple[SymbolRelocationParams, ...] = ()


class RegisterOffsetParser:
    """A parser for a register with an offset"""

    type_name = "register_offset"

    def __init__(
        self, group: RegisterGroup, padding_bits: int, offset_bits: int, relative: bool
    ) -> None:
        """Initialize the parser

        Args:
            group (RegisterGroup): The register group to parse from
            padding_bits (int): The number of bits to pad the offset with
            offset_bits (int): The number of bits to use for the offset
            relative (bool): Whether the offset is absolute or relative
        """
        self.group = group
        self.padding_bits = padding_bits
        self.offset_bits = offset_bits
        self.relative = relative

    def attempt_scan(self, line: str, offset: int) -> RegisterOffset | None:
        """Attempt to scan a register address from the line

        Args:
            line (str): The line to parse
            offset (int): The offset to start parsing from

        Returns:
            RegisterAddressOffset | None: The parsed addressation, or None if no label was found
        """
        register = RegisterParser(self.group).attempt_scan(line, offset)
        if register is None:
            return None
        offset += register.length_in_chars

        plus_sign_len = self._scan_plus_sign(line, offset)
        if plus_sign_len is None:
            return None
        offset += plus_sign_len

        address: Address | Label | None = LabelParser(
            self.offset_bits, self.relative
        ).attempt_scan(line, offset)
        if address is None:
            address = AddressParser(self.offset_bits).attempt_scan(line, offset)
        if address is None:
            return None
        offset += address.length_in_chars

        return RegisterOffset(
            register.length_in_chars + plus_sign_len + address.length_in_chars,
            address.asint,
            register.asint,
            register.asint << (self.padding_bits + self.offset_bits) | address.asint,
            self.padding_bits + self.offset_bits + register.n_bits,
            tuple(
                SymbolRelocationParams(
                    symbol.target,
                    symbol.size,
                    symbol.offset + self.padding_bits + register.n_bits,
                    symbol.relative,
                )
                for symbol in address.symbols
            ),
        )

    def _scan_plus_sign(self, line: str, offset: int) -> int | None:
        """Scan a plus sign from the line

        Args:
            line (str): The line to parse
            offset (int): The offset to start parsing from

        Returns:
            int | None: The offset after the plus sign, or None if no plus sign was found
        """
        match = re.match(r"\s*\+\s*", line[offset:])
        if match is None:
            return None
        return match.end()
