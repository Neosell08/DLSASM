import sympy


class Instruction:
    def __init__(self, keyword: str, params: int, func):
        self.keyword = keyword
        self.params = params
        self.func = func
        
    def call(self, args: list, linenum) -> list:
        if (len(args) != self.params):
            raise ValueError("Not enough paramaters in function: " + self.keyword + " at line " + str(linenum) + ". " + str(len(args)) + " given.\nArgs: " + str(args))
        return self.func(args)
class Function:
    def __init__(self, kword, area):
        self.kword = kword
        self.area = area
        self.realArea = []
class Variable:
    def __init__(self, kword, addr):
        self.kword = kword
        self.addr = addr
def WriteToPos(pos: str, x) -> list: 
    if type(x) == Variable:
        if (pos.startswith("RM")):
            return [f"MOV REG0 RM{x.addr}", f"MOV {pos} REG0"]
        else:
            return [f"MOV {pos} RM{x.addr}"]
    elif type(x) == int:
        if (pos != "REG0"):
            return [f"IMM {x}", f"MOV {pos} REG0"]
        else:
            return [f"IMM {x}"]
        

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
    lines.extend(WriteToPos("REG1", args[1]))
    lines.extend(WriteToPos("REG2", args[2]))
    lines.append("CAL REG1 REG2 " + args[3])
    lines.append(f"MOV RM{args[0].addr} REG0")
    return lines
def InterpretPtrVal(args): #arg0 = var to write/read from, arg1 = ram adress, arg2 = "r" or "w"
    lines = []
    if type(args[1]) == int:
        lines.append(f"IMM {args[1]}")
        lines.append(f"MOV REG1 REG0")
    elif type(args[1]) == Variable:
        lines.append(f"MOV REG1 RM{args[1].addr}")
    
    if (args[2] == "r"):
        lines.append("MOA 0 REG0 REG1")
        lines.append(f"MOV RM{args[0].addr} REG0")
    else:
        lines.append(f"MOV REG0 RM{args[0].addr}")
        lines.append("MOA 1 REG1 REG0")
    return lines



