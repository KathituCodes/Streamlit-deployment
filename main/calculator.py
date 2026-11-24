"""Smart Calculator engine.

Safely evaluates maths expressions typed by a user. It never calls eval():
the text is parsed into a syntax tree and only whitelisted numbers,
operators, functions and constants are allowed.
"""

import ast
import math
import operator as op
import re


class CalculatorError(Exception):
    """Raised when an expression cannot be calculated. The message is user-friendly."""


class SmartCalculator:
    MAX_INPUT_LENGTH = 200      # longest expression accepted
    MAX_EXPONENT = 1000         # stops inputs like 9**9**9 from freezing the app
    MAX_RESULT_DIGITS = 4300    # Python's own limit for printing very large integers

    BINARY_OPERATORS = {
        ast.Add: op.add,
        ast.Sub: op.sub,
        ast.Mult: op.mul,
        ast.Div: op.truediv,
        ast.FloorDiv: op.floordiv,
        ast.Mod: op.mod,
        ast.Pow: op.pow,
    }

    UNARY_OPERATORS = {
        ast.USub: op.neg,
        ast.UAdd: op.pos,
    }

    FUNCTIONS = {
        "sqrt": math.sqrt,
        "abs": abs,
        "round": round,
        "log": math.log10,     # log(100) = 2
        "ln": math.log,        # natural log
        "sin": lambda x: math.sin(math.radians(x)),   # angles in degrees
        "cos": lambda x: math.cos(math.radians(x)),
        "tan": lambda x: math.tan(math.radians(x)),
        "factorial": math.factorial,
    }

    CONSTANTS = {
        "pi": math.pi,
        "e": math.e,
    }

    def __init__(self):
        self.last_answer = 0   # available to the user as "ans"

    # ---------- public API ----------

    def evaluate(self, expression: str):
        """Return the numeric result, or raise CalculatorError with a clear message."""
        expression = self._normalise(expression)

        if not expression:
            raise CalculatorError("Please type an expression, for example 12 * (3 + 4).")
        if len(expression) > self.MAX_INPUT_LENGTH:
            raise CalculatorError(f"Expression is too long (max {self.MAX_INPUT_LENGTH} characters).")

        try:
            tree = ast.parse(expression, mode="eval")
        except SyntaxError:
            raise CalculatorError("That doesn't look like a valid expression. Check for missing numbers or brackets.")

        try:
            result = self._eval_node(tree.body)
        except ZeroDivisionError:
            raise CalculatorError("You can't divide by zero.")
        except OverflowError:
            raise CalculatorError("The result is too large to calculate.")
        except (ValueError, TypeError) as exc:
            raise CalculatorError(f"Math error: {exc}.")

        if isinstance(result, int) and abs(result) >= 10 ** self.MAX_RESULT_DIGITS:
            raise CalculatorError("The result is too large to display.")

        self.last_answer = result
        return result

    @staticmethod
    def format_result(value) -> str:
        """Display results cleanly: 0.1 + 0.2 shows 0.3, 6 / 2 shows 3, big numbers get commas."""
        if isinstance(value, float):
            if math.isinf(value) or math.isnan(value):
                return str(value)
            value = round(value, 10)
            if value.is_integer() and abs(value) < 1e15:
                value = int(value)
            else:
                return f"{value:,.10g}" if abs(value) < 1e15 else f"{value:.6e}"
        return f"{value:,}"

    # ---------- helpers ----------

    def _normalise(self, expression: str) -> str:
        """Accept the symbols people naturally type."""
        expression = expression.strip()
        expression = expression.replace("×", "*").replace("÷", "/").replace("−", "-")
        expression = expression.replace("^", "**")            # 2^3 means power, not XOR
        expression = re.sub(r"(?<=\d),(?=\d{3}(?!\d))", "", expression)  # 1,000 -> 1000
        expression = re.sub(r"(?<=[\d)\s])[xX](?=[\s\d(])", "*", expression)  # 2 x 3 -> 2 * 3
        return expression

    def _eval_node(self, node):
        # Numbers (bool is excluded because True + 1 is not maths input)
        if isinstance(node, ast.Constant):
            if isinstance(node.value, (int, float)) and not isinstance(node.value, bool):
                return node.value
            raise CalculatorError("Only numbers are allowed.")

        # Named constants and the previous answer
        if isinstance(node, ast.Name):
            name = node.id.lower()
            if name == "ans":
                return self.last_answer
            if name in self.CONSTANTS:
                return self.CONSTANTS[name]
            raise CalculatorError(f"Unknown name '{node.id}'. Try pi, e or ans.")

        # a + b, a ** b, etc.
        if isinstance(node, ast.BinOp):
            operator_fn = self.BINARY_OPERATORS.get(type(node.op))
            if operator_fn is None:
                raise CalculatorError("That operator is not supported. Use + - * / // % or ^.")
            left = self._eval_node(node.left)
            right = self._eval_node(node.right)
            if isinstance(node.op, ast.Pow) and abs(right) > self.MAX_EXPONENT:
                raise CalculatorError(f"Exponent is too large (max {self.MAX_EXPONENT}).")
            return operator_fn(left, right)

        # -a, +a
        if isinstance(node, ast.UnaryOp):
            operator_fn = self.UNARY_OPERATORS.get(type(node.op))
            if operator_fn is None:
                raise CalculatorError("That operator is not supported.")
            return operator_fn(self._eval_node(node.operand))

        # sqrt(16), round(2.567, 2)
        if isinstance(node, ast.Call):
            if not isinstance(node.func, ast.Name) or node.func.id.lower() not in self.FUNCTIONS:
                allowed = ", ".join(self.FUNCTIONS)
                raise CalculatorError(f"Unknown function. Available: {allowed}.")
            if node.keywords:
                raise CalculatorError("Functions only take plain values, for example round(2.567, 2).")
            args = [self._eval_node(arg) for arg in node.args]
            fn_name = node.func.id.lower()
            if fn_name == "factorial" and args and args[0] > 1000:
                raise CalculatorError("Factorial is limited to numbers up to 1000.")
            return self.FUNCTIONS[fn_name](*args)

        raise CalculatorError("That expression contains something the calculator can't handle.")


def main():
    """Command-line version."""
    calc = SmartCalculator()
    print("Smart Calculator")
    print("Examples: 12 * (3 + 4), 2^10, sqrt(144), 15% of a number as 0.15 * 2000, ans + 1")
    print("Type 'exit' to quit.\n")

    while True:
        user_input = input("calc > ").strip()
        if user_input.lower() in ("exit", "quit"):
            print("Goodbye!")
            break
        if not user_input:
            continue
        try:
            result = calc.evaluate(user_input)
            print(f"= {calc.format_result(result)}")
        except CalculatorError as err:
            print(f"Error: {err}")


if __name__ == "__main__":
    main()
