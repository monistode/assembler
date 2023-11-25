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

    def configuration_command(
        self, command: str, arguments: tuple[TextArgument, ...]
    ) -> CommandDefinition:
        """Get the configuration of a command."""
        return next(
            cmd
            for cmd in self.commands
            if cmd.mnemonic == command
            and len(cmd.arguments) == len(arguments)
            and all(
                argument.type_name == argument_parser.type_name
                for argument, argument_parser in zip(arguments, cmd.arguments)
            )
        )

    def add_command(self, command: Command[TextArgument]) -> None:
        """Add a command to the text section."""
        configuration_command = self.configuration_command(command.name, command.args)
        n_pre_opcode_arguments = configuration_command.pre_opcode_arguments
        command_code: int = 0
        command_bits: int = 0

        if n_pre_opcode_arguments == 0:
            command_code = configuration_command.opcode
            command_bits = self.parameters.opcode_length

        command_bytes = (
            sum(argument.n_bits for argument in command.args)
            + self.parameters.opcode_length
        ) // self.parameters.byte
        acc_bytes: int = 0

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
                acc_bytes += 1

            bit_offset = command_bits % self.parameters.byte
            overlay_offsets: list[tuple[int, int, int]] = []
            for symbol in argument.symbols:
                self.text.add_raw_relocation(
                    SymbolRelocationParams(
                        symbol.target,
                        symbol.size,
                        symbol.offset + bit_offset,
                        symbol.relative,
                    )
                )
                relocation_byte_offset = acc_bytes - command_bytes
                overlay_offsets.append(
                    (symbol.offset + bit_offset, relocation_byte_offset, symbol.size)
                )

            command_code <<= argument.n_bits
            command_code |= argument.asint % 2**argument.n_bits
            command_bits += argument.n_bits

            for start, offset, size in overlay_offsets:
                command_code = self.add_overlay(
                    command_code, command_bits, start, offset, size
                )

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

    def add_overlay(
        self, command_code: int, command_bits: int, start: int, offset: int, size: int
    ) -> int:
        """Add an overlay to a relocation.

        Takes the bits start - start + size, and adds offset to them.
        Uses 2-complement to add the offset. Assumes command_code is
        of length command_bits.
        """
        bits_till_end = command_bits - start - size
        overlay_mask = ((1 << size) - 1) << bits_till_end
        original_value = (command_code & overlay_mask) >> bits_till_end
        new_value = original_value + offset
        if new_value < 0:
            new_value += 2**size
        elif new_value >= 2**size:
            new_value -= 2**size
        return (command_code & ~overlay_mask) | (new_value << bits_till_end)

    def add_label(self, label: str) -> None:
        self.text.add_raw_symbol(label)

    def get(self) -> Text:
        """Finish parsing the text section and return the result."""
        return self.text
