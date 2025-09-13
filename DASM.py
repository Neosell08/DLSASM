
import pyperclip
import keyboard



MainROM = []
ValueROM = []
Tokens = []
stra = ""
stra.removeprefix

REGISTERS = {"REG0":0, "REG1":1,"REG2":2, "REG3":3}
CALCINSTR = {"ADD":0, "SUB":1, "MUL":2}

def InterpretIMM(args) -> list:
    val = 0
    if (args[0].upper().startswith("RGB")): #example RGB255/255/255
        rgb = args[0].upper().removeprefix("RGB").split("/")
        val = (round(15*rgb[0]/255.0)<<8) + (round(15*rgb[1]/255.0)<<4) + round(15*rgb[2]/255.0)
    elif (args[0].upper().startswith("HEX")):
        s = args[0].upper().removeprefix("HEX")
        rgb = [s[i:i+2] for i in range(0, len(s), 2)]
        val = (round(15*int(rgb[0], 16)/255.0)<<8) + (round(15*int(rgb[1], 16)/255.0)<<4) + round(15*int(rgb[2], 16)/255.0)
    else:
        val = int(args[0])
    return [0, val]
def InterpretMOV(args):
    val = [1<<12, 0]
    if (args[0].upper().startswith("RM")): #read from RAM
        val[0] += 8
        val[1] += int(args[0].upper().removeprefix("RM"))<<8
    elif (args[0].upper().startswith("SC")): #read to screen
        val[0] += 2
        val[1] += int(args[0].upper().removeprefix("SC"))
    else:
        val[0] += REGISTERS[args[0].upper()]<<8
        
    if (args[1].upper().startswith("RM")): #write to RAM
        [(1<<12) + (REGISTERS[args[0].upper()]<<8) + 12, ]
        val[0] += 12
        val[1] += int(args[1].upper().removeprefix("RM"))<<8
    elif (args[1].upper().startswith("SC")): #write from screen
        val[0] += 3
        val[1] += int(args[1].upper().removeprefix("SC"))
    else:
        val[0] += REGISTERS[args[1].upper()]<<4
    
    return val
def InterpretCAL(args):
    return [(1<<12) + (REGISTERS[args[0].upper()]<<8) + (REGISTERS[args[1].upper()]<<4) + CALCINSTR[args[2].upper()], 0]
def InterpretRSC():
    return [3<<12, 0]
def InterpretJMP(args):
    return [4<<12, int(args[0])]



with open("test.dasm") as f:
    lines = f.readlines()
    for line in lines:
        line = line.removesuffix("\n").split(" ")
        val = []
        if line[0] == "IMM":
            val = InterpretIMM(line[1:])
        elif line[0] == "MOV":
            val = InterpretMOV(line[1:])
        elif line[0] == "CAl":
            val = InterpretCAL(line[1:])
        elif line[0] == "RSC":
            val = InterpretRSC()
        elif line[0] == "JMP":
            val = InterpretJMP(line[1:])
        MainROM.append(val[0])
        ValueROM.append(val[1])


str0 = ""

print(MainROM[1])
print(ValueROM[1])
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
while not keyboard.is_pressed('a'):
    pass
pyperclip.copy(str1)
