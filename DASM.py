
import pyperclip
import keyboard



MainROM = []
ValueROM = []
Tokens = []


class Instruction:
    def __init__(self, keyword: str, params: int, func):
        self.keyword = keyword
        self.params = params
        self.func = func
    def call(self, args: list, linenum):
        if (len(args) != self.params):
            raise ValueError("Not enough paramaters in function: " + self.keyword + " at line " + str(linenum) + ". " + str(len(args)) + " given.\nArgs: " + str(args))
        return self.func(args)
        


REGISTERS = {"REG0":0, "REG1":1,"REG2":2, "REG3":3, "KBOARD":4, "RNDM":5}
CALCINSTR = {"ADD":0, "SUB":1, "MUL":2}



def InterpretReadWriteMain(arg: str, r: bool): #interpret where to read and write from on the main bus
    val = [0, 0]

    if r:
        if (arg.upper().startswith("RM")): #read from RAM
            val[0] += 32
            val[1] += int(arg.upper().removeprefix("RM"))<<8
        elif (arg.upper().startswith("SC")): #read to screen
            val[0] += 2
            val[1] += int(arg.upper().removeprefix("SC"))
        else:
            val[1] += REGISTERS[arg.upper()]
    else:       
        if (arg.upper().startswith("RM")): #write to RAM
            val[0] += 16
            val[1] += int(arg.upper().removeprefix("RM"))<<8
        elif (arg.upper().startswith("SC")): #write from screen
            val[0] += 3
            val[1] += int(arg.upper().removeprefix("SC"))
        else:
            
            val[1] += REGISTERS[arg.upper()]
    return val
def reversebits(num: int, bits: int) -> int:
    result = 0
    for i in range(bits):
        if num & (1 << i):
            result |= 1 << (bits - 1 - i)
    return result

def InterpretIMM(args) -> list: #Input the number into REG0
    val = 0
    if (args[0].upper().startswith("RGB")): #example RGB255/255/255
        rgb = args[0].upper().removeprefix("RGB").split("/")
        val = (round(15*int(rgb[0])/255.0)<<8) + (round(15*int(rgb[1])/255.0)<<4) + round(15*int(rgb[2])/255.0)
    elif (args[0].upper().startswith("HEX")):
        s = args[0].upper().removeprefix("HEX")
        rgb = [s[i:i+2] for i in range(0, len(s), 2)]
        val = (round(15*int(rgb[0], 16)/255.0)<<8) + (round(15*int(rgb[1], 16)/255.0)<<4) + round(15*int(rgb[2], 16)/255.0)
    else:
        val = int(args[0])
    return [0, val]
def InterpretMOV(args): #Move from one memory location to another 
    val = [1, 0]
    write = InterpretReadWriteMain(args[0], False)
    val[0] += write[0]
    val[1] += write[1]
   
    read = InterpretReadWriteMain(args[1], True)
    val[0] += read[0]
    val[1] += read[1]
    
    return val
def InterpretCAL(args): #Calculate and move into REG0. First arg is A second is B
    
    return [2 + (REGISTERS[args[1].upper()]<<12) + (CALCINSTR[args[2].upper()]<<4), (REGISTERS[args[0].upper()]<<4)]
def InterpretRSSC(args): #Reset Screen
    return [5, 0]
def InterpretJMP(args): #Jump to line
    print((int(args[0])|48))
    return [3 + ((int(args[0])&48)>>4), int(args[0])&15]
def InterpretJMI(args):
    return [6  + + ((int(args[0])&48)>>12) + (REGISTERS[args[1]]<<12), int(args[0])&15]
def InterpretWRT(args): #Draw to Screen ex: WRT 
    val = [(4) + (REGISTERS[args[0]]<<12), 0]
    return val
def InterpretRFSC(args): #Refresh Screen
    return [(3) + (8<<8), 0]

INSTRSET = {"IMM":Instruction("IMM", 1, InterpretIMM), "MOV":Instruction("MOV", 2, InterpretMOV), "CAL":Instruction("CAL", 3, InterpretCAL), "RSSC":Instruction("RSSC", 0, InterpretRSSC), "JMP":Instruction("JMP", 1, InterpretJMP), "WRT":Instruction("WRT", 1, InterpretWRT), "JMI":Instruction("JMI", 2, InterpretJMI)}


with open("test.dasm") as f:
    lines = f.readlines()
    for index in range(len(lines)):
        line = lines[index].removesuffix("\n").upper().split(" ")
        val = INSTRSET[line[0].upper()].call(line[1:], index) #line[0] = instr, line[1:] = args
        MainROM.append(val[0])
        ValueROM.append(val[1])


str0 = ""

for i in range(0, len(MainROM)):
    
   str0 += str(format(MainROM[i] + (ValueROM[i] << 16), f'0{8}x')) + " "
try:
    with open("Circuits/code", "x") as f:
        f.write("v2.0 raw\n" + str0)
except FileExistsError:
    with open("Circuits/code", "w") as f:
        f.write("v2.0 raw\n" + str0)
