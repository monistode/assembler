"""A disassembler for the text section of a monistode binary."""
from typing import Iterator

from monistode_binutils_shared.relocation import SymbolRelocation
from monistode_binutils_shared.section.text import Text

from monistode_assembler.exceptions import DisassemblyError

from .description import Configuration


class AnnotatedIterator(Iterator[int]):
    """An iterator with an annotation for the current address
    and the bytes we are iterating over."""

    def __init__(self, iterator: Iterator[int], start_address: int = 0) -> None:
        """Initialize an annotated iterator.

        Args:
            iterator: The iterator to annotate.
            start_address: The address of the first byte.
        """
        self.iterator = iterator
        self.address = start_address
        self.bytes: list[int] = []

    def __next__(self) -> int:
        """Get the next element of the iterator."""
        self.address += 1
        item = next(self.iterator)
        self.bytes.append(item)
        return item

    def pop(self) -> list[int]:
        """Pop the bytes that were iterated over."""
        popped = self.bytes
        self.bytes = []
        return popped

    def __iter__(self) -> Iterator[int]:
        """Get the iterator."""
        return self


class TextDisassembler:
    """A disassembler for the monistode set of ISAs."""

    def __init__(self, configuration: Configuration) -> None:
        """Initialize a disassembler for the given description.

        Args:
            configuration: The description of the ISA.
        """
        self.configuration = configuration

    def disassemble(self, section: Text) -> str:
        symbols = section.symbols
        instructions = AnnotatedIterator(iter(section))
        disassembly: list[str] = []
        notes: list[str] = []
        addresses: list[int] = []
        symbols = section.symbols
        used_symbols: list[list[str]] = []
        while True:
            try:
                addresses.append(instructions.address)
                disassembly.append(
                    self._disassemble(
                        instructions, instructions.address, section.relocations
                    )
                )
                notes.append(
                    " ".join(self.pprint_byte(byte) for byte in instructions.pop())
                )
                new_symbols = [
                    symbol.name
                    for symbol in symbols
                    if symbol.location.offset < instructions.address
                ]
                used_symbols.append(new_symbols)
                symbols = [
                    symbol for symbol in symbols if symbol.name not in new_symbols
                ]
            except StopIteration:
                break

        max_disassembly_length = (
            max(len(line) for line in disassembly) if disassembly else 0
        )
        output: list[str] = []
        for new_symbols, address, line_disassembly, note in zip(
            used_symbols, addresses, disassembly, notes
        ):
            output.append(
                "\n".join(
                    [f"    {symbol}:" for symbol in new_symbols]
                    + [
                        hex(address)[2:].zfill(
                            -(-self.configuration.text_address_size // 4)
                        )
                        + f": {line_disassembly.ljust(max_disassembly_length)} # {note}"
                    ]
                )
            )
        return "\n".join(output)

    def pprint_byte(self, byte: int) -> str:
        """Pretty print the given byte, taking into account the
        esoteric weirdness that might make it 6 bits long.
        """
        if self.configuration.text_byte_length % 4:
            return bin(byte)[2:].zfill(self.configuration.text_byte_length)
        return hex(byte)[2:].zfill(self.configuration.text_byte_length // 4)

    def _disassemble(
        self,
        instructions: Iterator[int],
        command_address: int,
        relocations: list[SymbolRelocation],
    ) -> str:
        """Disassemble the given instruction.

        Args:
            instructions: The instructions to disassemble.
        """
        instructions_till_opcode = self.get_instructions_till_opcode()
        command_instructions = [
            next(instructions) for _ in range(instructions_till_opcode)
        ]
        extracted_opcode = self.extract_opcode(command_instructions)
        for command in self.configuration.commands:
            if command.opcode == extracted_opcode:
                arg_strings: list[str] = []
                offset: int = 0
                n_pre_opcode_arguments = command.get_n_pre_opcode_arguments(
                    self.configuration.opcode_offset, self.configuration
                )
                command_length = (
                    sum(
                        argument.length_bits(self.configuration)
                        for argument in command.arguments
                    )
                    + self.configuration.opcode_length
                )
                if n_pre_opcode_arguments == 0:
                    offset += self.configuration.opcode_length
                for i, argument in enumerate(command.arguments):
                    offset += argument.length_bits(self.configuration)
                    while offset > self.configuration.text_byte_length * len(
                        command_instructions
                    ):
                        command_instructions.append(next(instructions))

                    argument_value = self.extract_argument(
                        self.instructions_to_command(command_instructions),
                        len(command_instructions),
                        offset - argument.length_bits(self.configuration),
                        argument.length_bits(self.configuration),
                    )
                    # Find all relocatiosn that cover this argument.
                    relocations_for_argument = [
                        relocation
                        for relocation in relocations
                        if relocation.location.offset
                        == command_address
                        + (
                            (offset - argument.length_bits(self.configuration))
                            // self.configuration.text_byte_length
                        )
                        and relocation.size == argument.length_bits(self.configuration)
                        and relocation.offset
                        == (offset - argument.length_bits(self.configuration))
                        % self.configuration.text_byte_length
                    ]
                    arg_strings.append(
                        argument.to_string(
                            argument_value,
                            relocations_for_argument,
                            (
                                offset
                                - argument.length_bits(self.configuration)
                                - command_length
                            )
                            // self.configuration.text_byte_length,
                            self.configuration,
                        )
                    )

                    if i == n_pre_opcode_arguments - 1:
                        offset += self.configuration.opcode_length
                if offset % self.configuration.text_byte_length:
                    raise DisassemblyError(
                        f"Command {command.mnemonic} is not aligned properly."
                    )
                return f"{command.mnemonic} {' '.join(arg_strings)}"
        raise DisassemblyError(f"Unknown opcode: {extracted_opcode}")

    def get_instructions_till_opcode(self) -> int:
        """Get the number of instructions that will definitely
        include the opcode.
        """
        last_bit = self.configuration.opcode_offset + self.configuration.opcode_length
        return -(-last_bit // self.configuration.text_byte_length)

    def instructions_to_command(self, instructions: list[int]) -> int:
        """Convert the given instructions to a command."""
        command = 0
        for instruction in instructions:
            command <<= self.configuration.text_byte_length
            command |= instruction
        return command

    def extract_opcode(self, instructions: list[int]) -> int:
        """Extract the opcode from the given instructions."""
        return self.extract_argument(
            self.instructions_to_command(instructions),
            len(instructions),
            self.configuration.opcode_offset,
            self.configuration.opcode_length,
        )

    def extract_argument(
        self, command: int, command_size: int, offset: int, size: int
    ) -> int:
        """Extract an argument from the given command."""
        trailing_bits: int = (
            self.configuration.text_byte_length * command_size - offset - size
        )
        command >>= trailing_bits

        argument_mask: int = (1 << size) - 1
        return command & argument_mask
