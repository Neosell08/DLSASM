from DAPINSTR import *
from DA import InterpretLines
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
    lines.append(f"MOV RM{varbs[len(varbs)-1].addr} REG0")
    return lines

    

removedlines = 0
i = 0
isInFunc = False
#check for pre-compile things
curFuncName = ""
curFuncArea = [0, 0]
while i - removedlines < len(lines):
    curi = i - removedlines
    line = lines[curi]


    if line == "\n" or line[0] == '#':
        lines.pop(curi)
        removedlines += 1
    elif line.startswith("func") and not isInFunc:
        removedlines += 1
        lines.pop(curi)
        curFuncArea[0] = curi
        curFuncName = line.split(" ")[1].removesuffix(":")
        isInFunc = True

    elif line.startswith("endfunc") and isInFunc:
        removedlines += 1
        lines.pop(curi)
        curFuncArea[1] = curi
        isInFunc = False
        print(curFuncName)
        funcs.append(Function(curFuncName, curFuncArea.copy()))
        curFuncName = ""
        curFuncArea = [0, 0]

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

    if (instr in INSTRSET):
        return INSTRSET[instr].call(args, linenum)
    else:
        for func in funcs:
            
            if func.kword == instr:
                return "JMP " + str(func.realArea[0]+1)

def LineLenghtFuncs(index: int) -> int:
    print(funcs[index].area)
    if (index > len(funcs)-1 or index < 0):
        raise KeyError("Index invalid")
    sm = 0
    for i in range(index+1):
        sm += funcs[i].area[1] - funcs[i].area[0] 
    return sm
    

funclines = []
for func in funcs:
    funcline = []
    for index in range(func.area[0], func.area[1]):
        funcline.extend(InterpretInstruction(lines.pop(0), index + removedlines))
        removedlines += 1
    funclines.append(funcline)
funcleng = 0
for i in range(len(funclines)):
    func = funclines[i]
    funcs[i].realArea = [funcleng, funcleng + len(func)]
    funcleng += len(func)
linelines = []
for i in range(len(lines)):
    line = lines[i]
    linelines.append(InterpretInstruction(line, i + removedlines))

writelines = []
with open("DAPOut.da", "w") as f:
    print(funclines)
    for i in range(len(funclines)):
        func = funclines[i] 
        for line in func:
            writelines.append(line + "\n")
    writelines.insert(0, "JMP " + str(funcleng+1) + "\n")
    for line in linelines:
        
        writelines.append(line + "\n")

str0 = ""
for line in writelines:
    str0 += line
try:
    with open("interm.da", "x") as f:
        f.write(str0)
except FileExistsError:
    with open("interm.da", "w") as f:
        f.write(str0)
print("[Written to DA file]")
code = InterpretLines(writelines)

try:
    with open("Circuits/code", "x") as f:
        f.write(code)
except FileExistsError:
    with open("Circuits/code", "w") as f:
        f.write(code)
print("[Written to file]")

    

