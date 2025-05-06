from parse_build import parse
import builder

with open("build", "r") as build_file:
    build = build_file.read()

vals, build_list, assembler_commands = parse(build)
o = builder.build(build_list, assembler_commands)

print(builder.finalize(o))