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
    if type(args[0]) == Variable:
        hasvarb = True
        foundvarb = args[0]
    else:
        for varb in varbs:
            if (varb.kword == args[0]):
                hasvarb = True
                foundvarb = varb
                break
    

    writeval = ""
    if type(args[1]) == str:
        if len(args[1]) != 1:
            raise Exception("Invalid allocation parameter")
        else:
            writeval = str(ord(args[1][0]))
    else:
        writeval = str(args[1])
    if (hasvarb):
        lines.append("IMM " + writeval)
        lines.append(f"MOV RM{foundvarb.addr} REG0")
    else:
        varbs.append(Variable(args[0], FindFreeAddr()))
        lines.append("IMM " + writeval)
        lines.append(f"MOV RM{varbs[len(varbs)-1].addr} REG0")
    return lines

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
        args = line.removeprefix(instr).removesuffix(" ").removesuffix(")").removeprefix("(").removesuffix(" ").removeprefix(" ").split(",")
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
                            f"JMP {func.realarea[0]+1}"]
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
ifvars = []

def ParsePreCompLine(line: str, env: list) -> tuple: 
    global funcs
    global varbs
    global ifvars
    global consts
    if line == "\n" or line[0] == '#':
        return None, env
    elif line.startswith("func"):
        parts = line.split(" ")
        env.append(parts[1].removesuffix(":"))
        return None, env
    elif line.startswith("if"):
        parts = line.split(" ")
        ifstr = "if" + str(len(ifvars))
        
        env.append(ifstr)
        ifvars.append(GetVar(parts[1].removesuffix(":")))
        return ifstr + "()", env
    elif line.startswith("endif") or line.startswith("endfunc"):
        env.pop(len(env)-1)
        return None, env
    elif line.startswith("def"):
        varbs.append(Variable(line.split(" ")[1], FindFreeAddr()))
        return None, env
    elif line.startswith("const"):
        parts = line.split(" ")
        consts[parts[1]] = HandleParam(parts[2])
        return None, env
    else:
        return line, env


 
funclines = []
removedlines = 0
i = 0
enviroment = []
enviromentlines = []
curfunc = None
lastleng = 0

#check for pre-compile things
while i < len(lines):
    line = lines[i]
    if line.startswith("import"):
        importlines = []
        lines.pop(i)
        with open(f"{line.split(" ")[1]}.neo", "r") as f:
            importlines = f.readlines()
            importlines.reverse()
        for l in importlines:
            lines.insert(i, l.removesuffix("\n"))
        print(f"[Imported {line.split(" ")[1]}.neo]")
        
        continue
    line, enviroment = ParsePreCompLine(line, enviroment)
    if curfunc == None:
        if line != None:
            lines[i] = line
        else:
            lines.pop(i)
            removedlines += 1
            i -= 1
        
        if (len(enviroment) > 0):
            curfunc = enviroment[0]
            enviromentlines.append([])
            lastleng = 1
        i+=1
    else:
        lines.pop(i)
        lastindex = len(enviromentlines)-1
        if line != None:
            enviromentlines[lastindex].append(line)
       
        if len(enviroment) > lastleng:
            curfunc = enviroment[lastindex+1]
            enviromentlines.append([])

        elif len(enviroment) < lastleng:
            funccode = enviromentlines.pop(lastindex)
            ifvar = ifvars[int(curfunc.lower().removeprefix("if"))] if curfunc.startswith("if") else None
            funcs.append(Function(curfunc, funccode, ifvar))
            if (len(enviroment) > 0): 
                curfunc = enviroment[lastindex-1]
            else:
                curfunc = None
        lastleng = len(enviroment)

#end of checking for pre compile things

curremoved = 0
funcleng = 0
for i in range(len(funcs)):
    funcline = []
    func = funcs[i]
    func.realarea = [funcleng]
    isif = func.ifvar != None
    for line in func.code:
        funcline.extend(InterpretInstruction(line, -1))
        removedlines += 1
        curremoved += 1
    if (isif):
        funcline.insert(0, f"MOV REG1 RM{func.ifvar.addr}")
        funcline.insert(1, f"JMI +2 REG1")
        funcline.insert(2, "RET")
    funcline.append("RET")
    funcleng += len(funcline)
    func.realarea.append(funcleng)
    funclines.append(funcline)

linelines = []

for i in range(len(lines)):
    line = lines[i]
    ret = []
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

    

