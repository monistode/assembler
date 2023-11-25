"""A parser for just padding (for nothing)."""
from dataclasses import dataclass

from monistode_binutils_shared.relocation import SymbolRelocationParams


@dataclass
class Padding:
    """A padding pseudo-argument"""

    type_name = "padding"

    n_bits: int
    length_in_chars: int = 0
    asint: int = 0
    symbols: tuple[SymbolRelocationParams, ...] = ()


class PaddingParser:
    """A parser for a padding pseudo-argument"""

    type_name = "padding"

    def __init__(self, n_bits: int) -> None:
        """Initialize the parser

        Args:
            n_bits (int): The number of bits in the padding
        """
        self.n_bits = n_bits

    def attempt_scan(self, line: str, offset: int) -> Padding | None:
        """Attempt to scan a padding argument from the line

        Args:
            line (str): The line to parse
            offset (int): The offset to start parsing from

        Returns:
            Padding | None: The parsed padding, or None if the line does not
                contain a padding
        """
        return Padding(self.n_bits)
