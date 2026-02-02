from NEOINSTR import *
from DA import InterpretLines
lines = []
FILENAME = "neo.neo"


with open(FILENAME, "r") as f:
    lines = f.readlines()
    for i in range(len(lines)):
        if (lines[i][0].isalpha()):
            lines[i] = lines[i].removesuffix("\n")

print(f"[Read from {FILENAME}]")
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
def FindFreeAddr():
        unfreeaddr = []
        for var in varbs:
            unfreeaddr.append(var.addr)
        for i in range(len(unfreeaddr)+1):
            if not i in unfreeaddr:
                return i
def Allocate(args: list):
    lines = []
    
    hasvarb = False
    foundvarb = None
    for varb in varbs:
        if (varb.kword == parts[1]):
            hasvarb = True
            foundvarb = varb
            break
    if (hasvarb):
        lines.append("IMM " + str(args[1]))
        lines.append(f"MOV RM{foundvarb.addr} REG0")
    else:
        varbs.append(Variable(args[0], FindFreeAddr()))
        lines.append("IMM " + str(args[1]))
        lines.append(f"MOV RM{varbs[len(varbs)-1].addr} REG0")
    return lines

funclines = []
removedlines = 0
i = 0
isInFunc = False
isInIf = False
#check for pre-compile things
curFuncName = ""
ifstatements = 0
curFuncArea = [0, 0]
while i - removedlines < len(lines):
    curi = i - removedlines
    line = lines[curi]
    if line == "\n" or line[0] == '#': #if is empty line or comment
        lines.pop(curi)
        removedlines += 1
    elif (line.startswith("func") or line.startswith("if")) and not isInFunc: #if the start of a function
        if (line.startswith("func")):
            removedlines += 1
            lines.pop(curi)
        else:
            
            lines[curi] = lines[curi][:2] + str(ifstatements) + lines[curi][2:]
            isInIf =True
        curFuncArea[0] = curi
        curFuncName = ""
        if (line.startswith("func")):
            curFuncName = line.split(" ")[1].removesuffix(":")
        else:
            curFuncName = f"if{ifstatements}"
        isInFunc = True
        

    elif (line.startswith("endfunc") or line.startswith("endif")) and isInFunc: #if the end of a function
        removedlines += 1
        lines.pop(curi)
        curFuncArea[1] = curi
        if (isInIf):
            curFuncArea[0] +=1
            funcs.insert(ifstatements, Function(curFuncName, curFuncArea.copy()))
        else:
            funcs.append(Function(curFuncName, curFuncArea.copy()))
        isInFunc = False
        isInIf = False
        curFuncName = ""
        curFuncArea = [0, 0]
        ifstatements +=1
    elif line.startswith("const"): #if defining a constant
        removedlines += 1
        lines.pop(curi)
        parts = line.split(" ")
        consts[parts[1]] = HandleParam(parts[2])
    elif line.startswith("def"): #if defining a variable pre interpret
        removedlines += 1
        lines.pop(curi)
        parts = line.split(" ")
        hasvarb = False
        for varb in varbs:
            if (varb.kword == parts[1]):
                hasvarb = True
                break
        if (not hasvarb):
            varbs.append(Variable(parts[1], FindFreeAddr()))
        
    i += 1


#end of checking for pre compile things

INSTRSET = {
    "write":Instruction("write", 1, InterpretWrite),
    "alloc":Instruction("alloc", 2, Allocate),
    "calc":Instruction("calc", 4, InterpretCalculate),
    "ptrval":Instruction("ptrval", 3, InterpretPtrVal),
    "chrinput":Instruction("input", 1, InterpretInput),
    "return":Instruction("return", 0, InterpretReturn)}

def InterpretInstruction(line: str, linenum: int): #args: line string and index of line
    try:
        argindx = line.index("(")
        instr = line[:argindx]
        args = line.removeprefix(instr).removesuffix(")").removeprefix("(").removesuffix(" ").removesuffix(" ").split(",")
        argstoremove = []
        for i in range(len(args)):
            arg = HandleParam(args[i].removeprefix(" "))
            if (arg != None and arg != ""):
                args[i] = arg
            else:
                argstoremove.append(i)

        for i in range(len(argstoremove)):
            args.pop(argstoremove[i])
        if (instr in INSTRSET):
            ret = INSTRSET[instr].call(args, linenum)
            return ret
        else:
            for func in funcs:
                
                if func.kword == instr:
                    
                    return [f"CALL",
                            f"JMP {func.realArea[0]+1}"]
            assert(1==0)
    except Exception as e:
        print(e)
        raise ValueError(f"Error on line {linenum},\n{line}")
def LineLenghtFuncs(index: int) -> int:
    if (index > len(funcs)-1 or index < 0):
        raise KeyError("Index invalid")
    sm = 0
    for i in range(index+1):
        sm += funcs[i].area[1] - funcs[i].area[0] 
    return sm
def GetVar(key:str) -> Variable:
    global varbs
    for var in varbs:
        if var.kword == key:
            return var
def GetFunc(key:str) -> Function:
    global funcs
    for f in funcs:
        if f.kword == key:
            return f
    

curremoved = 0
for i in range(len(funcs)):
    funcline = []
    func = funcs[i]
    
    
    for index in range(func.area[0], func.area[1]):
        print(lines[index-curremoved])
        funcline.extend(InterpretInstruction(lines.pop(index-curremoved), index + removedlines))
        removedlines += 1
        curremoved += 1
    
    funcline.append("RET")
    funclines.append(funcline)

# #making the integer input function
# intinpfunc = []
# intinpfunc.append("MOV REG1 KBOARD")
# intinpfunc.append("WRT REG1")
# intinpfunc.append("IMM 10")
# intinpfunc.append("MOV REG2 REG0")
# intinpfunc.append("CAL REG1 REG2 EQ")
# intinpfunc.append("MOV REG2 REG0")
# intinpfunc.append("CAL REG2 REG1 NOT") 
# intinpfunc.append("JMI 2+ REG0")#check if there is a newline then finish
# intinpfunc.append("RET")
# intinpfunc.append("MOA 0 REG2 REG3")
# intinpfunc.append("MOA 1 REG3 REG1")
# intinpfunc.append("IMM 10")
# intinpfunc.append("MOV REG1 REG0")
# intinpfunc.append("CAL REG1 REG2 MUL")
# intinpfunc.append("MOV REG2 REG0")
# intinpfunc.append("MOA 0 REG1 REG3")
# intinpfunc.append("CAL REG1 REG2 ADD")
# intinpfunc.append("MOA 1 REG3 REG0")
# intinpfunc.append("JMP 1")




funcleng = 0

for i in range(len(funclines)):
    func = funclines[i]
    funcs[i].realArea = [funcleng, funcleng + len(func)] #the size of the function in DA code
    funcleng += len(func)
linelines = []
for i in range(len(lines)):
    line = lines[i]
    ret = []
    if (line.startswith("if")):
        parts = line.split(" ")
        ret = InterpretInstruction(parts[0] +"()", i + removedlines) 
        retleng = len(ret)
        ret.insert(0, f"MOV REG1 RM{GetVar(parts[1].removesuffix(":")).addr}")
        ret.insert(1, f"CAL REG1 REG2 NOT")
        ret.insert(2, f"JMI +{retleng+1} REG0")
    else:
        ret = InterpretInstruction(line, i + removedlines) 
    assert(ret != None)
    linelines.append(ret)

writelines = []
with open("NEOOut.da", "w") as f:
    for i in range(len(funclines)):
        func = funclines[i] 
        for line in func:
            writelines.append(line + "\n")
    writelines.insert(0, "JMP " + str(funcleng+1) + "\n")
    for NEOLine in linelines:
        for line in NEOLine:
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

    

