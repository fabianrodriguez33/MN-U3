"""Lógica matemática: Regla del Trapecio (simple y compuesta) y análisis de convergencia."""
import numpy as np
import pandas as pd
import sympy as sp
from scipy.integrate import quad

_SAFE_NAMES = {"pi": sp.pi, "e": sp.E, "E": sp.E}


def trapecio_simple(f, a, b):
    """Ecuación (1): I = h/2 [f(a) + f(b)], con h = b - a."""
    h = b - a
    return h / 2 * (f(a) + f(b))


def trapecio_compuesto(f, a, b, n):
    """Ecuación (3). Retorna (x, fx, integral, DataFrame de iteraciones)."""
    if n < 1:
        raise ValueError("n debe ser >= 1")
    h = (b - a) / n
    x = a + h * np.arange(n + 1)
    fx = np.asarray(f(x), dtype=float) * np.ones(n + 1)
    coef = np.full(n + 1, 2.0)
    coef[0] = coef[-1] = 1.0
    integral = h / 2 * float(np.sum(coef * fx))
    tabla = pd.DataFrame({"i": np.arange(n + 1), "x_i": x, "f(x_i)": fx, "coef": coef.astype(int)})
    return x, fx, integral, tabla


def cota_error_compuesta(f2_max, a, b, n):
    """Ecuación (4): (b-a) h^2 / 12 * max|f''|."""
    h = (b - a) / n
    return (b - a) * h ** 2 / 12 * f2_max


def max_segunda_derivada(expr_str, var_name, a, b, params=None, muestras=2001):
    """Estima max|f''| en [a,b] derivando simbólicamente."""
    expr, x = _parse(expr_str, var_name, params or {})
    d2 = sp.lambdify(x, sp.diff(expr, x, 2), "numpy")
    xs = np.linspace(a, b, muestras)
    return float(np.max(np.abs(d2(xs) * np.ones_like(xs))))


def _parse(expr_str, var_name, params):
    x = sp.Symbol(var_name)
    local = {**_SAFE_NAMES, var_name: x}
    for k in params:
        local[k] = sp.Symbol(k)
    expr = sp.sympify(expr_str.replace("^", "**"), locals=local)
    expr = expr.subs({sp.Symbol(k): v for k, v in params.items()})
    libres = expr.free_symbols - {x}
    if libres:
        raise ValueError(f"Parámetros sin valor: {sorted(str(s) for s in libres)}")
    return expr, x


def evaluador_simbolico(expr_str, var_name="x", params=None):
    """Convierte una expresión (con parámetros) en una función NumPy vectorizada f(x).

    params: dict {nombre: valor} para las demás variables (ej. {'A': 2, 'k': 3}).
    """
    expr, x = _parse(expr_str, var_name, params or {})
    g = sp.lambdify(x, expr, "numpy")

    def f(v):
        v = np.asarray(v, dtype=float)
        return np.asarray(g(v), dtype=float) * np.ones_like(v)

    return f, expr


def valor_exacto(f, a, b):
    """Cuadratura adaptativa de alta precisión (referencia)."""
    return quad(lambda t: float(f(t)), a, b, epsabs=1e-13, epsrel=1e-13, limit=500)[0]


def analisis_convergencia(f, a, b, lista_n, exacto=None):
    """Tabla comparativa con error absoluto y relativo real."""
    if exacto is None:
        exacto = valor_exacto(f, a, b)
    filas = []
    for n in lista_n:
        _, _, I, _ = trapecio_compuesto(f, a, b, n)
        err = abs(exacto - I)
        filas.append({
            "n": n,
            "h": (b - a) / n,
            "Integral": I,
            "Error absoluto": err,
            "Error relativo (%)": err / abs(exacto) * 100 if exacto else np.nan,
        })
    return pd.DataFrame(filas), exacto


def R_trafico(t):
    """Caso guía: tasa de transferencia R(t) en Mbps."""
    t = np.asarray(t, dtype=float)
    return (10 + 5 * np.sin(np.pi * t)) / (4 + np.exp(0.15 * t))
