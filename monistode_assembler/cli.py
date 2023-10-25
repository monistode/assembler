"""A CLI for the assembler."""

import click
import yaml

from .assemble import Assembler
from .description import Configuration


@click.command()
@click.argument("source", type=click.File("r"))
@click.argument("destination", type=click.File("wb"))
@click.argument("configuration", type=click.File("r"))
def main(source, destination, configuration) -> None:
    """Assemble a source file into an object file."""
    assembler = Assembler(configuration=Configuration(**yaml.safe_load(configuration)))
    assembled = assembler.assemble(source.read())
    destination.write(assembled)


if __name__ == "__main__":
    main()
