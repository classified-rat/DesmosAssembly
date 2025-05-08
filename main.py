import logging
import sys

from parse_build import parse
import builder
from classes import Acommand

# init logger
logging.basicConfig(stream=sys.stdout, format="%(levelname)s - %(module)s: %(message)s")
logging.addLevelName(5, "VERBOSE")

logger = logging.getLogger("")
logger.setLevel(logging.NOTSET)

logger.log(5, "LOGGER STARTED")

with open("build", "r") as build_file:
    build = build_file.read()

vals: dict
build_list: list
assembler_commands: list[Acommand]

vals, build_list, assembler_commands = parse(build)
o = builder.build(build_list, assembler_commands)

output: str = builder.finalize(o)

logger.info(f"compiled code: {output}")

for command in assembler_commands:
    if command.name == "output":
        with open(command.file_reference[0], "w") as OUTPUT:
            OUTPUT.write(output)