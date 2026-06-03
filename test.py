Expr = "2+2"


def IsExpression(Varbs: dict, expr: str): # can be optimized further
    variableHolder = ""
    expressionChars = "+-/*0123456789() "
    for i in range(len(expr)):
        c = expr[i]
        if (not c in expressionChars):
            variableHolder += c
        elif (variableHolder in Varbs):
            return False
        else:
            variableHolder
    if (len(variableHolder) > 0 and variableHolder in Varbs):
        return False
    
    return True

def HandleExpression(Varbs: dict, expr: str):
    expr = expr.replace(" ", "")
    variableHolder = ""
    expressionChars = "+-/*0123456789()"
    expressionParts = []

    for i in range(len(expr)):
        c = expr[i]
        if (c in expressionChars):
            expressionParts.append(str(c))
            if (variableHolder)
        else:
            variableHolder += c
        
            




        
        
