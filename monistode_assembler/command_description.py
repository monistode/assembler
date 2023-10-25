from typing import Literal

from pydantic.dataclasses import dataclass

from monistode_assembler.arguments.common import ArgumentParser
from monistode_assembler.arguments.immediate import ImmediateParser
from monistode_assembler.arguments.padding import PaddingParser
from monistode_assembler.exceptions import AssemblyError, DisassemblyError
from monistode_assembler.sections.text_argument import TextArgument


@dataclass
class ConfigurationImmediateArgument:
    type: Literal["immediate"]
    bits: int

    def get_parser(self) -> ArgumentParser[TextArgument]:
        return ImmediateParser(self.bits)

    def to_string(self, value: int) -> str:
        return "$" + str(value)


@dataclass
class ConfigurationPaddingArgument:
    type: Literal["padding"]
    bits: int

    def get_parser(self) -> ArgumentParser[TextArgument]:
        return PaddingParser(self.bits)

    def to_string(self, value: int) -> str:
        if value != 0:
            raise DisassemblyError("Padding argument must be zero")
        return ""


@dataclass
class ConfigurationCommand:
    mnemonic: str
    opcode: int
    arguments: list[ConfigurationImmediateArgument | ConfigurationPaddingArgument]

    def get_n_pre_opcode_arguments(self, opcode_offset: int) -> int:
        offset = 0
        n_pre_opcode_arguments = 0
        for argument in self.arguments:
            if offset == opcode_offset:
                break
            if offset + argument.bits > opcode_offset:
                raise AssemblyError(
                    "Opcode offset is not aligned with argument boundaries"
                )
            n_pre_opcode_arguments += 1
            offset += argument.bits
        return n_pre_opcode_arguments
