"""The text section argument protocol"""
from typing import Protocol

from monistode_binutils_shared.relocation import SymbolRelocationParams


class DataArgument(Protocol):
    """A candidate for the data section argument"""

    length_in_chars: int

    @property
    def asbytes(self) -> bytes:
        """The argument as bytes"""

    @property
    def symbols(self) -> tuple[SymbolRelocationParams, ...]:
        """The symbols in the argument"""
