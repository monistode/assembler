"""Common types for the section parsers."""
from typing import Protocol, TypeVar

from monistode_binutils_shared import Section

from ..arguments import Argument, ArgumentParser
from ..command import Command


T = TypeVar("T", bound=Argument)


class SectionParser(Protocol[T]):
    """A parser for a single section of an assembly source file."""

    section_name: str

    def command_signatures(
        self, command: str
    ) -> tuple[tuple[ArgumentParser[T], ...], ...]:
        """Get the possible signatures for a command."""

    def add_command(self, command: Command[T]) -> None:
        """Add a command to the section."""

    def add_label(self, label: str) -> None:
        """Add a label to the section."""

    def get(self) -> Section:
        """Finish parsing the section and return the result."""
