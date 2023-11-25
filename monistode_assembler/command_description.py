from dataclasses import field
from typing import Literal, TYPE_CHECKING

from monistode_binutils_shared.relocation import SymbolRelocation
from pydantic.dataclasses import dataclass

from monistode_assembler.arguments.address import AddressParser
from monistode_assembler.arguments.common import ArgumentParser
from monistode_assembler.arguments.immediate import ImmediateParser
from monistode_assembler.arguments.label import LabelParser
from monistode_assembler.arguments.padding import PaddingParser
from monistode_assembler.arguments.regiser import RegisterParser
from monistode_assembler.exceptions import AssemblyError, DisassemblyError
from monistode_assembler.sections.text_argument import TextArgument

if TYPE_CHECKING:
    from monistode_assembler.description import Configuration


@dataclass
class ConfigurationRegisterArgument:
    type: Literal["register"]
    group: str

    def get_parsers(
        self, configuration: "Configuration"
    ) -> tuple[ArgumentParser[TextArgument], ...]:
        return (RegisterParser(configuration.register_groups[self.group]),)

    def to_string(
        self,
        value: int,
        relocations_for_argument: list[SymbolRelocation],
        end_of_command_offset: int,
        configuration: "Configuration",
    ) -> str:
        return f"%{configuration.register_groups[self.group][value]}"

    def length_bits(self, configuration: "Configuration") -> int:
        return configuration.register_groups[self.group].length


@dataclass
class ConfigurationImmediateArgument:
    type: Literal["immediate"]
    bits: int

    def get_parsers(
        self, configuration: "Configuration"
    ) -> tuple[ArgumentParser[TextArgument], ...]:
        return (ImmediateParser(self.bits),)

    def to_string(
        self,
        value: int,
        relocations_for_argument: list[SymbolRelocation],
        end_of_command_offset: int,
        configuration: "Configuration",
    ) -> str:
        return "$" + str(value)

    def length_bits(self, configuration: "Configuration") -> int:
        return self.bits


@dataclass
class RelativeTextAddressArgument:
    type: Literal["text_address"]
    bits: int
    relative: bool = field(default=True)

    def get_parsers(
        self, configuration: "Configuration"
    ) -> tuple[ArgumentParser[TextArgument], ...]:
        return (
            AddressParser(self.bits),
            LabelParser(self.bits, relative=self.relative),
        )

    def to_string(
        self,
        value: int,
        relocations_for_argument: list[SymbolRelocation],
        end_of_command_offset: int,
        configuration: "Configuration",
    ) -> str:
        if relocations_for_argument:
            offset = value - end_of_command_offset
            if offset < 0:
                offset += 1 << self.bits
            if offset >= 1 << self.bits:
                offset -= 1 << self.bits
            return " + ".join(
                [
                    ("ABSOLUTE " if not relocation.relative and self.relative else "")
                    + ("OFFSET " if relocation.relative and not self.relative else "")
                    + relocation.symbol.name
                    for relocation in relocations_for_argument
                ]
            ) + (f" + {offset}" if offset else "")
        return str(value)

    def length_bits(self, configuration: "Configuration") -> int:
        return self.bits


@dataclass
class RelativeDataAddressArgument:
    type: Literal["data_address"]
    bits: int
    relative: bool = field(default=False)

    def get_parsers(
        self, configuration: "Configuration"
    ) -> tuple[ArgumentParser[TextArgument], ...]:
        return (
            AddressParser(self.bits),
            LabelParser(self.bits, relative=self.relative),
        )

    def to_string(
        self,
        value: int,
        relocations_for_argument: list[SymbolRelocation],
        end_of_command_offset: int,
        configuration: "Configuration",
    ) -> str:
        if relocations_for_argument:
            offset = value - end_of_command_offset
            if offset < 0:
                offset += 1 << self.bits
            if offset >= 1 << self.bits:
                offset -= 1 << self.bits
            return " + ".join(
                [
                    ("ABSOLUTE " if not relocation.relative and self.relative else "")
                    + ("OFFSET " if relocation.relative and not self.relative else "")
                    + relocation.symbol.name
                    for relocation in relocations_for_argument
                ]
            ) + (f" + {offset}" if offset else "")
        return str(value)

    def length_bits(self, configuration: "Configuration") -> int:
        return self.bits


@dataclass
class ConfigurationPaddingArgument:
    type: Literal["padding"]
    bits: int

    def get_parsers(
        self, configuration: "Configuration"
    ) -> tuple[ArgumentParser[TextArgument], ...]:
        return (PaddingParser(self.bits),)

    def to_string(
        self,
        value: int,
        relocations_for_argument: list[SymbolRelocation],
        end_of_command_offset: int,
        configuration: "Configuration",
    ) -> str:
        if value != 0:
            raise DisassemblyError("Padding argument must be zero")
        if relocations_for_argument:
            raise DisassemblyError("Padding argument cannot be relocated")
        return ""

    def length_bits(self, configuration: "Configuration") -> int:
        return self.bits


@dataclass
class ConfigurationCommand:
    mnemonic: str
    opcode: int
    arguments: list[
        ConfigurationImmediateArgument
        | ConfigurationPaddingArgument
        | RelativeTextAddressArgument
        | RelativeDataAddressArgument
        | ConfigurationRegisterArgument
    ] = field(default_factory=list)

    def get_n_pre_opcode_arguments(
        self, opcode_offset: int, configuration: "Configuration"
    ) -> int:
        if not self.arguments:
            return 0
        offset = 0
        for n_pre_opcode_arguments, argument in enumerate(self.arguments):
            if offset == opcode_offset:
                return n_pre_opcode_arguments
            if offset + argument.length_bits(configuration) > opcode_offset:
                raise AssemblyError(
                    "Opcode offset is not aligned with argument boundaries"
                )
            offset += argument.length_bits(configuration)
        raise AssemblyError("Opcode offset is out of bounds")
