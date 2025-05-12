import logging
import regex as re
from classes import Token, TokenManager, Dasm, Acommand

# get logger
logger = logging.getLogger("")

# list of instructions and associated data
_instructions = {
    r"ld\s+rx\s+.?(?:[0-9]+|\$\w+(?=$|\s|\]))": {"length": 2, "opcode": 0},
    r"ld\s+ry\s+.?(?:[0-9]+|\$\w+(?=$|\s|\]))": {"length": 2, "opcode": 1},
    r"mov\s+rx\s+acc": {"length": 1, "opcode": 2},
    r"add": {"length": 1, "opcode": 3},
    r"jnz\s+(?:[0-9]+|\$\w+(?=$|\s|\]))": {"length": 2, "opcode": 4},
    r"^push\s+rx": {"length": 1, "opcode": 5},
    r"push\s+ry": {"length": 1, "opcode": 6},
    r"pop\s+rx": {"length": 1, "opcode": 7},
    r"pop\s+ry": {"length": 1, "opcode": 8},
    r"dec\s+rx": {"length": 1, "opcode": 9},
    r"dec\s+ry": {"length": 1, "opcode": 10},
    r"mov\s+rx\s+\[(?:[0-9]+|\$\w+(?=$|\s|\]))\]": {"length": 2, "opcode": 11},
    r"mov\s+ry\s+\[(?:[0-9]+|\$\w+(?=$|\s|\]))\]": {"length": 2, "opcode": 12},
    r"call\s+(?:[0-9]+|\$\w+(?=$|\s|\]))": {"length": 2, "opcode": 13},
    r"ret": {"length": 1, "opcode": 14},
    r"jl\s+(?:[0-9]+|\$\w+(?=$|\s|\])),\s*(?:[0-9]+|\$\w+(?=$|\s|\]))": {"length": 3, "opcode": 15},
    r"mult": {"length": 1, "opcode": 16},
    r"neg": {"length": 1, "opcode": 17},
    r"inv": {"length": 1, "opcode": 18},
    r"^pop": {"length": 1, "opcode": 19},
    r"mov\s+rx\s+\^(?:[0-9]+|\$\w+(?=$|\s|\]))": {"length": 2, "opcode": 20},
    r"mov\s+rx\s+\^ry": {"length": 1, "opcode": 21},
    r"ppush\s+rx": {"length": 1, "opcode": 22},
    r"poly\s*$": {"length": 1, "opcode": 23},
    r"polypop": {"length": 1, "opcode": 24},
    r"mov\s+\^ry\s+rx": {"length": 1, "opcode": 25},
    r"^db\s+(?:[,.-0-9]*|\$\w+(?=$|\s|\]))": {"length": -1, "opcode": None, "name": "db"}, # special instructions, defines values to put in to the code
    r"^resb\s+(?:[0-9]*|\$\w+(?=$|\s|\]))": {"length": -1, "opcode": None, "name": "resb"}
}

def build(files: list[str] | str, assembler_commands: list[Acommand]) -> dict[str, Dasm]:
    if type(files) is str:
        files = [files]

    logger.info(f"compiling files: {files}")

    manager: TokenManager = TokenManager()

    for command in assembler_commands:
        if command.name == "merge":
            root = command.file_reference[0]
            name = command.file_reference[1]
            manager.add_token(Token(f"__{root}_store_offset",
                                    f"__{name}_offset"))
            manager.add_token(Token(f"__{name}_offset"))

    out: dict[str, Dasm] = {}
    for file in files:
        compiled: list = []
        with open(file, "r") as FILE:
            code = FILE.readlines()
            code = filter_file(code)

        # get preprocessor directives
        directives: list[str] = [line for line in code if line[0] == "#"]
        for directive in directives:
            if directive.lower().startswith("#define"):
                name: str = re.split("\\s+", directive)[1]
                value: str = re.split("\\s+", directive)[2]
                value: float | str = float(value) if re.match(".?[0-9.]+", value) is None else value
                manager += Token(name, value)

        code = [line for line in code if not line[0] == "#"]

        # compile code
        for line in code:
            line = line.strip()
            if line[0] == ":": # detect labels
                offset: int = 0
                if manager.token_exists(f"__{file}_offset"):
                    offset = int(manager.search_tokens(f"__{file}_offset"))
                name: str = line[1:]
                value: float = len(compiled) + 1 + offset
                manager += Token(name, value)

            else:  # normal instructions

                tokens: list[str] = re.findall(r"\$\w+(?=$|\s|\])", line)
                for token in tokens:
                    token: str
                    name: str = re.findall(r"\w+", token)[0]
                    if manager.token_exists(name):
                        rep = manager.search_tokens(name)
                        logger.debug(f"token {token} replaced to {rep}\n\tin line \"{line}\"")
                        line = re.sub(f"\\${name}(?:$|\\s|\\])", str(rep), line)

                comp = parse_instruction(line, manager)
                # print(f"{line} -> {comp}")
                compiled.extend(comp)

        for i, val in enumerate(compiled):
            if len(match := re.findall(r"[^0-9.-]+", str(val))) > 0:
                match: list
                name: str = re.findall(r"\w+", match[0])[0]
                compiled[i] = manager.search_tokens(name)

        dasm: Dasm = Dasm(file, compiled, code)
        if manager.token_exists(f"__{file}_store_offset"):
            name = manager.search_tokens(f"__{file}_store_offset")
            manager.set_token_value(name, len(compiled))

        if manager.token_exists(f"__{file}_offset"):
            offset: int = int(manager.search_tokens(f"__{file}_offset"))
            dasm.offset = offset

        out[file] = dasm

    # print(manager)
    logger.info(f"Manager tokens: {manager}")
    return out

def parse_instruction(instruction: str, manager: TokenManager) -> list:
    # figure out which instruction it is
    for inst in _instructions.keys():
        if re.match(inst, instruction) is not None:
            logger.debug(f"\"{instruction}\" matched instruction regex /{inst}/")

            # get the arguments for the opcode
            args: list = instruction.strip().split(",")
            args[0] = args[0].split(" ")[-1]

            # truncate length of args to needed length
            if not _instructions[inst]["length"] == -1:
                args: str = args[:_instructions[inst]["length"]-1]

            if instruction.startswith("resb"):
                logger.debug("reserving memory")
                args = ["0"] * int(args[0])


            # get tokens in args
            retoken: list = []
            for i, arg in enumerate(args):
                if arg.strip().startswith("$"):
                    name: str = re.findall(r"\w+", arg.strip())[0]

                    # if token is defined replace it with value
                    if manager.token_exists_with_value(name):
                        args[i] = str(manager.search_tokens(name))

                    # if it's not defined replace it with zero
                    # keep track of index and put the token back in after float case
                    else:
                        retoken.append({"index": i,
                                        "token": arg.strip()})
                        args[i] = "0.0"

            if len(args) > 0:
                logger.debug(f"instruction args: {args}")

            # convert to numbers
            args = [float(re.sub(r"[\[\]]", "", arg).replace("^","")) for arg in args]

            for replace in retoken:
                replace: dict
                args[replace["index"]] = replace["token"]

            # return the code
            operation: list = [_instructions[inst]["opcode"]]+args if _instructions[inst]["opcode"] is not None else args
            return operation

    # prevent exceptions by returning empty code list
    logger.warning(f"instruction \"{instruction}\" did not match any instruction")
    return []

def finalize(code: dict[str, Dasm]) -> str:
    output: list = []
    for file in code.keys():
        i: int = 0
        for v in code[file].code:
            if i+code[file].offset+1 > len(output):
                output.append(v)
            else:
                output[i] = v
            i += 1

    return str(Dasm("out", output))

def filter_file(lines: list[str]) -> list[str]:
    filtered_code: list[str] = []
    for line in lines:
        # strip newlines
        line = line.strip()

        # remove comments
        line = line.split(";")[0]

        # get rid of empty lines
        if line == "":
            continue

        filtered_code.append(line)

    return filtered_code