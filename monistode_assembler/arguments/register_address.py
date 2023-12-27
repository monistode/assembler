"""A parser for am addressation by register in the text section"""
from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING

from monistode_binutils_shared.relocation import SymbolRelocationParams

from .regiser import RegisterParser

if TYPE_CHECKING:
    from monistode_assembler.description import RegisterGroup


@dataclass
class RegisterAddress:
    """An addressation by register"""

    type_name: str
    length_in_chars: int
    value: int
    asint: int
    n_bits: int
    symbols: tuple[SymbolRelocationParams, ...] = ()


class RegisterAddressParser:
    """A parser for an addressation by register"""

    def __init__(self, group: RegisterGroup) -> None:
        """Initialize the parser

        Args:
            group (RegisterGroup): The register group to parse from
        """
        self.group = group

    @property
    def type_name(self) -> str:
        registers = sorted(
            self.group.registers
            if isinstance(self.group.registers, list)
            else list(self.group.registers.keys())
        )
        return f"{'|'.join(registers)} register_address"

    def attempt_scan(self, line: str, offset: int) -> RegisterAddress | None:
        """Attempt to scan a register address from the line

        Args:
            line (str): The line to parse
            offset (int): The offset to start parsing from

        Returns:
            RegisterAddress | None: The parsed addressation, or None if no label was found
        """
        if offset >= len(line) or line[offset] != "[":
            return None
        register = RegisterParser(self.group).attempt_scan(line, offset + 1)
        if register is None:
            return None
        if register.length_in_chars + 1 + offset >= len(line):
            return None
        if line[register.length_in_chars + 1 + offset] != "]":
            return None
        return RegisterAddress(
            self.type_name,
            register.length_in_chars + 2,
            register.value,
            register.asint,
            register.n_bits,
            register.symbols,
        )
