"""Exceptions for the assembler."""


class AssemblerError(Exception):
    """An error that occurred while assembling a program."""

    def __init__(self, message: str, line_number: int | None = None) -> None:
        """Initialize the error.

        Args:
            message: The error message.
            line_number: The line number where the error occurred.
        """
        super().__init__(message)
        self.line_number = line_number
        self.message = message


class AssemblyError(AssemblerError):
    """An error that occurred while assembling an assembly source file."""


class DisassemblyError(AssemblerError):
    """An error that occurred while disassembling a binary file."""


class ParserError(AssemblerError):
    """An error that occurred while parsing an assembly source file."""
