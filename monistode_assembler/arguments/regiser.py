"""A parser for an immediate argument"""
from __future__ import annotations
from dataclasses import dataclass
import re
from typing import TYPE_CHECKING

from monistode_binutils_shared.relocation import SymbolRelocationParams

if TYPE_CHECKING:
    from monistode_assembler.description import RegisterGroup


@dataclass
class Register:
    """A register"""

    type_name: str
    length_in_chars: int
    value: int
    asint: int
    n_bits: int
    symbols: tuple[SymbolRelocationParams, ...] = ()


class RegisterParser:
    """A parser for a register argument"""

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
        return f"{'|'.join(registers)} register"

    def attempt_scan(self, line: str, offset: int) -> Register | None:
        """Attempt to scan an immediate argument from the line

        Args:
            line (str): The line to parse
            offset (int): The offset to start parsing from

        Returns:
            Immediate | None: The parsed immediate, or None if the line does not
        """
        if offset >= len(line) or line[offset] != "%":
            return None
        offset += 1
        match = re.match(r"[a-zA-Z0-9]+", line[offset:])
        if match is None:
            return None
        register_name = match.group(0)
        register_index = self.group.get_register_index(register_name)
        if register_index is None:
            return None
        return Register(
            type_name=self.type_name,
            length_in_chars=len(register_name) + 1,
            value=register_index,
            asint=register_index,
            n_bits=self.group.length,
        )
