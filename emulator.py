from classes import Dasm, Point, Polygon


# load code
with open("o.txt", "r") as CODE:
    code: str = CODE.read()

code = code.replace(r"\left[", "").replace(r"\right]", "")

code: list[float] = [float(e.strip()) for e in code.split(",")]

print(code)

# begin emulator

code: list[float]
stack: list[float] = []
pointer = 0
stacklen: int = 0

Pbuffer: list[float] = []
vertx: list[float]
verty: list[float]
poly: Polygon
polyStack: list[Polygon] = []

rx: float = 0
ry: float = 0

# updates
def _update_stack():
    global stacklen
    stacklen = len(stack)

# stack functions
def push(v: float):
    global stacklen
    stack.append(v)
    _update_stack()

def poprx():
    global rx
    rx = stack.pop()
    _update_stack()

def popry():
    global ry
    ry = stack.pop()
    _update_stack()

def popnull():
    stack.pop()
    _update_stack()

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
    if stack[stacklen] == 0:
        popnull()
        pointer = stack[stacklen] + 2