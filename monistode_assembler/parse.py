"""Parse an asembly source file into a list of instructions."""
import re

from monistode_binutils_shared import Section

from .arguments import Argument, MatchingParser
from .command import Command
from .exceptions import AssemblerError, ParserError
from .sections import SectionParser


class Parser:
    """A parser for monistode assembly language source files."""

    def __init__(
        self,
        section_parsers: list[SectionParser],
    ) -> None:
        """Initialize the parser."""
        self._section_parsers = section_parsers
        self._argument_parser = MatchingParser()
        self._current_section_parser: SectionParser | None = None

    def parse(self, source: str) -> list[Section]:
        for line_number, line in enumerate(source.splitlines()):
            try:
                self._parse_line(line)
            except AssemblerError as error:
                error.line_number = line_number
                error.line_content = line
                raise error
        return self.generate_sections()

    def generate_sections(self) -> list[Section]:
        """Generate the sections from the parsed source code."""
        sections = []
        for parser in self._section_parsers:
            sections.append(parser.get())
        # TODO: aggregate relocations and symbols
        return sections

    def _parse_line(self, line: str) -> None:
        """Parse the source code into a list of sections."""
        line = self._clean_line(line)
        if not line:
            return
        section_name = self._parse_section_name(line)
        if section_name is not None:
            self._current_section_parser = self._get_section_parser(section_name)
            return
        label = self._parse_label(line)
        if label is not None:
            self._add_label(label)
            self._parse_line(line[0 if label is None else len(label) + 1 :])
            return
        command = self._parse_command(line)
        if command is None or command.startswith("#"):
            return
        command = command.lower()
        arguments = self._parse_arguments(command, line[len(command) :])
        self._add_command(Command(command, arguments))

    def _get_section_parser(self, section_name: str) -> SectionParser:
        """Get the parser for a section."""
        for parser in self._section_parsers:
            if parser.section_name == section_name:
                return parser
        raise ParserError(f"Unknown section name: {section_name}")

    def _clean_line(self, line: str) -> str:
        """Clean a line of source code."""
        return line.strip()

    def _find_whitespace(self, line: str, start: int = 0) -> int:
        """Find the next whitespace character in a string."""
        result = re.search(r"\s", line[start:])
        if result is None:
            return -1
        return result.start() + start

    def _strip_comments(self, line: str, start: int = 0) -> str:
        """Strip comments from a line of source code."""
        result = re.search(r"#", line[start:])
        if result is None:
            return line
        return line[: result.start()]

    def _parse_section_name(self, line: str) -> str | None:
        """Parse the name of a section."""
        if line.startswith("."):
            return self._strip_comments(line[1:])
        return None

    def _parse_label(self, line: str) -> str | None:
        """Parse a label."""
        first_whitespace = self._find_whitespace(line)
        if first_whitespace == -1:
            if line.endswith(":"):
                return line[:-1]
            return None
        if line[first_whitespace + 1] == ":":
            return line[:first_whitespace]

    def _add_label(self, label: str) -> None:
        """Add a label to the current section."""
        if self._current_section_parser is None:
            raise ParserError("Label found outside of section")
        self._current_section_parser.add_label(label)

    def _parse_command(self, line: str) -> str | None:
        """Parse a command."""
        first_whitespace = self._find_whitespace(line)
        if "#" in line:
            first_whitespace = min(line.find("#"), first_whitespace)
        if first_whitespace == -1:
            return line
        if first_whitespace == 0:
            return None
        return line[:first_whitespace]

    def _parse_arguments(
        self, command: str, raw_arguments: str
    ) -> tuple[Argument, ...]:
        """Parse the arguments of a command."""
        if self._current_section_parser is None:
            raise ParserError("Command found outside of section")
        signatures = self._current_section_parser.command_signatures(command)
        return self._argument_parser.parse(raw_arguments, signatures)

    def _add_command(self, command: Command) -> None:
        """Add a command to the current section."""
        if self._current_section_parser is None:
            raise ParserError("Command found outside of section")
        self._current_section_parser.add_command(command)
