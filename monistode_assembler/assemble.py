"""Assemble a program into an object file."""
import itertools
from typing import Iterator

from monistode_binutils_shared import ObjectManager, ObjectParameters

from monistode_assembler.arguments.common import ArgumentParser
from monistode_assembler.command_description import ConfigurationCommand
from monistode_assembler.sections.common import SectionParser
from monistode_assembler.sections.data import DataSectionParameters, DataSectionParser
from monistode_assembler.sections.text import (
    CommandDefinition,
    TextSectionParameters,
    TextSectionParser,
)
from monistode_assembler.sections.text_argument import TextArgument

from .description import Configuration
from .parse import Parser


class Assembler:
    """An assembler for monistode assembly language source files."""

    def __init__(self, configuration: Configuration) -> None:
        """Initialize the assembler."""
        self._configuration = configuration
        section_parsers: list[SectionParser] = [
            TextSectionParser(
                parameters=TextSectionParameters(
                    byte=configuration.text_byte_length,
                    opcode_offset=configuration.opcode_offset,
                    opcode_length=configuration.opcode_length,
                    text_address_bits=configuration.text_address_size,
                    data_address_bits=configuration.data_address_size,
                ),
                commands=[
                    CommandDefinition(
                        mnemonic=command.mnemonic,
                        opcode=command.opcode,
                        arguments=signature,
                        pre_opcode_arguments=command.get_n_pre_opcode_arguments(
                            configuration.opcode_offset, configuration
                        ),
                    )
                    for command in configuration.commands
                    for signature in self.signatures_for(command)
                ],
            ),
            DataSectionParser(
                parameters=DataSectionParameters(
                    byte=configuration.data_byte_length,
                    data_address_bits=configuration.data_address_size,
                )
            ),
        ]
        self._parser = Parser(section_parsers)
        self._object_parameters = ObjectParameters(
            opcode_size=configuration.opcode_length,
            text_byte=configuration.text_byte_length,
            data_byte=configuration.data_byte_length,
            text_address=configuration.text_address_size,
            data_address=configuration.data_address_size,
        )
        self._manager = ObjectManager(self._object_parameters)

    def signatures_for(
        self, command: ConfigurationCommand
    ) -> Iterator[tuple[ArgumentParser[TextArgument], ...]]:
        """Generate all possible signatures for a command.

        Args:
            command (ConfigurationCommand): The command to generate signatures for

        Yields:
            tuple[ArgumentParser[TextArgument], ...]: The signature,
                as a tuple of argument parsers
        """
        for signature in itertools.product(
            *(
                argument.get_parsers(self._configuration)
                for argument in command.arguments
            )
        ):
            yield signature

    def assemble(self, source: str) -> bytes:
        """Assemble a program from a source file."""
        self._parser.parse(source)
        for section in self._parser.generate_sections():
            self._manager.append_section(section)
        return self._manager.to_bytes()
