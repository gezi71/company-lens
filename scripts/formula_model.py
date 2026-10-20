"""Small Excel formula graph with a safe, independent Python arithmetic evaluator.

Only the generated scalar arithmetic, IF and CHOOSE expressions are supported.
No eval, macros, external links, ranges, or arbitrary Python calls are executed.
"""
import ast
import math
import operator
import re
from dataclasses import dataclass


@dataclass
class Cell:
    value: object = None
    formula: str = None
    note: str = ""
    percent: bool = False


class MissingInput(ValueError):
    pass


class FormulaModel:
    def __init__(self):
        self.cells = {}
        self.cache = {}
        self.active = set()

    def set(self, sheet, address, value=None, formula=None, note="", percent=False):
        self.cells[(sheet, address)] = Cell(value, formula, note, percent)
        self.cache.clear()
        return f"'{sheet}'!{address}"

    def get(self, sheet, address):
        key = sheet, address.replace("$", "")
        if key in self.cache:
            return self.cache[key]
        cell = self.cells.get(key)
        if cell is None or (cell.value is None and cell.formula is None):
            raise MissingInput(f"缺失输入 {key}")
        if key in self.active:
            raise ValueError(f"循环引用 {key}")
        self.active.add(key)
        try:
            result = self._evaluate(cell.formula, sheet) if cell.formula else cell.value
            if isinstance(result, float) and not math.isfinite(result):
                raise ValueError(f"非有限值 {key}")
            self.cache[key] = result
            return result
        finally:
            self.active.remove(key)

    def _evaluate(self, formula, sheet):
        pattern = r"(?:(?:'([^']+)'|([A-Za-z_][A-Za-z_0-9]*))!)?(\$?[A-Z]{1,3}\$?\d+)"
        expression = re.sub(pattern, lambda m: f"REF({(m[1] or m[2] or sheet)!r},{m[3].replace('$', '')!r})",
                            formula.lstrip("=")).replace("^", "**")
        # Excel comparison operators differ from Python; leave quoted text intact.
        segments = re.split(r'''("[^"]*"|'[^']*')''', expression)
        for i in range(0, len(segments), 2):
            segments[i] = re.sub(r"(?<![<>=!])=(?!=)", "==", segments[i].replace("<>", "!="))
        expression = "".join(segments)
        return self._node(ast.parse(expression, mode="eval").body)

    def _node(self, node):
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float, str)):
            return node.value
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.USub, ast.UAdd)):
            return (-1 if isinstance(node.op, ast.USub) else 1) * self._node(node.operand)
        if isinstance(node, ast.BinOp):
            ops = {ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul,
                   ast.Div: operator.truediv, ast.Pow: operator.pow}
            if type(node.op) in ops:
                return ops[type(node.op)](self._node(node.left), self._node(node.right))
        if isinstance(node, ast.Compare) and len(node.ops) == 1:
            ops = {ast.Gt: operator.gt, ast.Lt: operator.lt, ast.GtE: operator.ge,
                   ast.LtE: operator.le, ast.Eq: operator.eq, ast.NotEq: operator.ne}
            if type(node.ops[0]) in ops:
                return ops[type(node.ops[0])](self._node(node.left), self._node(node.comparators[0]))
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            name = node.func.id
            if name == "REF" and len(node.args) == 2:
                return self.get(self._node(node.args[0]), self._node(node.args[1]))
            if name == "IF" and len(node.args) == 3:
                return self._node(node.args[1] if self._node(node.args[0]) else node.args[2])
            if name == "CHOOSE" and len(node.args) == 4:
                index = self._node(node.args[0])
                if index not in (1, 2, 3):
                    raise ValueError("情景选择器必须为1、2或3")
                return self._node(node.args[int(index)])
            if name in {"MAX", "MIN", "ABS"}:
                funcs = {"MAX": max, "MIN": min, "ABS": abs}
                return funcs[name](*[self._node(x) for x in node.args])
        raise ValueError(f"不支持的公式表达式: {ast.dump(node)}")
