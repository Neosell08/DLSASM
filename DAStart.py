from DA import InterpretLines

lines = []
with open("test.da") as f:
    lines = f.readlines()
code = InterpretLines(lines)
    



try:
    with open("Circuits/code", "x") as f:
        f.write(code)
except FileExistsError:
    with open("Circuits/code", "w") as f:
        f.write(code)
print("written to code file")
