import sympy
from sympy.parsing.sympy_parser import parse_expr
from sympy.printing.precedence import PRECEDENCE

class Instruction:
    def __init__(self, keyword: str, params: int, func):
        self.keyword = keyword
        self.params = params
        self.func = func
    def call(self, args: list, linenum):
        if (len(args) != self.params):
            raise ValueError("Not enough paramaters in function: " + self.keyword + " at line " + str(linenum) + ". " + str(len(args)) + " given.\nArgs: " + str(args))
        return self.func(args)
class Function:
    def __init__(self, kword, area):
        self.kword = kword
        self.area = area
class Variable:
    def __init__(self, kword, addr):
        self.kword = kword
        self.addr = addr
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


def get_operation_tree(equation_str):
    expr = parse_expr(equation_str, transformations='all')
    
    def build_tree(node):
        if node.is_Number:
            return {'type': 'number', 'value': node, 'precedence': float('inf')}
        elif node.is_Symbol:
            return {'type': 'symbol', 'value': str(node), 'precedence': float('inf')}
        elif hasattr(node, 'func') and node.func.is_Function:
            return {
                'type': 'function',
                'value': str(node.func),
                'precedence': PRECEDENCE[node.func],
                'children': [build_tree(arg) for arg in node.args]
            }
        elif node.is_Mul or node.is_Add or node.is_Pow or node.is_Div:
            prec = PRECEDENCE.get(node.func, 0)
            children = [build_tree(arg) for arg in node.args]
            return {
                'type': 'op',
                'value': str(node.func.__name__),
                'precedence': prec,
                'children': children,
                'associative': len(children) > 2
            }
        elif hasattr(node, 'args') and len(node.args) == 2:
            # Binary operators
            op_map = {
                sympy.Add: '+', sympy.Mul: '*', sympy.Pow: '**',
                sympy.Sub: '-', sympy.core.function.UndefinedFunction: 'func'
            }
            op_str = op_map.get(node.func, '?')
            prec = PRECEDENCE.get(node.func, 0)
            return {
                'type': 'op',
                'value': op_str,
                'precedence': prec,
                'children': [build_tree(node.args[0]), build_tree(node.args[1])]
            }
        return {'type': 'unknown', 'value': str(node)}
    
    return build_tree(expr)
def InterpretOperation(tree):
    if (tree["type"] ==):