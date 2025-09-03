
import pyperclip
import keyboard



MainROM = []
ValueROM = []
Tokens = []

REGISTERS = {"REG0":0, "REG1":1,"REG2":2, "REG3":3}
CALCINSTR = {"ADD":0, "SUB":1, "MUL":2}

def InterpretIMM(args) -> list:
    return [0, int(args[0])]
def InterpretMOV(args):
    return [(1<<12) + (REGISTERS[args[0].upper()]<<8) + (REGISTERS[args[1].upper()]<<4), 0]
def InterpretCAL(args):
    return [(1<<12) + (REGISTERS[args[0].upper()]<<8) + (REGISTERS[args[1].upper()]<<4) + CALCINSTR[args[2].upper()], 0]


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
    




        
        