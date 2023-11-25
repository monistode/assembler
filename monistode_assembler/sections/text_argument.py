"""The text section argument protocol"""
from typing import Protocol

from monistode_binutils_shared.relocation import SymbolRelocationParams


class TextArgument(Protocol):
    """A candidate for the text section argument"""

    length_in_chars: int
    type_name: str

    @property
    def asint(self) -> int:
        """The argument as a big integer"""

    @property
    def n_bits(self) -> int:
        """The number of bits in the argument"""

    @property
    def symbols(self) -> tuple[SymbolRelocationParams, ...]:
        """The symbols in the argument"""
