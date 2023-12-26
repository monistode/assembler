"""A parser for an addressation by register with an offset in the text section"""
from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING

from monistode_binutils_shared.relocation import SymbolRelocationParams

from .register_offset import RegisterOffsetParser

if TYPE_CHECKING:
    from monistode_assembler.description import RegisterGroup


@dataclass
class RegisterAddressOffset:
    """An addressation by register with an offset"""

    type_name = "register_address_offset"

    length_in_chars: int
    address: int
    register: int
    asint: int
    n_bits: int
    symbols: tuple[SymbolRelocationParams, ...] = ()


class RegisterAddressOffsetParser:
    """A parser for an addressation by register with an offset"""

    type_name = "register_address_offset"

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

    def attempt_scan(self, line: str, offset: int) -> RegisterAddressOffset | None:
        """Attempt to scan a register address from the line

        Args:
            line (str): The line to parse
            offset (int): The offset to start parsing from

        Returns:
            RegisterAddressOffset | None: The parsed addressation, or None if no label was found
        """
        if offset >= len(line) or line[offset] != "[":
            return None
        offset += 1

        register_address_offset = RegisterOffsetParser(
            self.group, self.padding_bits, self.offset_bits, self.relative
        ).attempt_scan(line, offset)
        if register_address_offset is None:
            return None
        offset += register_address_offset.length_in_chars

        if offset >= len(line):
            return None
        if line[offset] != "]":
            return None

        return RegisterAddressOffset(
            register_address_offset.length_in_chars + 2,
            register_address_offset.address,
            register_address_offset.register,
            register_address_offset.asint,
            register_address_offset.n_bits,
            register_address_offset.symbols,
        )
