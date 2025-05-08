from __future__ import annotations
import logging
from typing import Optional
from collections import UserList

# get logger
logger = logging.getLogger("")
VERBOSE: int = 5  # custom logging level for this module


# token class
class Token:
    """Keeps track of values used for compilation"""
    # properties
    name: str
    value: float | str

    # methods
    def __init__(self, name: str, value: Optional[float | str] = None):
        self.name = name
        self.value = value

        logger.log(VERBOSE, f"New token created {{\"{self.name}\": \"{self.value}\"}}")

    # set value of token if not set in constructor
    def set_value(self, value: float | str) -> None:
        """Sets value of token and triggers log message"""
        self.value = value
        logger.log(VERBOSE, f"Token defined {{\"{self.name}\": \"{self.value}\"}}")

    # returns whether token is defined
    def is_defined(self) -> bool:
        """checks if the token has a value"""
        return self.value is not None

    def __repr__(self):
        return f"{{\"{self.name}\":\"{self.value}\"}}"


# keeps all tokens in one place
class TokenManager:
    """Keeps track of and manages individual tokens"""
    tokens: list[Token]

    def __init__(self):
        self.tokens = []

    def add_token(self, token: Token) -> None:
        """Adds token manager registry"""
        self.tokens.append(token)
        logger.log(VERBOSE, f"Token added to manager {token}")

    def __iadd__(self, other: Token) -> TokenManager:
        """Adds token manager registry"""
        self.add_token(other)
        return self

    # set value of token given a name
    def set_token_value(self, name: str, value: float) -> None:
        """Set a token value based on a name"""
        for token in self.tokens:
            if token.name == name:
                token.set_value(value)
                return

        logger.exception(f"No token \"{name}\" exists")
        raise KeyError

    # get value of token based on name
    def search_tokens(self, name: str) -> float | str:
        """Get value of a token based on a name"""
        for token in self.tokens:
            if token.name == name:
                return token.value

        logger.exception(f"No token \"{name}\" exists")
        raise KeyError

    def token_exists(self, name: str) -> bool:
        """Check to see if a token exists"""
        for token in self.tokens:
            if token.name == name:
                return True
        return False

    def token_exists_with_value(self, name: str) -> bool:
        """Check if a token exists and if it is defined"""
        if self.token_exists(name):
            return self[name].is_defined()
        return False

    # get token by name
    def __getitem__(self, item: str) -> Token:
        for token in self.tokens:
            if token.name == item:
                return token

        logger.exception(f"No token \"{item}\" exists")
        raise KeyError

    # get string representation of manager
    def __repr__(self) -> str:
        out: str = ""
        for token in self.tokens:
            out += f"{token.name}: {token.value}\n"
        return out


# data structure representing compiled code
class Dasm:
    """Represents a compiled .dasm file"""
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

    def __repr__(self) -> str:
        return f"<Dasm {self.file_name} : {self.code}>"

    def __str__(self) -> str:
        code = [str(e) for e in self.code]
        return f"\\left[{', '.join(code)}\\right]"


# assembler command representation
class Acommand:
    """Represent a command used at some point in the compilation process"""
    name: str
    args: list[str]
    file_reference: list[str] = []

    def __init__(self, name: str, args: list[str]):
        self.name = name
        self.args = args
        self.file_reference = []

        logger.log(VERBOSE, f"New assembler command object \"{self.name}\" created")

    def pass_vals(self, vals: dict) -> Acommand:
        """Pass the values from the build file"""
        # print(f"args: {self.args}")
        # print(f"file_ref: {self.file_reference}")
        for i, arg in enumerate(self.args):
            name: str = arg
            if arg.startswith("$"):
                name = vals[arg[1:]]

            self.file_reference.append(name)
            # print(self.file_reference)

        return self

    def __repr__(self) -> str:
        return f"<Acommand {self.name}>"


# ----------------------------------------------
# Desmos Emulation classes
# the following classes are designed to emulate
# the functionality of data types from Desmos
# ----------------------------------------------


class Dlist(UserList):
    """Emulation of Desmos' list"""
    def __getitem__(self, i):
        if isinstance(i, slice):

            i = slice(i.start - 1 if i.start is not None else None,
                      i.stop - 1 if i.stop is not None else None,
                      i.step)
            return self.__class__(self.data[i])
        else:
            logger.log(VERBOSE, f"Dlist getitem index: {i}")
            if i < 1 or i > len(self.data):
                logger.warning("Dlist out of bounds reference, defaulting")
                return None
            return self.data[int(i - 1)]

    def __setitem__(self, i, item):
        self.data[i - 1] = item

    def __repr__(self):
        return f"D{repr(self.data)}"


class Point:
    """Emulation of Desmos' Point"""
    x: float
    y: float

    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

    def __repr__(self):
        return f"D({self.x}, {self.y})"

    def __str__(self):
        return f"\\left({self.x}, {self.y}\\right)"


class Polygon:
    """Emulation of Desmos' polygon"""
    points: list[Point]

    def __init__(self, x: Dlist[float], y: Dlist[float]):
        self.points = []
        for i in range(len(x)):
            self.points.append(Point(x[i + 1], y[i + 1]))

    def __repr__(self):
        return f"D<Polygon with {len(self.points)} points>"

    # get desmos LaTeX formula
    def __str__(self):
        points: list[str] = [repr(point) for point in self.points]
        latex: str = f"\\left[{', '.join(points)}\\right]"
        return latex

    def __len__(self):
        return len(points)

# tests
if __name__ == "__main__":
    import sys

    logging.basicConfig(stream=sys.stdout, format="%(levelname)s - %(module)s: %(message)s")
    logging.addLevelName(5, "VERBOSE")
    logging.addLevelName(9, "TEST")

    TEST: int = 9

    logger = logging.getLogger("")
    logger.setLevel(TEST)

    logger.log(5, "LOGGER STARTED")

    ########################
    # Desmos emulation tests
    ########################

    point: Point = Point(1,1)
    logger.log(TEST, f"repr: {repr(point)}\n\tstr: {str(point)}")

    assert point.x == 1
    assert point.y == 1
    assert str(point) == "\\left(1, 1\\right)"

    points: Dlist[float] = Dlist((1,2,3,4))
    polygon: Polygon = Polygon(points, points)

    logger.log(TEST, f"repr: {repr(polygon)}\n\tstr: {str(polygon)}")

    assert len(polygon) == 4
    assert polygon.points[2].x == 3
    assert str(polygon) == "\\left[D(1, 1), D(2, 2), D(3, 3), D(4, 4)\\right]"