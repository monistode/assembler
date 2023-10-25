"""A class for loading an assembler's description from a file."""

from typing import Literal

from pydantic.dataclasses import dataclass
import yaml

from monistode_assembler.arguments.common import ArgumentParser
from monistode_assembler.arguments.immediate import ImmediateParser
from monistode_assembler.arguments.padding import PaddingParser
from monistode_assembler.sections.text import TextArgument


@dataclass
class ConfigurationImmediateArgument:
    type: Literal["immediate"]
    bits: int

    def get_parser(self) -> ArgumentParser[TextArgument]:
        return ImmediateParser(self.bits)


@dataclass
class ConfigurationPaddingArgument:
    type: Literal["padding"]
    bits: int

    def get_parser(self) -> ArgumentParser[TextArgument]:
        return PaddingParser(self.bits)


@dataclass
class ConfigurationCommand:
    mnemonic: str
    opcode: int
    arguments: list[ConfigurationImmediateArgument | ConfigurationPaddingArgument]


@dataclass
class Configuration:
    opcode_length: int
    text_byte_length: int
    data_byte_length: int
    text_address_size: int
    data_address_size: int
    commands: list[ConfigurationCommand]

    @classmethod
    def load(cls, path: str) -> "Configuration":
        """Load the configuration from a file."""
        with open(path) as file:
            return cls(**yaml.safe_load(file))
