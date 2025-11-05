
import pyperclip
import keyboard



MainROM = []
ValueROM = []
Tokens = []
stra = ""
stra.removeprefix

REGISTERS = {"REG0":0, "REG1":1,"REG2":2, "REG3":3}
CALCINSTR = {"ADD":0, "SUB":1, "MUL":2}
def InterpretReadWriteMain(arg: str, r: bool): #interpret where to read and write from on the main bus
    val = [0, 0]
    if r:
        if (arg.upper().startswith("RM")): #read from RAM
            val[0] += 8
            val[1] += int(arg.upper().removeprefix("RM"))<<8
        elif (arg.upper().startswith("SC")): #read to screen
            val[0] += 2
            val[1] += int(arg.upper().removeprefix("SC"))
        else:
            val[0] += REGISTERS[arg.upper()]<<8
    else:       
        if (arg.upper().startswith("RM")): #write to RAM
            val[0] += 12
            val[1] += int(arg.upper().removeprefix("RM"))<<8
        elif (arg.upper().startswith("SC")): #write from screen
            val[0] += 3
            val[1] += int(arg.upper().removeprefix("SC"))
        else:
            val[0] += REGISTERS[arg.upper()]<<4
    return val
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
    return [0<<12, val]
def InterpretMOV(args): #Move from one memory location to another 
    val = [1<<12, 0]
    write = InterpretReadWriteMain(args[0], False)
    val[0] += write[0]
    val[1] += write[1]
    read = InterpretReadWriteMain(args[1], True)
    val[0] += read[0]
    val[1] += read[1]
    return val
def InterpretCAL(args): #Calculate and move into REG0
    return [(2<<12) + (REGISTERS[args[0].upper()]<<8) + (REGISTERS[args[1].upper()]<<4) + CALCINSTR[args[2].upper()], 0]
def InterpretRSSC(): #Reset Screen
    return [3<<12, 0]
def InterpretJMP(args): #Jump to line
    return [4<<12, int(args[0])]
def InterpretWRT(args): #Draw to Screen
    val = [(5<<12) + (REGISTERS[args[1]]<<4), 0]
    read = InterpretReadWriteMain(args[0], True)
    val[0] += read[0]
    val[1] += read[1]
    return val
def InterpretRFSC(args): #Refresh Screen
    return [(3<<12) + (8<<8), 0]

    


with open("test.dasm") as f:
    lines = f.readlines()
    for line in lines:
        line = line.removesuffix("\n").upper().split(" ")
        val = []
        if line[0] == "IMM": #Immediately write a 16 bit value to register 0 Ex: IMM 64
            val = InterpretIMM(line[1:])
        elif line[0] == "MOV": #Move a value from one location to another Ex: MOV REG0(to) RM22(from)
            val = InterpretMOV(line[1:])
        elif line[0] == "CAL": #Do a calculation using the ALU Ex: CAL REG0 REG1 SUB
            val = InterpretCAL(line[1:])
        elif line[0] == "RSSC": #Reset the screen Ex: RSSC
            val = InterpretRSSC()
        elif line[0] == "JMP": #Jump from one instruction to another Ex: JMP 0
            val = InterpretJMP(line[1:])
        elif line[0] == "WRT": #Write to the console Ex: WRT REG0(addr: only registers) RAM0(color)
            val = InterpretWRT(line[1:])
        elif line[0] == "RFSC": #Refresh the console screen(doesnt work) Ex: RFSC
            val = InterpretRFSC(line[1:])
        
        MainROM.append(val[0])
        ValueROM.append(val[1])


str0 = ""


for i in range(0, len(MainROM)):
   str0 += str(MainROM[i] + (ValueROM[i] << 16)) + " "
try:
    with open("Circuits/code", "x") as f:
        f.write("v2.0 raw\n" + str0)
except FileExistsError:
    with open("Circuits/code", "w") as f:
        f.write("v2.0 raw\n" + str0)
