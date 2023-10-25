from dataclasses import field
from typing import Literal

from pydantic.dataclasses import dataclass

from monistode_assembler.arguments.address import AddressParser
from monistode_assembler.arguments.common import ArgumentParser
from monistode_assembler.arguments.immediate import ImmediateParser
from monistode_assembler.arguments.label import LabelParser
from monistode_assembler.arguments.padding import PaddingParser
from monistode_assembler.exceptions import AssemblyError, DisassemblyError
from monistode_assembler.sections.text_argument import TextArgument


@dataclass
class ConfigurationImmediateArgument:
    type: Literal["immediate"]
    bits: int

    def get_parsers(self) -> tuple[ArgumentParser[TextArgument], ...]:
        return (ImmediateParser(self.bits),)

    def to_string(self, value: int) -> str:
        return "$" + str(value)


@dataclass
class RelativeTextAddressArgument:
    type: Literal["text_addr"]
    bits: int
    relative: bool = field(default=False)

    def get_parsers(self) -> tuple[ArgumentParser[TextArgument], ...]:
        return (
            AddressParser(self.bits),
            LabelParser(self.bits, relative=self.relative),
        )

    def to_string(self, value: int) -> str:
        return str(value)


@dataclass
class ConfigurationPaddingArgument:
    type: Literal["padding"]
    bits: int

    def get_parsers(self) -> tuple[ArgumentParser[TextArgument], ...]:
        return (PaddingParser(self.bits),)

    def to_string(self, value: int) -> str:
        if value != 0:
            raise DisassemblyError("Padding argument must be zero")
        return ""


@dataclass
class ConfigurationCommand:
    mnemonic: str
    opcode: int
    arguments: list[
        ConfigurationImmediateArgument
        | ConfigurationPaddingArgument
        | RelativeTextAddressArgument
    ]

    def get_n_pre_opcode_arguments(self, opcode_offset: int) -> int:
        offset = 0
        for n_pre_opcode_arguments, argument in enumerate(self.arguments):
            if offset == opcode_offset:
                return n_pre_opcode_arguments
            if offset + argument.bits > opcode_offset:
                raise AssemblyError(
                    "Opcode offset is not aligned with argument boundaries"
                )
            offset += argument.bits
        raise AssemblyError("Opcode offset is out of bounds")
