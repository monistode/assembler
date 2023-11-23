"""A parser for a sequence of arguments that tries to match a signature."""

import re

from ..exceptions import ParserError
from .common import Argument, ArgumentParser


class MatchingParser:
    """A parser for a sequence of arguments that tries to match a signature."""

    def parse(
        self, line: str, signatures: tuple[tuple[ArgumentParser, ...], ...]
    ) -> tuple[Argument, ...]:
        """Parse the arguments from the line

        Args:
            line (str): The line to parse
            offset (int): The offset to start parsing from

        Raises:
            ParseError: If the line does not match any of the signatures
                or matches multiple signatures
        """
        runs = [self._parse(line, signature) for signature in signatures]
        candidates = [candidate for candidate in runs if candidate is not None]
        if len(candidates) == 0:
            raise ParserError("Could not parse arguments: no matching signature")
        if len(candidates) > 1:
            raise ParserError(
                f"Line matches {len(candidates)} signatures - "
                + ", ".join(
                    " ".join(type(argument).__name__ for argument in candidate)
                    for candidate in candidates
                )
            )
        return candidates[0]

    def _parse(
        self, line: str, signature: tuple[ArgumentParser, ...]
    ) -> tuple[Argument, ...] | None:
        """Parse the arguments from the line

        Args:
            line (str): The line to parse
            signature (tuple[ArgumentParser, ...]): The signature to match

        Returns:
            tuple[Argument, ...] | None: The parsed arguments, or None if the line
                does not match the signature
        """
        offset = 0
        arguments = []
        for parser in signature:
            offset = self._skip_delimiters(line, offset)
            if offset >= len(line):
                return None
            if line[offset] == "#":
                return None
            argument = parser.attempt_scan(line, offset)
            if argument is None:
                return None
            arguments.append(argument)
            offset += argument.length_in_chars
        return tuple(arguments)

    def _skip_delimiters(self, line: str, offset: int) -> int:
        """Skip leading delimiters in a line of source code."""
        result = re.search(r"[^\s,]", line[offset:])
        if result is None:
            return offset
        return result.start() + offset
