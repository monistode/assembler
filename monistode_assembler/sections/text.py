"""The text section parser of the assembler."""
from dataclasses import dataclass

from monistode_binutils_shared.relocation import SymbolRelocationParams
from monistode_binutils_shared.section.text import Text

from ..arguments.common import ArgumentParser
from ..command import Command
from ..exceptions import AssemblyError
from .text_argument import TextArgument


@dataclass
class CommandDefinition:
    """A single assembly command."""

    mnemonic: str
    opcode: int
    arguments: tuple[ArgumentParser[TextArgument], ...]
    pre_opcode_arguments: int


@dataclass
class TextSectionParameters:
    """The parameters of the text section parser."""

    byte: int
    opcode_length: int
    opcode_offset: int
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

    def configuration_command(self, command: str) -> CommandDefinition:
        """Get the configuration of a command."""
        return next(cmd for cmd in self.commands if cmd.mnemonic == command)

    def add_command(self, command: Command[TextArgument]) -> None:
        """Add a command to the text section."""
        configuration_command = self.configuration_command(command.name)
        n_pre_opcode_arguments = configuration_command.pre_opcode_arguments
        command_code: int = 0
        command_bits: int = 0

        if n_pre_opcode_arguments == 0:
            command_code = configuration_command.opcode
            command_bits = self.parameters.opcode_length

        for i, argument in enumerate(command.args):
            while command_bits >= self.parameters.byte:
                offset = (
                    command_bits % self.parameters.byte
                    + command_bits // self.parameters.byte * self.parameters.byte
                    - self.parameters.byte
                )
                extracted_byte = command_code >> offset
                self.text.add_byte(extracted_byte)
                command_code -= extracted_byte << offset
                command_bits -= self.parameters.byte

            bit_offset = command_bits % self.parameters.byte
            for symbol in argument.symbols:
                self.text.add_raw_relocation(
                    SymbolRelocationParams(
                        symbol.target, symbol.offset + bit_offset, symbol.relative
                    )
                )

            command_code <<= argument.n_bits
            command_code |= argument.asint % 2**argument.n_bits
            command_bits += argument.n_bits

            if i == n_pre_opcode_arguments - 1:
                command_code <<= self.parameters.opcode_length
                command_code |= configuration_command.opcode
                command_bits += self.parameters.opcode_length

        while command_bits >= self.parameters.byte:
            offset = (
                command_bits % self.parameters.byte
                + command_bits // self.parameters.byte * self.parameters.byte
                - self.parameters.byte
            )
            extracted_byte = command_code >> offset
            self.text.add_byte(extracted_byte)
            command_code -= extracted_byte << offset
            command_bits -= self.parameters.byte

        if command_bits:
            raise AssemblyError(
                f"Command {command.name} has {command_bits} bits left over"
            )

    def add_label(self, label: str) -> None:
        self.text.add_raw_symbol(label)

    def get(self) -> Text:
        """Finish parsing the text section and return the result."""
        return self.text
