"""A parser for just padding (for nothing)."""
from dataclasses import dataclass

from monistode_binutils_shared.relocation import SymbolRelocationParams


@dataclass
class Padding:
    """A padding pseudo-argument"""

    n_bits: int
    length_in_chars: int = 0
    asint: int = 0
    symbols: tuple[SymbolRelocationParams, ...] = ()


class PaddingParser:
    """A parser for a padding pseudo-argument"""

    def __init__(self, n_bits: int) -> None:
        """Initialize the parser

        Args:
            n_bits (int): The number of bits in the immediate
        """
        self.n_bits = n_bits

    def attempt_scan(self, line: str, offset: int) -> Padding | None:
        """Attempt to scan an immediate argument from the line

        Args:
            line (str): The line to parse
            offset (int): The offset to start parsing from

        Returns:
            Immediate | None: The parsed immediate, or None if the line does not
        """
        return Padding(self.n_bits)
