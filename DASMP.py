lines = []

with open("dap.dasmp", "r") as f:
    lines = f.readlines()
    for i in range(len(lines)):
        lines[i] = lines[i].removesuffix("\n")

class Instruction:
    def __init__(self, keyword: str, params: int, func):
        self.keyword = keyword
        self.params = params
        self.func = func
    def call(self, args: list, linenum):
        if (len(args) != self.params):
            raise ValueError("Not enough paramaters in function: " + self.keyword + " at line " + str(linenum) + ". " + str(len(args)) + " given.\nArgs: " + str(args))
        return self.func(args)

def InterpretWrite(args):
    lines = []
    for c in args[0]:
        lines.append("IMM " + str(ord(c)))
        lines.append("WRT REG0")
    
    

INSTRSET = {"write":Instruction("write", 1, InterpretWrite)}