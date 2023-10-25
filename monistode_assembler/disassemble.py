"""Disassemble a binary file into a list of instructions."""
from monistode_binutils_shared import Section
from monistode_binutils_shared.object_manager import ObjectManager
from monistode_binutils_shared.section.text import Text

from monistode_assembler.description import Configuration

from .disassemble_text import TextDisassembler


class Disassembler:
    """A disassembler for the monistode set of ISAs."""

    def __init__(self, configuration: Configuration, binary: bytes) -> None:
        """Initialize a disassembler for the given description.

        Args:
            configuration: The description of the ISA.
            binary: The binary file to disassemble.
        """
        self._configuration = configuration
        self._object_manager = ObjectManager.from_bytes(binary)
        self._object_manager.load()

    def disassemble(self) -> str:
        """Disassemble a binary file into a list of instructions.

        Returns:
            The disassembled binary file.
        """
        sections_disassembled = [
            (section.name, self.disassemble_section(section))
            for section in self._object_manager._sections
        ]

        sections_disassembled_formatted = [
            f".{name}"
            + (
                (" # (not disassembled)\n" + self.raw_display(section))
                if section is None
                else f"\n{section}"
            )
            for name, section in sections_disassembled
        ]

        return "\n\n".join(
            [self._object_manager.summary()] + sections_disassembled_formatted
        )

    def raw_display(self, section: Section) -> str:
        """Display a section of a binary file as raw bytes.

        Args:
            section: The section to display.

        Returns:
            The raw bytes of the section.
        """
        lines = []
        for i, byte in enumerate(section.data):
            if i % 16 == 0:
                lines.append(f"{i:08x}:")
            lines[-1] += f" {byte:02x}"

    def disassemble_section(self, section: Section) -> str | Section:
        """Disassemble a section of a binary file into a list of instructions.

        Args:
            section: The section to disassemble.

        Returns:
            The disassembled section.
        """
        if isinstance(section, Text):
            return TextDisassembler(self._configuration).disassemble(section)
        return section
