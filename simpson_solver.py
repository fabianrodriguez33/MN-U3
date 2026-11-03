"""Sesión 13: Reglas de Simpson 1/3, 3/8 y combinada (funciones y datos tabulares)."""
import warnings

import numpy as np
import pandas as pd
import sympy as sp

from trapezoidal_solver import valor_exacto

_SAFE_NAMES = {"pi": sp.pi, "e": sp.E, "E": sp.E}


def _malla(f_or_y, a, b, n, x):
    """Devuelve (x, y, h) a partir de una función con [a,b,n] o de arreglos (x, y)."""
    if callable(f_or_y):
        if a is None or b is None or n is None:
            raise ValueError("Con una función se requieren a, b y n")
        n = int(n)
        if n < 1:
            raise ValueError("n debe ser >= 1")
        xs = np.linspace(a, b, n + 1)
        ys = np.asarray(f_or_y(xs), dtype=float) * np.ones(n + 1)
    else:
        ys = np.asarray(f_or_y, dtype=float)
        if x is None:
            raise ValueError("Con datos tabulares se requiere el arreglo x")
        xs = np.asarray(x, dtype=float)
        if xs.shape != ys.shape or xs.size < 2:
            raise ValueError("x e y deben tener la misma longitud (>= 2 puntos)")
        d = np.diff(xs)
        if np.any(d <= 0) or not np.allclose(d, d[0], rtol=1e-9, atol=1e-12):
            raise ValueError("Los puntos x deben estar ordenados y igualmente espaciados")
    return xs, ys, (xs[-1] - xs[0]) / (len(xs) - 1)


def _pesos_13(n):
    w = np.ones(n + 1)
    w[1:-1:2] = 4
    w[2:-1:2] = 2
    return w


def _pesos_38(n):
    w = np.full(n + 1, 3.0)
    w[0] = w[-1] = 1
    w[3:-1:3] = 2
    return w


def _resultado(xs, ys, w, factor):
    I = float(factor * np.sum(w * ys))
    tabla = pd.DataFrame({"i": np.arange(len(xs)), "x_i": xs, "f(x_i)": ys, "peso": w.astype(int)})
    return xs, ys, I, tabla


def simpson_13_compuesto(f_or_y, a=None, b=None, n=None, x=None):
    """Simpson 1/3 compuesto. Si n es impar se conmuta a la regla combinada (con advertencia).

    Retorna (x, y, integral, DataFrame de pesos)."""
    xs, ys, h = _malla(f_or_y, a, b, n, x)
    N = len(xs) - 1
    if N % 2:
        warnings.warn("n impar: se usa Simpson combinado (1/3 + 3/8)", stacklevel=2)
        return simpson_combinado(ys, xs)
    return _resultado(xs, ys, _pesos_13(N), h / 3)


def simpson_38_compuesto(f_or_y, a=None, b=None, n=None, x=None):
    """Simpson 3/8 compuesto; n debe ser múltiplo de 3. Retorna (x, y, integral, tabla)."""
    xs, ys, h = _malla(f_or_y, a, b, n, x)
    N = len(xs) - 1
    if N % 3:
        raise ValueError("Simpson 3/8 requiere n múltiplo de 3")
    return _resultado(xs, ys, _pesos_38(N), 3 * h / 8)


def simpson_combinado(y, x):
    """1/3 en los primeros subintervalos (pares) y 3/8 en los últimos 3 si n es impar.

    Para n = 1 no hay regla de Simpson aplicable (se lanza ValueError)."""
    xs, ys, h = _malla(y, None, None, None, x)
    N = len(xs) - 1
    if N == 1:
        raise ValueError("Se requieren al menos 2 subintervalos")
    if N % 2 == 0:
        return _resultado(xs, ys, _pesos_13(N), h / 3)
    k = N - 3  # subintervalos para 1/3 (par, posiblemente 0)
    w = np.zeros(N + 1)
    I = 0.0
    if k > 0:
        w13 = _pesos_13(k)
        I += h / 3 * np.sum(w13 * ys[: k + 1])
        w[: k + 1] += w13 * (1 / 3)
    w38 = _pesos_38(3)
    I += 3 * h / 8 * np.sum(w38 * ys[k:])
    w[k:] += w38 * (3 / 8)
    # pesos efectivos expresados como múltiplos de h
    tabla = pd.DataFrame({"i": np.arange(N + 1), "x_i": xs, "f(x_i)": ys, "peso (xh)": w})
    return xs, ys, float(I), tabla


def trapecio_datos(y, x):
    """Trapecio compuesto sobre datos tabulares (para comparar)."""
    xs, ys, h = _malla(y, None, None, None, x)
    return float(h / 2 * (ys[0] + 2 * ys[1:-1].sum() + ys[-1]))


def evaluador_simbolico(expr_str, variables_dict=None, x_var="x"):
    """Expresión -> función NumPy f(x). variables_dict: {parámetro: valor}. Retorna (f, expr)."""
    params = variables_dict or {}
    x = sp.Symbol(x_var)
    local = {**_SAFE_NAMES, x_var: x, **{k: sp.Symbol(k) for k in params}}
    expr = sp.sympify(expr_str.replace("^", "**"), locals=local)
    expr = expr.subs({sp.Symbol(k): v for k, v in params.items()})
    libres = expr.free_symbols - {x}
    if libres:
        raise ValueError(f"Parámetros sin valor: {sorted(str(s) for s in libres)}")
    g = sp.lambdify(x, expr, "numpy")

    def f(v):
        v = np.asarray(v, dtype=float)
        return np.asarray(g(v), dtype=float) * np.ones_like(v)

    return f, expr


def cota_error_13(expr_str, a, b, n, variables_dict=None, x_var="x", muestras=2001):
    """|E| <= n h^5 / 180 * max|f''''| (ec. compuesta). Retorna (cota, max|f4|)."""
    params = variables_dict or {}
    x = sp.Symbol(x_var)
    local = {**_SAFE_NAMES, x_var: x, **{k: sp.Symbol(k) for k in params}}
    expr = sp.sympify(expr_str.replace("^", "**"), locals=local)
    expr = expr.subs({sp.Symbol(k): v for k, v in params.items()})
    d4 = sp.lambdify(x, sp.diff(expr, x, 4), "numpy")
    xs = np.linspace(a, b, muestras)
    m = float(np.max(np.abs(d4(xs) * np.ones_like(xs))))
    h = (b - a) / n
    return n * h ** 5 / 180 * m, m


def analisis_convergencia_simpson(expr_str, a, b, n_list, variables_dict=None, x_var="x"):
    """DataFrame: n, h, I_Simpson13, I_Simpson38, Error_Abs_13, Error_Rel_%_13.

    I_Simpson13 requiere n par (si no, NaN); I_Simpson38 requiere n múltiplo de 3 (si no, NaN)."""
    f, _ = evaluador_simbolico(expr_str, variables_dict, x_var)
    exacto = valor_exacto(f, a, b)
    filas = []
    for n in n_list:
        i13 = simpson_13_compuesto(f, a, b, n)[2] if n % 2 == 0 else np.nan
        i38 = simpson_38_compuesto(f, a, b, n)[2] if n % 3 == 0 else np.nan
        err = abs(exacto - i13)
        filas.append({
            "n": n,
            "h": (b - a) / n,
            "I_Simpson13": i13,
            "I_Simpson38": i38,
            "Error_Abs_13": err,
            "Error_Rel_%_13": err / abs(exacto) * 100 if exacto else np.nan,
        })
    return pd.DataFrame(filas), exacto


def segmentos_interpolantes(xs, ys, metodo):
    """Polinomios interpolantes por tramo: [(x0, x1, coef)] con np.polyfit.

    metodo: '13' (parábolas, 2 subint.), '38' (cúbicas, 3 subint.) o 'combinado'."""
    N = len(xs) - 1
    if metodo == "13":
        saltos = [2] * (N // 2)
    elif metodo == "38":
        saltos = [3] * (N // 3)
    else:
        saltos = [2] * (N // 2) if N % 2 == 0 else [2] * ((N - 3) // 2) + [3]
    segs, i = [], 0
    for s in saltos:
        px, py = xs[i: i + s + 1], ys[i: i + s + 1]
        segs.append((px[0], px[-1], np.polyfit(px, py, s)))
        i += s
    return segs
