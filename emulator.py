import logging
import sys

from classes import Dasm, Dlist, Point, Polygon

# init logger
logging.basicConfig(stream=sys.stdout, format="%(levelname)s - %(module)s: %(message)s")
logging.addLevelName(5, "VERBOSE")

logger = logging.getLogger("")
logger.setLevel(logging.DEBUG)

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

    logger.debug(f"Push to stack\n\tstack = {stack}")


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
    polygon: Polygon = _poly()
    logger.debug(f"Adding polygon: {polygon.points}")
    polyStack.append(polygon)
    Pbuffer = Dlist()

    # logger.debug(f"Added polygon to stack {repr(polygon)}")


def popPoly():
    global polyStack
    polyStack = polyStack.pop()


# interpereter

def main():
    global rx, ry, acc, pointer, stack
    op = code[pointer]

    logger.log(STATE, f"Op = {op} | pointer = {pointer}\n\tstack = {stack}\n\tlookahead = {code[int(pointer):int(pointer+3)]}")

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
        if stack.pop() == 0:
            pointer += 2
        else:
            jump(code[pointer + 1])

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
        rx = stack[len(stack) - code[pointer + 1] + 1]
        pointer += 2

    elif op == 12:  # mov ry []
        ry = stack[len(stack) - code[pointer + 1] + 1]
        pointer += 2

    elif op == 13:  # call
        call(code[pointer + 1])

        logger.debug(f"invoked call to {pointer}")

    elif op == 14:  # ret
        ret()

    elif op == 15:  # jl
        if stack[len(stack)] < code[pointer + 1]:
            jump(code[pointer + 2])
            stack.pop()
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

        logger.debug(f"poly call\n\tpolyStack = {polyStack}")

    elif op == 24:  # polypop
        polyStack.pop()
        pointer += 1

        logger.debug(f"polypop call\n\tpolyStack = {polyStack}")


# driver
if __name__ == "__main__":
    logging.addLevelName(11,"STATE")
    STATE: int = 11

    logger.setLevel(STATE)

    stats: dict = {
        "max polygons": {
            "count": 0,
            "list": []
        },
        "step count": 0
    }
    max_steps: int = int(1e5)
    step: int = 0
    while pointer <= len(code) and step < max_steps:
        main()
        step += 1

        stats["step count"] = step

        if len(polyStack) > stats["max polygons"]["count"]:
            stats["max polygons"] = {
                "count": len(polyStack),
                "list": polyStack.copy()
            }
            logger.log(STATE, f"STATS: stats")

    if step == max_steps:
        logger.warning(f"emulator stopped after {max_steps} steps")

        # keep track of stats


    logger.info(f"Polygons: {'\n\t'.join([str(poly.points) for poly in polyStack.as_list()])}")
    polygons = f"[{',\n\t'.join([str(p) for p in stats["max polygons"]["list"].as_list()])}]"
    logger.info(f"stats\n\tstep count: {stats["step count"]}\n\tMax polygons: {stats["max polygons"]["count"]}\n\t{polygons}")