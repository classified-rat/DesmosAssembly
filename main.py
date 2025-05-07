from parse_build import parse
import builder
from classes import Acommand

with open("build", "r") as build_file:
    build = build_file.read()

vals: dict
build_list: list
assembler_commands: list[Acommand]

vals, build_list, assembler_commands = parse(build)
o = builder.build(build_list, assembler_commands)

output: str = builder.finalize(o)

for command in assembler_commands:
    if command.name == "output":
        with open(command.file_reference[0], "w") as OUTPUT:
            OUTPUT.write(output)