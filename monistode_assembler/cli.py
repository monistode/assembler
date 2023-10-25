"""A CLI for the assembler."""

import click
import yaml

from .assemble import Assembler
from .description import Configuration
from .disassemble import Disassembler


@click.group()
def main() -> None:
    """Assemble and disassemble monistode assembly files."""
    pass


@main.command()
@click.argument("configuration", type=click.File("r"))
@click.argument("source", type=click.File("r"))
@click.argument("destination", type=click.File("wb"))
def assemble(source, destination, configuration) -> None:
    """Assemble a source file into an object file."""
    assembler = Assembler(configuration=Configuration(**yaml.safe_load(configuration)))
    assembled = assembler.assemble(source.read())
    destination.write(assembled)


@main.command()
@click.argument("configuration", type=click.File("r"))
@click.argument("source", type=click.File("rb"))
@click.argument("destination", type=click.File("w"), default="-")
@click.option("--header-only", is_flag=True)
def disassemble(source, destination, configuration, header_only) -> None:
    """Disassemble an object file into a source file."""
    disassembler = Disassembler(
        configuration=Configuration(**yaml.safe_load(configuration)),
        binary=source.read(),
    )
    if header_only:
        disassembled = disassembler.disassemble_header()
    else:
        disassembled = disassembler.disassemble()
    destination.write(disassembled + "\n")


if __name__ == "__main__":
    main()
