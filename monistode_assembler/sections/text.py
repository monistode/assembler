"""The text section parser of the assembler."""
from dataclasses import dataclass
from typing import Protocol

from monistode_binutils_shared.relocation import SymbolRelocationParams
from monistode_binutils_shared.section.text import Text

from ..arguments.common import ArgumentParser
from ..command import Command
from ..exceptions import AssemblyError


class TextArgument(Protocol):
    """A candidate for the text section argument"""

    length_in_chars: int

    @property
    def asint(self) -> int:
        """The argument as a big integer"""

    @property
    def n_bits(self) -> int:
        """The number of bits in the argument"""

    @property
    def symbols(self) -> tuple[SymbolRelocationParams, ...]:
        """The symbols in the argument"""


@dataclass
class CommandDefinition:
    """A single assembly command."""

    mnemonic: str
    opcode: int
    arguments: tuple[ArgumentParser[TextArgument], ...]


@dataclass
class TextSectionParameters:
    """The parameters of the text section parser."""

    byte: int
    opcode_length: int
    text_address_bits: int
    data_address_bits: int


class TextSectionParser:
    """The text section parser of the assembler."""

    section_name = "text"

    def __init__(
        self, parameters: TextSectionParameters, commands: list[CommandDefinition]
    ) -> None:
        """Initialize the text section parser."""
        self.parameters = parameters
        self.commands = commands
        self.text = Text(parameters.byte)

    def command_signatures(
        self, command: str
    ) -> tuple[tuple[ArgumentParser[TextArgument], ...], ...]:
        """Get all possible signatures of a command."""
        return tuple(cmd.arguments for cmd in self.commands if cmd.mnemonic == command)

    def command_opcode(self, command: str) -> int:
        """Get the opcode of a command."""
        return next(cmd.opcode for cmd in self.commands if cmd.mnemonic == command)

    def add_command(self, command: Command[TextArgument]) -> None:
        """Add a command to the text section."""
        command_code: int = self.command_opcode(command.name)
        command_bits: int = self.parameters.opcode_length

        for argument in command.args:
            while command_bits // self.parameters.byte:
                self.text.add_byte(command_code % 2**self.parameters.byte)
                command_code >>= self.parameters.byte
                command_bits -= self.parameters.byte

            bit_offset = command_bits % self.parameters.byte
            for symbol in argument.symbols:
                self.text.add_relocation(
                    SymbolRelocationParams(
                        symbol.target, symbol.offset + bit_offset, symbol.relative
                    )
                )

            command_code <<= argument.n_bits
            command_code |= argument.asint % 2**argument.n_bits
            command_bits += argument.n_bits

        while command_bits // self.parameters.byte:
            self.text.add_byte(command_code % 2**self.parameters.byte)
            command_code >>= self.parameters.byte
            command_bits -= self.parameters.byte

        if command_bits:
            raise AssemblyError(
                f"Command {command.name} has {command_bits} bits left over"
            )

    def add_label(self, label: str) -> None:
        self.text.add_symbol(label)

    def get(self) -> Text:
        """Finish parsing the text section and return the result."""
        return self.text
