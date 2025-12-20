import sympy
from sympy.parsing.sympy_parser import parse_expr
from sympy.printing.precedence import PRECEDENCE

class Instruction:
    def __init__(self, keyword: str, params: int, func):
        self.keyword = keyword
        self.params = params
        self.func = func
    def call(self, args: list, linenum):
        if (len(args) != self.params):
            raise ValueError("Not enough paramaters in function: " + self.keyword + " at line " + str(linenum) + ". " + str(len(args)) + " given.\nArgs: " + str(args))
        return self.func(args)
class Function:
    def __init__(self, kword, area):
        self.kword = kword
        self.area = area
class Variable:
    def __init__(self, kword, addr):
        self.kword = kword
        self.addr = addr
def InterpretWrite(args):
    lines = []
    if type(args[0]) == Variable:
        lines.append(f"MOV REG0 RM{args[0].addr}")
        lines.append("WRT REG0")
    else:
        for c in args[0]:
            lines.append("IMM " + str(ord(c)))
            lines.append("WRT REG0")
    return lines

def InterpretCalculate(args):
    lines = []

    lines.append("IMM " + str(args[1]))
    lines.append("MOV REG1 REG0")
    lines.append("IMM " + str(args[2]))
    lines.append("MOV REG2 REG0")
    lines.append("CAL REG1 REG2 " + args[3])
    lines.append("MOV RM" + str(args[0].addr) + " REG0")
