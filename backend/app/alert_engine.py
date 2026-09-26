import ast
import operator
import math
from typing import Dict, Any, Union, Set

class SecurityException(Exception):
    """Исключение для защиты от инъекций кода."""
    pass

class CrackenAlertEngine:
    def __init__(self):
        self.allowed_operators = {
            # Арифметика
            ast.Add: operator.add,
            ast.Sub: operator.sub,
            ast.Mult: operator.mul,
            ast.Div: operator.truediv,
            ast.FloorDiv: operator.floordiv,
            ast.Mod: operator.mod,
            ast.Pow: operator.pow,
            ast.USub: operator.neg,
            ast.UAdd: operator.pos,
            # Сравнения (для триггеров алертов)
            ast.Gt: operator.gt,
            ast.GtE: operator.ge,
            ast.Lt: operator.lt,
            ast.LtE: operator.le,
            ast.Eq: operator.eq,
            ast.NotEq: operator.ne,
        }
        
        self.allowed_functions = {
            "abs": abs,
            "round": round,
            "sqrt": math.sqrt,
            "log": math.log,
        }
        
        self.allowed_variables: Set[str] = {
            "price",
            "volume_rub",
            "open",
            "high",
            "low",
            "avg_volume_2h",
        }

    def _eval_node(self, node: ast.AST, context: Dict[str, float]) -> Any:
        if isinstance(node, ast.Constant):
            return node.value

        elif isinstance(node, ast.Name):
            if node.id in self.allowed_variables:
                return context.get(node.id, 0.0)
            raise SecurityException(f"Запрещенная переменная: '{node.id}'")

        elif isinstance(node, ast.BinOp):
            op_type = type(node.op)
            if op_type in self.allowed_operators:
                left_val = self._eval_node(node.left, context)
                right_val = self._eval_node(node.right, context)
                
                if op_type in (ast.Div, ast.FloorDiv, ast.Mod) and right_val == 0.0:
                    return 0.0
                    
                return self.allowed_operators[op_type](left_val, right_val)
            raise SecurityException(f"Неподдерживаемый оператор: {op_type.__name__}")

        elif isinstance(node, ast.UnaryOp):
            op_type = type(node.op)
            if op_type in self.allowed_operators:
                operand_val = self._eval_node(node.operand, context)
                return self.allowed_operators[op_type](operand_val)
            raise SecurityException(f"Неподдерживаемый унарный оператор: {op_type.__name__}")


        elif isinstance(node, ast.Compare):
            left_val = self._eval_node(node.left, context)
            op_type = type(node.ops[0])
            right_val = self._eval_node(node.comparators[0], context)
            
            if op_type in self.allowed_operators:
                return self.allowed_operators[op_type](left_val, right_val)
            raise SecurityException(f"Неподдерживаемый оператор сравнения: {op_type.__name__}")

        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id in self.allowed_functions:
                args = [self._eval_node(arg, context) for arg in node.args]
                return self.allowed_functions[node.func.id](*args)
            raise SecurityException(f"Запрещенный вызов функции")

        else:
            raise SecurityException(f"Запрещенная структура: '{type(node).__name__}'")

    def execute(self, formula_str: str, context: Dict[str, float]) -> Any:
        clean_formula = formula_str.strip()
        if not clean_formula:
            return None
        try:
            tree = ast.parse(clean_formula, mode='eval')
            return self._eval_node(tree.body, context)
        except SecurityException as sec_err:
            print(f"🔒 [SECURITY BLOCKED]: {sec_err}")
            return None
            
        except (SyntaxError, Exception) as err:
            print(f"❌ [ERROR]: Ошибка вычисления формулы: {err}")
            return None
