"""The text section parser of the assembler."""
from dataclasses import dataclass

from monistode_binutils_shared.section.data import Data

from ..arguments.common import ArgumentParser
from ..arguments.string import StringParser
from ..command import Command
from .data_argument import DataArgument


@dataclass
class DataSectionParameters:
    """The parameters of the text section parser."""

    byte: int
    data_address_bits: int


class DataSectionParser:
    """The data section parser of the assembler."""

    section_name = "data"

    def __init__(self, parameters: DataSectionParameters) -> None:
        """Initialize the data section parser."""
        self.parameters = parameters
        self.data = Data(parameters.byte)

        self.signatures: dict[str, tuple[ArgumentParser[DataArgument], ...]] = {
            "ascii": (StringParser(b""),),
            "asciiz": (StringParser(b"\0"),),
        }

    def command_signatures(
        self, command: str
    ) -> tuple[tuple[ArgumentParser, ...], ...]:
        """Get all possible signatures of a command."""
        return (self.signatures.get(command, ()),)

    def add_command(self, command: Command[DataArgument]) -> None:
        """Add a command to the text section."""
        data_bytes = b""
        for argument in command.args:
            data_bytes += argument.asbytes
            for symbol in argument.symbols:
                self.data.add_raw_relocation(symbol)
        for byte in data_bytes:
            self.data.add_byte(byte)

    def add_label(self, label: str) -> None:
        self.data.add_raw_symbol(label)

    def get(self) -> Data:
        """Finish parsing the data section and return the result."""
        return self.data
