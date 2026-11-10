"""Sesión 14: Problemas de valor inicial dy/dx = f(x, y) — Euler, Heun, RK3 y RK4."""
import threading

import numpy as np
import pandas as pd
import sympy as sp
from scipy.integrate import solve_ivp

from parser_util import parsear

NOMBRES = {"euler": "Euler", "heun": "Heun", "rk3": "RK3", "rk4": "RK4"}
ORDEN = {"euler": 1, "heun": 2, "rk3": 3, "rk4": 4}


# ----------------------------------------------------------------------------- un paso
def euler_step(f, x, y, h):
    return y + h * f(x, y)


def heun_step(f, x, y, h):
    k1 = f(x, y)
    return y + h / 2 * (k1 + f(x + h, y + h * k1))


def rk3_step(f, x, y, h):
    k1 = f(x, y)
    k2 = f(x + h / 2, y + h / 2 * k1)
    k3 = f(x + h, y - h * k1 + 2 * h * k2)
    return y + h / 6 * (k1 + 4 * k2 + k3)


def rk4_step(f, x, y, h):
    k1 = f(x, y)
    k2 = f(x + h / 2, y + h / 2 * k1)
    k3 = f(x + h / 2, y + h / 2 * k2)
    k4 = f(x + h, y + h * k3)
    return y + h / 6 * (k1 + 2 * k2 + 2 * k3 + k4)


PASOS = {"euler": euler_step, "heun": heun_step, "rk3": rk3_step, "rk4": rk4_step}


# ----------------------------------------------------------------------------- utilidades
def construir_f(f_expr, params=None, var_x="x", var_y="y"):
    """Texto -> (callable f(x, y) escalar, expresión sympy con parámetros sustituidos)."""
    expr, _ = parsear(f_expr, (var_x, var_y))
    expr = expr.subs({sp.Symbol(k): v for k, v in (params or {}).items()})
    libres = {str(s) for s in expr.free_symbols} - {var_x, var_y}
    if libres:
        raise ValueError(f"Parámetros sin valor: {sorted(libres)}")
    g = sp.lambdify((sp.Symbol(var_x), sp.Symbol(var_y)), expr, "numpy")

    def f(x, y):
        return float(g(x, y))

    return f, expr


def _malla(x0, x_target, h=None, n=None):
    """Devuelve (n, h_efectivo). Con h se redondea n al entero más cercano."""
    largo = x_target - x0
    if largo <= 0:
        raise ValueError("x_target debe ser mayor que x0")
    if n is None:
        if h is None or h <= 0:
            raise ValueError("Indique h > 0 o el número de pasos n")
        n = max(1, int(round(largo / h)))
    n = int(n)
    if n < 1:
        raise ValueError("n debe ser >= 1")
    return n, largo / n


def _correr(paso, f, x0, y0, h, n):
    xs = x0 + h * np.arange(n + 1)
    ys = np.full(n + 1, np.nan)
    ys[0] = y0
    with np.errstate(all="ignore"):
        for i in range(n):
            try:
                ys[i + 1] = paso(f, xs[i], ys[i], h)
            except (ZeroDivisionError, OverflowError, ValueError):
                break
            if not np.isfinite(ys[i + 1]):
                break
    return xs, ys


def solucion_exacta(f_expr, x0, y0, params=None, var_x="x", var_y="y", timeout=10):
    """Intenta resolver con sympy.dsolve. Retorna callable y(x) numérico o None.

    Se elige la rama que cumple y(x0) = y0. Si dsolve no responde en `timeout` s o no da
    una solución explícita, retorna None."""
    resultado = {}

    def trabajo():
        try:
            expr, _ = parsear(f_expr, (var_x, var_y))
            expr = expr.subs({sp.Symbol(k): v for k, v in (params or {}).items()})
            x, Y = sp.Symbol(var_x), sp.Function("Y")
            ode = sp.Eq(Y(x).diff(x), expr.subs(sp.Symbol(var_y), Y(x)))
            sol = sp.dsolve(ode, Y(x), ics={Y(x0): y0})
            sols = sol if isinstance(sol, (list, tuple)) else [sol]
            for s in sols:
                rhs = s.rhs
                if rhs.has(Y) or rhs.free_symbols - {x}:
                    continue
                g = sp.lambdify(x, rhs, "numpy")
                with np.errstate(all="ignore"):
                    v0 = complex(g(float(x0)))
                if abs(v0.imag) < 1e-9 and abs(v0.real - y0) < 1e-7 * max(1, abs(y0)):
                    resultado["f"] = lambda t, g=g: np.real(g(np.asarray(t, dtype=float)))
                    resultado["expr"] = rhs
                    return
        except Exception:
            pass

    hilo = threading.Thread(target=trabajo, daemon=True)
    hilo.start()
    hilo.join(timeout)
    return resultado.get("f"), resultado.get("expr")


def referencia(f, x0, y0, xs):
    """Solución numérica de alta precisión (DOP853) en los puntos xs."""
    r = solve_ivp(lambda t, y: [f(t, y[0])], (xs[0], xs[-1]), [y0], t_eval=xs,
                  method="DOP853", rtol=1e-12, atol=1e-13)
    if not r.success or r.y.shape[1] != len(xs):
        return np.full(len(xs), np.nan)
    return r.y[0]


def _exacta_en(f, f_expr, x0, y0, xs, params, exacta, var_x, var_y):
    """Retorna (valores, descripción de la fuente)."""
    if exacta is not None:
        if callable(exacta):
            return np.asarray(exacta(xs), dtype=float), "solución exacta dada"
        e, _ = parsear(exacta, var_x)
        g = sp.lambdify(sp.Symbol(var_x), e, "numpy")
        return np.asarray(g(xs), dtype=float) * np.ones(len(xs)), "solución exacta dada"
    g, expr = solucion_exacta(f_expr, x0, y0, params, var_x, var_y)
    if g is not None:
        return np.asarray(g(xs), dtype=float), "sympy.dsolve"
    return referencia(f, x0, y0, xs), "referencia numérica (DOP853, tol 1e-12)"


# ----------------------------------------------------------------------------- API principal
def solve_pvi(f_expr, x0, y0, x_target, h=None, methods=("euler", "heun", "rk3", "rk4"),
              params=None, n=None, exacta=None, var_x="x", var_y="y"):
    """Resuelve el PVI con varios métodos a la vez.

    Retorna un DataFrame: x_i, y_Exacto, y_<Método>, Error_Abs_<Método>, Error_Rel_%_<Método>.
    df.attrs: 'fuente_exacta', 'h', 'n'. Con `exacta` (texto en x o callable) se omite dsolve."""
    f, _ = construir_f(f_expr, params, var_x, var_y)
    n, h_ef = _malla(x0, x_target, h, n)
    xs = x0 + h_ef * np.arange(n + 1)
    m = max(1, -(-200 // n))  # subdivisiones por paso para la curva exacta continua
    xd = x0 + h_ef * np.arange(n * m + 1) / m
    ex_d, fuente = _exacta_en(f, f_expr, x0, y0, xd, params, exacta, var_x, var_y)
    ex = ex_d[::m]
    df = pd.DataFrame({"x_i": xs, "y_Exacto": ex})
    df.attrs["curva"] = {"x": xd.tolist(), "y": ex_d.tolist()}  # listas: attrs se compara con ==
    for m in methods:
        _, ys = _correr(PASOS[m], f, x0, y0, h_ef, n)
        nm = NOMBRES[m]
        err = np.abs(ex - ys)
        df[f"y_{nm}"] = ys
        df[f"Error_Abs_{nm}"] = err
        with np.errstate(all="ignore"):
            df[f"Error_Rel_%_{nm}"] = np.where(ex != 0, err / np.abs(ex) * 100, np.nan)
    df.attrs.update({"fuente_exacta": fuente, "h": h_ef, "n": n})
    return df


def convergence_analysis_pvi(f_expr, x0, y0, x_target, h_list=(0.1, 0.05, 0.01, 0.005, 0.001),
                             params=None, methods=("euler", "heun", "rk3", "rk4"),
                             exacta=None, var_x="x", var_y="y"):
    """Error en x_target al disminuir h. Columnas: h, n, y_exacto y, por método, y/error abs/rel."""
    f, _ = construir_f(f_expr, params, var_x, var_y)
    xt = np.array([float(x_target)])
    ex, fuente = _exacta_en(f, f_expr, x0, y0, np.array([x0, float(x_target)]), params, exacta, var_x, var_y)
    ex_t = float(ex[-1])
    filas = []
    for h in h_list:
        n, h_ef = _malla(x0, x_target, h)
        fila = {"h": h_ef, "n": n, "y_Exacto": ex_t}
        for m in methods:
            _, ys = _correr(PASOS[m], f, x0, y0, h_ef, n)
            nm = NOMBRES[m]
            err = abs(ex_t - ys[-1])
            fila[f"y_{nm}"] = ys[-1]
            fila[f"Error_Abs_{nm}"] = err
            fila[f"Error_Rel_%_{nm}"] = err / abs(ex_t) * 100 if ex_t else np.nan
        filas.append(fila)
    df = pd.DataFrame(filas)
    df.attrs["fuente_exacta"] = fuente
    return df


def iteraciones_detalle(f_expr, x0, y0, x_target, metodo, h=None, n=None, params=None,
                        var_x="x", var_y="y"):
    """Tabla paso a paso con las pendientes k de cada iteración."""
    f, _ = construir_f(f_expr, params, var_x, var_y)
    n, h_ef = _malla(x0, x_target, h, n)
    xs, ys = x0 + h_ef * np.arange(n + 1), np.full(n + 1, np.nan)
    ys[0] = y0
    filas = []
    with np.errstate(all="ignore"):
        for i in range(n):
            x, y, h_ = xs[i], ys[i], h_ef
            fila = {"i": i, "x_i": x, "y_i": y}
            if metodo == "euler":
                k1 = f(x, y)
                fila["k1"] = k1
            elif metodo == "heun":
                k1 = f(x, y)
                pred = y + h_ * k1
                k2 = f(x + h_, pred)
                fila.update({"k1": k1, "predictor": pred, "k2": k2, "pend. prom.": (k1 + k2) / 2})
            elif metodo == "rk3":
                k1 = f(x, y); k2 = f(x + h_ / 2, y + h_ / 2 * k1); k3 = f(x + h_, y - h_ * k1 + 2 * h_ * k2)
                fila.update({"k1": k1, "k2": k2, "k3": k3})
            else:
                k1 = f(x, y); k2 = f(x + h_ / 2, y + h_ / 2 * k1)
                k3 = f(x + h_ / 2, y + h_ / 2 * k2); k4 = f(x + h_, y + h_ * k3)
                fila.update({"k1": k1, "k2": k2, "k3": k3, "k4": k4})
            ys[i + 1] = PASOS[metodo](f, x, y, h_)
            fila["y_{i+1}"] = ys[i + 1]
            filas.append(fila)
            if not np.isfinite(ys[i + 1]):
                break
    return pd.DataFrame(filas)
