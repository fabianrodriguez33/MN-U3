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


def _nombres(var_name):
    return (var_name,) if isinstance(var_name, str) else tuple(var_name)


def parsear(expr_str, var_name="x"):
    """Retorna (expr, símbolo_de_la_primera_variable).

    var_name puede ser un nombre ("x") o varios (("x", "y")). Los demás nombres libres
    quedan como parámetros."""
    if not expr_str or not expr_str.strip():
        raise ValueError("Escriba una función")
    nombres = _nombres(var_name)
    simbolos = {n: sp.Symbol(n) for n in nombres}
    local = {**FUNCIONES, **CONSTANTES, **simbolos}
    expr = parse_expr(expr_str.strip(), local_dict=local, transformations=_TRANSF)
    return sp.sympify(expr), simbolos[nombres[0]]


def parametros_libres(expr_str, var_name="x"):
    """Nombres de parámetros detectados (símbolos distintos de la variable), ordenados."""
    try:
        expr, _ = parsear(expr_str, var_name)
    except Exception:
        return []
    return sorted(str(s) for s in expr.free_symbols if str(s) not in _nombres(var_name))


def evaluar_numero(txt):
    """'pi/2', '1.5', 'sqrt(2)' -> float."""
    expr, _ = parsear(txt, "x")
    if expr.free_symbols:
        raise ValueError(f"'{txt}' no es un número")
    return float(expr)
