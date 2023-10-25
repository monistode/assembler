"""Assemble a program into an object file."""
from monistode_binutils_shared import ObjectManager, ObjectParameters

from monistode_assembler.sections.common import SectionParser
from monistode_assembler.sections.text import (
    CommandDefinition,
    TextSectionParameters,
    TextSectionParser,
)

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
                    opcode_length=configuration.opcode_length,
                    text_address_bits=configuration.text_address_size,
                    data_address_bits=configuration.data_address_size,
                ),
                commands=[
                    CommandDefinition(
                        mnemonic=command.mnemonic,
                        opcode=command.opcode,
                        arguments=tuple(
                            argument.get_parser() for argument in command.arguments
                        ),
                    )
                    for command in configuration.commands
                ],
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

    def assemble(self, source: str) -> bytes:
        """Assemble a program from a source file."""
        self._parser.parse(source)
        for section in self._parser.generate_sections():
            self._manager.append_section(section)
        return self._manager.to_bytes()
