import streamlit as st

from calculator import CalculatorError, SmartCalculator

st.set_page_config(page_title="Smart Calculator", layout="centered")

# ---------- session state ----------
if "calc" not in st.session_state:
    st.session_state.calc = SmartCalculator()
if "expr" not in st.session_state:
    st.session_state.expr = ""
if "history" not in st.session_state:
    st.session_state.history = []      # list of (expression, result) pairs, newest first
if "result" not in st.session_state:
    st.session_state.result = None
if "error" not in st.session_state:
    st.session_state.error = None

calc: SmartCalculator = st.session_state.calc


# ---------- actions ----------
def calculate():
    expression = st.session_state.expr
    try:
        value = calc.evaluate(expression)
        shown = calc.format_result(value)
        st.session_state.result = shown
        st.session_state.error = None
        st.session_state.history.insert(0, (expression.strip(), shown))
        st.session_state.history = st.session_state.history[:20]
    except CalculatorError as err:
        st.session_state.result = None
        st.session_state.error = str(err)


def press(symbol):
    st.session_state.expr += symbol


def clear():
    st.session_state.expr = ""
    st.session_state.result = None
    st.session_state.error = None


def backspace():
    st.session_state.expr = st.session_state.expr[:-1]


def reuse(expression):
    st.session_state.expr = expression


def clear_history():
    st.session_state.history = []


# ---------- layout ----------
st.title("Smart Calculator")
st.caption("Type an expression and press Enter, or use the keypad.")

with st.form("calculator", clear_on_submit=False, border=False):
    st.text_input(
        "Expression",
        key="expr",
        placeholder="e.g. 12 * (3 + 4)  or  sqrt(144)  or  2^10",
        label_visibility="collapsed",
    )
    st.form_submit_button("=  Calculate", type="primary", use_container_width=True, on_click=calculate)

if st.session_state.result is not None:
    st.success(f"**= {st.session_state.result}**")
elif st.session_state.error:
    st.error(st.session_state.error)

# Keypad: each row is 4 buttons
keypad = [
    ["7", "8", "9", "÷"],
    ["4", "5", "6", "×"],
    ["1", "2", "3", "-"],
    ["0", ".", "mod", "+"],
    ["(", ")", "^", "√"],
]
insert_text = {"÷": "/", "×": "*", "√": "sqrt(", "mod": "%"}

for row in keypad:
    cols = st.columns(4)
    for col, key in zip(cols, row):
        col.button(
            key,
            key=f"btn_{key}",
            use_container_width=True,
            on_click=press,
            args=(insert_text.get(key, key),),
        )

c1, c2, c3, c4 = st.columns(4)
c1.button("C", use_container_width=True, on_click=clear, help="Clear")
c2.button("⌫", use_container_width=True, on_click=backspace, help="Delete last character")
c3.button("ans", use_container_width=True, on_click=press, args=("ans",), help="Use the previous answer")
c4.button("π", use_container_width=True, on_click=press, args=("pi",))

# ---------- history ----------
st.divider()
st.subheader("History")
if st.session_state.history:
    for i, (expression, shown) in enumerate(st.session_state.history):
        left, right = st.columns([5, 1])
        left.markdown(f"`{expression}` = **{shown}**")
        right.button("Reuse", key=f"reuse_{i}", on_click=reuse, args=(expression,))
    st.button("Clear history", on_click=clear_history)
else:
    st.caption("Your calculations will appear here.")

# ---------- help ----------
with st.expander("What can I type?"):
    st.markdown(
        """
| You type | Meaning | Example |
| --- | --- | --- |
| `+ - * /` (or `x`, `×`, `÷`) | Basic maths | `12 x 3` |
| `^` or `**` | Power | `2^10` |
| `//` | Whole-number division | `17 // 5` |
| `%` | Remainder | `17 % 5` |
| `sqrt()` `abs()` `round()` | Functions | `round(2.567, 2)` |
| `log()` `ln()` | Log base 10, natural log | `log(1000)` |
| `sin()` `cos()` `tan()` | Trig, angles in degrees | `sin(30)` |
| `factorial()` | Factorial | `factorial(5)` |
| `pi`, `e` | Constants | `2 * pi * 7` |
| `ans` | Previous answer | `ans * 1.16` |

Commas in numbers are fine: `1,000,000 / 4`.
"""
    )
