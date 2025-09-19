
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
def InterpretIMM(args) -> list:
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
def InterpretMOV(args):
    val = [1<<12, 0]
    write = InterpretReadWriteMain(args[0], False)
    val[0] += write[0]
    val[1] += write[1]
    read = InterpretReadWriteMain(args[1], True)
    val[0] += read[0]
    val[1] += read[1]
    return val
def InterpretCAL(args):
    return [(2<<12) + (REGISTERS[args[0].upper()]<<8) + (REGISTERS[args[1].upper()]<<4) + CALCINSTR[args[2].upper()], 0]
def InterpretRSC():
    return [3<<12, 0]
def InterpretJMP(args):
    return [4<<12, int(args[0])]
def InterpretDRW(args):
    val = [(5<<12) + (REGISTERS[args[1]]<<4), 0]
    read = InterpretReadWriteMain(args[0], True)
    val[0] += read[0]
    val[1] += read[1]
    return val
    


with open("test.dasm") as f:
    lines = f.readlines()
    for line in lines:
        line = line.removesuffix("\n").upper().split(" ")
        val = []
        if line[0] == "IMM": #Ex: IMM 64
            val = InterpretIMM(line[1:])
        elif line[0] == "MOV": #Ex: MOV REG0(to) RM22(from)
            val = InterpretMOV(line[1:])
        elif line[0] == "CAL": #Ex: CAL REG0 REG1 SUB
            val = InterpretCAL(line[1:])
        elif line[0] == "RSC": #Ex: RSC
            val = InterpretRSC()
        elif line[0] == "JMP": #Ex: JMP 0
            val = InterpretJMP(line[1:])
        elif line[0] == "DRW": #Ex: DRW REG0(addr: only registers) RAM0(color)
            val = InterpretDRW(line[1:])
        
        MainROM.append(val[0])
        ValueROM.append(val[1])


str0 = ""


for i in range(0, 256):
    if (i < len(MainROM)):
        str0 += format(MainROM[i], '16b') + "\n"
    else:
        str0+="0000000000000000\n"
str1 = ""
for i in range(0, 256):
    if (i < len(ValueROM)):
        str1 += format(ValueROM[i], '16b')  + "\n"
    else:
        str1+="0000000000000000\n"

pyperclip.copy(str0)
print("Main ROM copied to clipboard. Press a to continue to Value ROM")
while not keyboard.is_pressed('a'):
    pass
pyperclip.copy(str1)
print("Value ROM copied to clipboard.")
