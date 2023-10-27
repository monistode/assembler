"""A class for loading an assembler's description from a file."""
from dataclasses import field

from pydantic.dataclasses import dataclass
import yaml

from .command_description import ConfigurationCommand


@dataclass
class RegisterGroup:
    """A group of registers."""

    length: int
    registers: list[str] | dict[str, int]

    def get_register_index(self, register_name: str) -> int | None:
        """Get the index of a register in the group."""
        if isinstance(self.registers, list):
            if register_name not in self.registers:
                return None
            return self.registers.index(register_name)
        else:
            return self.registers.get(register_name)

    def __getitem__(self, index: int) -> str:
        """Get the register name at the given index."""
        if isinstance(self.registers, list):
            return self.registers[index]
        else:
            return next(
                register_name
                for register_name, register_index in self.registers.items()
                if register_index == index
            )


@dataclass
class Configuration:
    opcode_length: int
    opcode_offset: int
    text_byte_length: int
    data_byte_length: int
    text_address_size: int
    data_address_size: int
    commands: list[ConfigurationCommand]
    register_groups: dict[str, RegisterGroup] = field(default_factory=dict)

    @classmethod
    def load(cls, path: str) -> "Configuration":
        """Load the configuration from a file."""
        with open(path) as file:
            return cls(**yaml.safe_load(file))
