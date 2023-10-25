"""A class for loading an assembler's description from a file."""


from pydantic.dataclasses import dataclass
import yaml

from .command_description import ConfigurationCommand


@dataclass
class Configuration:
    opcode_length: int
    opcode_offset: int
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
