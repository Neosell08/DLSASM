import sympy


class Instruction:
    def __init__(self, keyword: str, params: int, func):
        self.keyword = keyword
        self.params = params
        self.func = func
        
    def call(self, args: list, linenum) -> list:
        print(args)
        if (len(args) != self.params):
            raise ValueError("Not enough paramaters in function: " + self.keyword + " at line " + str(linenum) + ". " + str(len(args)) + " given.\nArgs: " + str(args))
        return self.func(args)
    
class Function:
    def __init__(self, kword, code, ifvar = None):
        self.kword = kword
        self.code = code
        self.realArea = []
        self.ifvar = ifvar
    def __str__(self):
        return self.kword + str(self.code)
class Variable:
    def __init__(self, kword, addr):
        self.kword = kword
        self.addr = addr
    def __str__(self):
        return f"{self.kword}: {self.addr}"

def GetVar(varbs: list, key:str) -> Variable:
    for var in varbs:
        if var.kword == key:
            return var
        
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
    elif type(x) == str:
        if len(x) == 1:
            return [f"IMM {ord(x[0])}", f"MOV {pos} REG0"]
        else:
            raise Exception("string too long to write")
    else:
        raise Exception(f"Cannot write value {x} to position {pos}")
       
        

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

def InterpretCalculate(args): #arg0: variable to store result into, arg1: number 1, arg2: number 2, arg3; operation
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
def InterpretReturn(args):
    return ["RET"]
def InterpretInput(args):
    lines = []
    lines.append("IMM 0")
    lines.append("MOV REG2 REG0")
    lines.append("MOV REG1 KBOARD")
    lines.append("CAL REG1 REG2 EQ")
    lines.append("JMI -4 REG0")
    lines.append("WRT REG1")
    lines.append("IMM 10")
    lines.append("WRT REG0")
    lines.append(f"MOV RM{args[0].addr} REG1")
    return lines
def HandleFunction(sublist: list, funcname:str, ifstatements:int, variables: list, ifvar:Variable = None):
    funclines = []
    removedlines = 0
    lineleng = 0
    curlines = [funcname, ifvar]
    for i in range(len(sublist)):
        i = i - removedlines
        if (i >= len(sublist)):
            break
        print(sublist)
        line = sublist[i]
        lineleng+=1
        if line.startswith("#") or line == "\n":
            sublist.pop(i)
            removedlines += 1
            continue
        elif (line.startswith("func")):
            funcsfound, lines = HandleFunction(sublist[i+1:], line.split(" ")[1].removesuffix(":"), ifstatements)
            sublist = sublist[:i+1]
            sublist.extend(lines)
            rem = funcsfound.pop(0)
            lineleng += rem
            removedlines += rem
            for func in funcsfound:
                if (func[0].startswith("if ")):
                    ifstatements += 1
            funclines.extend(funcsfound)
            
        if line.startswith("if"):
            name = f"if{ifstatements}"
            ifvar2 = GetVar(variables, line.split(" ")[1].removesuffix(":"))
            funcsfound, lines = HandleFunction(sublist[i+1:], name, ifstatements, variables, ifvar2)
            sublist = sublist[:i+1]
            sublist.extend(lines)
            rem = funcsfound.pop(0)
            ifstatements = funcsfound.pop(0)
            lineleng += rem
            removedlines += rem
            
            funclines.extend(funcsfound)
            curlines.append(f"if{ifstatements}()")
            ifstatements += 1

        elif line.startswith("endfunc") or line.startswith("endif"):
            sublist = sublist[i+1:]
            break
        else:
            curlines.append(line)
    funclines.insert(0, curlines)
    funclines.insert(0, ifstatements)
    funclines.insert(0, lineleng)
    return funclines, sublist


