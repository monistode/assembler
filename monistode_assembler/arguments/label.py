"""A parser for an immediate argument"""
from dataclasses import dataclass
import re

from monistode_binutils_shared.relocation import (
    RelocationTargetSymbol,
    SymbolRelocationParams,
)


@dataclass
class Label:
    """An immediate argument"""

    length_in_chars: int
    n_bits: int
    symbols: tuple[SymbolRelocationParams, ...]
    value: int = 0
    asint: int = 0


class LabelParser:
    """A parser for an immediate argument"""

    def __init__(self, n_bits: int, relative: bool = False):
        """Initialize the parser

        Args:
            n_bits (int): The number of bits in the immediate
            relative (bool, optional): Whether the immediate is relative to the
        """
        self.n_bits = n_bits
        self.relative = relative

    def attempt_scan(self, line: str, offset: int) -> Label | None:
        """Attempt to scan an immediate argument from the line

        Args:
            line (str): The line to parse
            offset (int): The offset to start parsing from

        Returns:
            Immediate | None: The parsed immediate, or None if the line does not
        """
        # detect all ascii followed by either whitespace of a comma
        match = re.match(r"([a-zA-Z_][a-zA-Z0-9_]*)(?:\s|,|$)", line[offset:])
        if match is None:
            return None
        return Label(
            length_in_chars=match.end(),
            n_bits=self.n_bits,
            symbols=(
                SymbolRelocationParams(
                    RelocationTargetSymbol(match.group(1), "text"), 0, self.relative
                ),
            ),
        )
