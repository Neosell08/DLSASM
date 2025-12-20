from DAPINSTR import *
lines = []

with open("dap.dap", "r") as f:
    lines = f.readlines()
    for i in range(len(lines)):
        if (lines[i][0].isalpha()):
            lines[i] = lines[i].removesuffix("\n")


funcs = []
consts = {}
varbs = []

    
def HasVar(var: str) -> Variable:
    for varb in varbs:
        if varb.kword == var:
            return varb
    return None

def HandleParam(arg: str):
    if arg.isnumeric():
        return int(arg)
    elif (arg.startswith("\"") and arg.endswith("\"")):
        return arg.strip("\"")
    elif (arg in consts):
        return consts[arg]
    elif HasVar(arg) != None:
        return HasVar(arg)
    elif arg.startswith("&") and HasVar(arg.removeprefix("&")):
        return HasVar(arg.removeprefix("&")).addr
    else: return None
def Allocate(args: list):
    lines = []
    def FindFreeAddr():
        unfreeaddr = []
        for var in varbs:
            unfreeaddr.append(var.addr)
        for i in range(len(unfreeaddr)+1):
            if not i in unfreeaddr:
                return i
    
    varbs.append(Variable(args[0], FindFreeAddr()))
    lines.append("IMM " + str(args[1]))
    lines.append(f"MOV RM{varbs[len(varbs)-1]} REG0")
    return lines

    

removedlines = 0
i = 0
isInFunc = False
#check for pre-compile things
while i - removedlines < len(lines):
    curi = i - removedlines
    line = lines[curi]
    curFuncArea = [0, 0]
    curFuncName = ""
    if line == "\n":
        lines.pop(curi)
        removedlines += 1
    elif line.startswith("func") and not isInFunc:
        removedlines += 1
        lines.pop(curi)
        curFuncArea[0] = curi
        curFuncName = line.split(" ")[1].removesuffix(":")
        isInFunc = True
        print(curFuncName)

    elif line.startswith("endfunc") and isInFunc:
        removedlines += 1
        lines.pop(curi)
        curFuncArea[1] = curi
        isInFunc = False
        funcs.append(Function(curFuncName, curFuncArea.copy()))
        curFuncArea.clear()

    elif line.startswith("const"):
        removedlines += 1
        lines.pop(curi)
        parts = line.split(" ")
        consts[parts[1]] = HandleParam(parts[2])
    i += 1





INSTRSET = {
    "write":Instruction("write", 1, InterpretWrite),
    "alloc":Instruction("alloc", 2, Allocate),
    "calc":Instruction("calc", 4, InterpretCalculate)}

def InterpretInstruction(line: str, linenum: int):
    argindx = line.index("(")
    instr = line[:argindx]
    args = line.removeprefix(instr).removesuffix(")").removeprefix("(").removesuffix(" ").removesuffix(" ").split(",")
    for i in range(len(args)):
        args[i] = HandleParam(args[i].removeprefix(" "))
    return INSTRSET[instr].call(args, linenum)

def LineLenghtFuncs(index: int) -> int:
    print(index)
    if (index > len(funcs)-1 or index < 0):
        raise KeyError("Index invalid")
    elif (index == 0):
        return 0
    sm = 0
    for i in range(index):
        sm += len(funcs[i])
    return sm
    

funclines = []
for func in funcs:
    for index in range(func.area[0], func.area[1]):
        funclines.append(InterpretInstruction(lines.pop(0), index + removedlines))
        removedlines += 1
linelines = []
for i in range(len(lines)):
    line = lines[i]
    linelines.append(InterpretInstruction(line, i + removedlines))

    
writelines = []
with open("DAPOut.da", "w") as f:
    writelines.append("JMP " + str(LineLenghtFuncs(len(funcs)-1)))
    for func in funclines:
        for line in func:
            writelines.append(line + "\n")
    for line in linelines:
        writelines.append(line + "\n")
    
print(funcs[0].kword)
    

    

