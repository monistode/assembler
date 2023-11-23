"""Exceptions for the assembler."""


class AssemblerError(Exception):
    """An error that occurred while assembling a program."""

    def __init__(
        self,
        message: str,
        line_number: int | None = None,
        line_content: str | None = None,
    ) -> None:
        """Initialize the error.

        Args:
            message: The error message.
            line_number: The line number where the error occurred.
            line_content: The content of the line where the error occurred.
        """
        super().__init__(message)
        self.message = message
        self.line_number = line_number
        self.line_content = line_content

    def __str__(self) -> str:
        """Return the error message."""
        return (
            f"{self.message} (line {self.line_number})"
            if self.line_number
            else self.message
        ) + (f"\n{self.line_content}" if self.line_content else "")


class AssemblyError(AssemblerError):
    """An error that occurred while assembling an assembly source file."""


class DisassemblyError(AssemblerError):
    """An error that occurred while disassembling a binary file."""


class ParserError(AssemblerError):
    """An error that occurred while parsing an assembly source file."""
