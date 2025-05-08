import logging
import sys

from classes import Dasm, Dlist, Point, Polygon

# init logger
logging.basicConfig(stream=sys.stdout, format="%(levelname)s - %(module)s: %(message)s")
logging.addLevelName(5, "VERBOSE")

logger = logging.getLogger("")
logger.setLevel(logging.INFO)

logger.log(5, "LOGGER STARTED")

# load code
with open("o.txt", "r") as CODE:
    code: str = CODE.read()

code = code.replace(r"\left[", "").replace(r"\right]", "")

code: list[float] = [float(e.strip()) for e in code.split(",")]

logger.info(f"Loaded code: {code}")

# begin emulator

code: Dlist[float] = Dlist(code)
stack: Dlist[float] = Dlist()
pointer = 1

Pbuffer: Dlist[float] = Dlist()
vertx: Dlist[float]
verty: Dlist[float]
poly: Polygon
polyStack: Dlist[Polygon] = Dlist()

rx: float = 0
ry: float = 0
acc: float = 0

# dynamic values
def vertx() -> Dlist[float]:
    return Pbuffer[1::2]

def verty() -> Dlist[float]:
    return Pbuffer[2::2]

def _poly() -> Polygon:
    return Polygon(vertx(), verty())

# stack functions
def push(v: float):
    stack.append(v)

def poprx():
    global rx
    rx = stack.pop()

def popry():
    global ry
    ry = stack.pop()

def popnull():
    stack.pop()

# utility functions
def jump(jumpPointer: float):
    global pointer
    if jumpPointer < 1:
        pointer = 1
    else:
        pointer = jumpPointer

def call(callPointer: float):
    global pointer
    stack.extend((pointer, 0))
    pointer = callPointer

def ret():
    global pointer
    if stack[len(stack)] == 0:
        popnull()
        pointer = stack[len(stack)] + 2
    else:
        popnull()

def polyPush(value: float):
    Pbuffer.append(value)

def poly():
    global Pbuffer
    polyStack.append(_poly())
    Pbuffer = Dlist()

def popPoly():
    global polyStack
    polyStack = polyStack.pop()

# interpereter

def main():
    global rx, ry, acc, pointer, stack
    op = code[pointer]

    if op == 0:  # ld rx
        rx = code[pointer + 1]
        pointer += 2

    elif op == 1:  # ld ry
        ry = code[pointer + 1]
        pointer += 2

    elif op == 2:  # mov rx acc
        rx = acc
        pointer += 1

    elif op == 3:  # add
        acc = rx + ry
        pointer += 1

    elif op == 4:  # jnz
        if stack[len(stack)] == 0:
            pointer += 2
        else:
            jump(code[pointer + 1])\

    elif op == 5:  # push rx
        push(rx)
        pointer += 1

    elif op == 6:  # push ry
        push(ry)
        pointer += 1

    elif op == 7:  # pop rx
        poprx()
        pointer += 1

    elif op == 8:  # pop ry
        popry()
        pointer += 1

    elif op == 9:  # dec rx
        rx -= 1
        pointer += 1

    elif op == 10:  # dec ry
        ry -= 1
        pointer += 1

    elif op == 11:  # mov rx []
        rx = stack[len(stack) - code[pointer + 1]]
        pointer += 2

    elif op == 12:  # mov ry []
        ry = stack[len(stack) - code[pointer + 1]]
        pointer += 2

    elif op == 13:  # call
        call(code[pointer + 1])

    elif op == 14:  # ret
        ret()

    elif op == 15:  # jl
        if stack[len(stack)] < code[pointer + 1]:
            jump(code[pointer + 2])
        else:
            pointer += 3

    elif op == 16:  # mult
        acc = rx * ry
        pointer += 1

    elif op == 17:  # neg
        rx = -rx
        pointer += 1

    elif op == 18:  # inv
        rx = 1 / rx
        pointer += 1

    elif op == 19:  # pop
        popnull()
        pointer += 1

    elif op == 20:  # mov rx ^
        rx = code[code[pointer + 1]]
        pointer += 2

    elif op == 21:  # mov rx ^ry
        rx = code[ry]
        pointer += 1

    elif op == 22:  # ppush rx
        polyPush(rx)
        pointer += 1

    elif op == 23:  # poly
        poly()
        pointer += 1

    elif op == 24:  # polypop
        raise NotImplementedError()

# driver
if __name__ == "__main__":
    while pointer <= len(code):
        main()

    logger.info(f"Polygons: {polyStack}")