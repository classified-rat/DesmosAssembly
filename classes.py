from __future__ import annotations
from typing import Optional

# token class
class Token:
    # properties
    name: str
    value: float | str

    # methods
    def __init__(self, name: str, value: Optional[float | str] = None):
        self.name = name
        self.value = value

    # set value of token if not set in constructor
    def set_value(self, value: float | str):
        self.value = value

    # returns whether token is defined
    def is_defined(self) -> bool:
        return self.value is not None

# keeps all tokens in one place
class TokenManager:
    tokens: list[Token]

    def __init__(self):
        self.tokens = []

    def add_token(self, token: Token):
        self.tokens.append(token)

    def __iadd__(self, other: Token):
        self.tokens.append(other)
        return self

    # set value of token given a name
    def set_token_value(self, name: str, value: float):
        for token in self.tokens:
            if token.name == name:
                token.value = value
                return
        raise KeyError

    # get value of token based on name
    def search_tokens(self, name: str) -> float | str:
        for token in self.tokens:
            if token.name == name:
                return token.value
        raise KeyError

    def token_exists(self, name: str) -> bool:
        for token in self.tokens:
            if token.name == name:
                return True
        return False

    def token_exists_with_value(self, name: str) -> bool:
        if self.token_exists(name):
            return self[name].is_defined()
        return False

    # get token by name
    def __getitem__(self, item: str):
        for token in self.tokens:
            if token.name == item:
                return token
        raise KeyError

    # get string representation of manager
    def __repr__(self):
        out: str = ""
        for token in self.tokens:
            out += f"{token.name}: {token.value}\n"
        return out

# data structure representing compiled code
class Dasm:
    file_name: str
    code: list
    raw_code: list[str]
    has_raw_code: bool
    offset: int = 0

    def __init__(self, file_name: str, compiled_code: list, raw_code: Optional[list[str]] = None):
        self.file_name: str = file_name
        self.code: list = compiled_code

        if raw_code is not None:
            self.has_raw_code: bool = True
            self.raw_code: list[str] = raw_code
        else:
            self.has_raw_code: bool = True

    def __repr__(self):
        return f"<Dasm {self.file_name} : {self.code}>"

    def __str__(self):
        code = [str(e) for e in self.code]
        return f"\\left[{', '.join(code)}\\right]"

# assembler command representation
class Acommand:
    name: str
    args: list[str]
    file_reference: list[str] = []

    def __init__(self, name: str, args: list[str]):
        self.name = name
        self.args = args
        self.file_reference = []

    def pass_vals(self, vals: dict) -> Acommand:
        print(f"args: {self.args}")
        print(f"file_ref: {self.file_reference}")
        for i, arg in enumerate(self.args):
            name: str = arg
            if arg.startswith("$"):
                name = vals[arg[1:]]

            self.file_reference.append(name)
            print(self.file_reference)

        return self


    def find_file_reference(self, name: str) -> bool:
        for arg in self.file_reference:
            if arg == name:
                return True
        return False

