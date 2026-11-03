"""Componentes Streamlit: teclado en pantalla para funciones, parámetros automáticos y límites."""
import streamlit as st

from parser_util import evaluar_numero, parametros_libres

_FUNCS = ("sin(", "cos(", "tan(", "asin(", "acos(", "atan(", "sinh(", "cosh(", "tanh(",
          "exp(", "ln(", "log(", "sqrt(", "abs(")


def _insertar(key, texto):
    st.session_state[key] = st.session_state.get(key, "") + texto


def _borrar(key):
    s = st.session_state.get(key, "")
    for f in _FUNCS:  # quita una función completa, p. ej. "sin("
        if s.endswith(f):
            st.session_state[key] = s[: -len(f)]
            return
    st.session_state[key] = s[:-1]


def _limpiar(key):
    st.session_state[key] = ""


def entrada_funcion(key, default, var="x", etiqueta="Función"):
    """Campo de texto + teclado de botones. Retorna la expresión escrita (str)."""
    k = f"{key}_expr"
    if k not in st.session_state:
        st.session_state[k] = default
    st.text_input(etiqueta, key=k, help="Puede escribirla con el teclado o con el teclado del equipo. "
                  "Acepta ^ para potencias, 2x para 2·x, ln, sen, pi, e.")
    with st.expander("⌨️ Teclado de funciones", expanded=True):
        filas = [
            ["7", "8", "9", "(", ")", "^", "⌫"],
            ["4", "5", "6", "+", "-", "*", "/"],
            ["1", "2", "3", ".", var, "pi", "e"],
            ["0", "sin(", "cos(", "tan(", "exp(", "ln(", "sqrt("],
            ["abs(", "asin(", "acos(", "atan(", "sinh(", "cosh(", "C"],
        ]
        for i, fila in enumerate(filas):
            cols = st.columns(len(fila))
            for j, (col, b) in enumerate(zip(cols, fila)):
                etq = b[:-1] if len(b) > 1 and b.endswith("(") else b
                if b == "⌫":
                    col.button(etq, key=f"{key}_b{i}{j}", on_click=_borrar, args=(k,), width="stretch")
                elif b == "C":
                    col.button(etq, key=f"{key}_b{i}{j}", on_click=_limpiar, args=(k,), width="stretch")
                else:
                    col.button(etq, key=f"{key}_b{i}{j}", on_click=_insertar, args=(k, b), width="stretch")
        st.caption("Los botones agregan al final del texto. Para otro lugar, edite el campo directamente.")
    return st.session_state[k]


def parametros_auto(key, expr_str, var="x"):
    """Detecta parámetros (A, k, ...) y crea un campo numérico para cada uno. Retorna dict."""
    nombres = parametros_libres(expr_str, var)
    valores = {}
    if nombres:
        st.markdown("**Parámetros detectados**")
        cols = st.columns(min(len(nombres), 4))
        for i, n in enumerate(nombres):
            valores[n] = cols[i % len(cols)].number_input(n, value=1.0, format="%g", key=f"{key}_p_{n}")
    return valores


def limite(etiqueta, default, key, col=None):
    """Límite como texto: acepta números o expresiones como pi/2, sqrt(2), 2*pi."""
    c = col or st
    txt = c.text_input(etiqueta, value=default, key=key)
    try:
        return evaluar_numero(txt)
    except Exception:
        raise ValueError(f"Límite '{etiqueta}' inválido: '{txt}'")
