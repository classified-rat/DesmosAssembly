import regex as re
from classes import Acommand

def parse(build: str) -> tuple[dict, list, list]:
    vals: dict = {}
    build_list: list = []
    assemble_commands: list[Acommand] = []

    for line in build.split("\n"):
        if line == "":
            continue
        line = line.split("#")[0]
        if re.match(r"^.*:.*$", line) is not None:
            vals[line.split(":")[0]] = line.split(":")[1].strip()

        if re.match(r"^[Bb]uild\s+\$\w*$", line) is not None:
            build_list.append(vals[line.split("$")[-1]])

        if re.match(r"^merge \$\w+ \$\w+$", line) is not None:
            args = line.split(" ")
            # assemble_commands.append({"merge": (args[1].strip(), args[2].strip())})
            assemble_commands.append(Acommand("merge",
                                              [args[1].strip(),
                                                    args[2].strip()]).
                                     pass_vals(vals))

        if re.match(r"output .*", line) is not None:
            args = line.split(" ")
            assemble_commands.append(Acommand("output",
                                              [args[1].strip()]).
                                     pass_vals(vals))

    print(vals)
    return vals, build_list, assemble_commands
