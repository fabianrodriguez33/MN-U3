"""Parser tolerante de expresiones: acepta ^, ln, sen, abs, multiplicación implícita (2x, 3sin(x))."""
import sympy as sp
from sympy.parsing.sympy_parser import (
    convert_xor, implicit_multiplication_application, parse_expr, standard_transformations,
)

FUNCIONES = {
    "sin": sp.sin, "sen": sp.sin, "cos": sp.cos, "tan": sp.tan,
    "asin": sp.asin, "acos": sp.acos, "atan": sp.atan,
    "sinh": sp.sinh, "cosh": sp.cosh, "tanh": sp.tanh,
    "exp": sp.exp, "log": sp.log, "ln": sp.log, "sqrt": sp.sqrt, "abs": sp.Abs,
}
CONSTANTES = {"pi": sp.pi, "e": sp.E}
_TRANSF = standard_transformations + (implicit_multiplication_application, convert_xor)


def parsear(expr_str, var_name="x"):
    """Retorna (expr, símbolo_variable). Los demás nombres libres quedan como parámetros."""
    if not expr_str or not expr_str.strip():
        raise ValueError("Escriba una función")
    x = sp.Symbol(var_name)
    local = {**FUNCIONES, **CONSTANTES, var_name: x}
    expr = parse_expr(expr_str.strip(), local_dict=local, transformations=_TRANSF)
    return sp.sympify(expr), x


def parametros_libres(expr_str, var_name="x"):
    """Nombres de parámetros detectados (símbolos distintos de la variable), ordenados."""
    try:
        expr, x = parsear(expr_str, var_name)
    except Exception:
        return []
    return sorted(str(s) for s in expr.free_symbols - {x})


def evaluar_numero(txt):
    """'pi/2', '1.5', 'sqrt(2)' -> float."""
    expr, _ = parsear(txt, "x")
    if expr.free_symbols:
        raise ValueError(f"'{txt}' no es un número")
    return float(expr)
