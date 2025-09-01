MainROM = []
ValueROM = []
Tokens = []

Registers = {"REG0":0, "REG1":1,"REG2":2, "REG3":3}

def InterpretIMM(args) -> list:
    return [0, args[0]]
def InterpretMOV(args):
    return [1<<12 + Registers[args[0]]<<8 + Registers[args[1]]<<4, 0]
def InterpretCAL(args):
    return []


with open("test.dasm") as f:
    lines = f.readlines()
    for line in lines:
        line = line.removesuffix("\n").split(" ")
        if line[0] == "IMM":
            InterpretIMM(line[1:])
        elif line[0] == "MOV":
            InterpretMOV(line[1:])
        elif line[0] == "CAl":
            InterpretCAL(line[1:])


        
        