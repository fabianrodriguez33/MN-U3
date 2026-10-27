"""UI Streamlit - Sesión 12: Integración numérica por Regla del Trapecio."""
import matplotlib.pyplot as plt
import numpy as np
import streamlit as st

import trapezoidal_solver as ts

st.set_page_config(page_title="Regla del Trapecio", layout="wide")
st.title("Integración Numérica: Regla del Trapecio Compuesto")

modo = st.sidebar.radio(
    "Modo", ["1. Caso Guía Autónoma (Sesión 12)", "2. Integrador Personalizado"]
)


def graficar(f, a, b, x, fx, titulo):
    xx = np.linspace(a, b, 1000)
    fig, ax = plt.subplots(figsize=(9, 4.5))
    ax.plot(xx, f(xx), color="tab:blue", label="f(x)")
    ax.plot(x, fx, "o", color="tab:red", ms=4 if len(x) < 60 else 1.5)
    for i in range(len(x) - 1):
        ax.fill([x[i], x[i], x[i + 1], x[i + 1]], [0, fx[i], fx[i + 1], 0],
                facecolor="tab:orange", edgecolor="k", alpha=0.35, lw=0.6 if len(x) < 60 else 0.1)
    ax.axhline(0, color="gray", lw=0.6)
    ax.set_title(titulo)
    ax.legend()
    ax.grid(alpha=0.3)
    st.pyplot(fig)
    plt.close(fig)


if modo.startswith("1"):
    st.subheader("Estimación del tráfico de red en un servidor web")
    st.latex(r"R(t)=\frac{10+5\sin(\pi t)}{4+e^{0.15t}},\qquad D=\int_0^{12}R(t)\,dt")
    n = st.sidebar.slider("Subintervalos n", 1, 200, 4)
    a, b = 0.0, 12.0
    x, fx, I, tabla = ts.trapecio_compuesto(ts.R_trafico, a, b, n)
    exacto = ts.valor_exacto(ts.R_trafico, a, b)
    err = abs(exacto - I)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("h", f"{(b - a) / n:.4f} s")
    c2.metric("D (trapecio)", f"{I:.6f} Mb")
    c3.metric("Valor exacto", f"{exacto:.6f} Mb")
    c4.metric("Error relativo", f"{err / exacto * 100:.4f} %")
    st.write(f"Error absoluto real: **{err:.6f} Mb**")
    graficar(ts.R_trafico, a, b, x, fx, f"Trapecio compuesto, n = {n}")
    st.markdown("#### Malla y evaluaciones")
    st.dataframe(tabla, use_container_width=True, hide_index=True)
    st.markdown("#### Tabla de convergencia")
    conv, _ = ts.analisis_convergencia(ts.R_trafico, a, b, [4, 10, 50, 100, 1000], exacto)
    st.dataframe(conv.style.format({"h": "{:.4f}", "Integral": "{:.6f}",
                                    "Error absoluto": "{:.6f}", "Error relativo (%)": "{:.4f}"}),
                 use_container_width=True, hide_index=True)
else:
    st.subheader("Integrador personalizado")
    st.caption("Use ^ o ** para potencias; funciones: sin, cos, exp, log, sqrt, pi, e…")
    col1, col2 = st.columns(2)
    expr_str = col1.text_input("f(x, parámetros)", "A*sin(k*x)/(1+x^2)")
    var = col2.text_input("Variable de integración", "x")
    params_txt = st.text_input("Parámetros (nombre=valor, separados por coma)", "A=2, k=3")
    c1, c2, c3 = st.columns(3)
    a = c1.number_input("a", value=0.0)
    b = c2.number_input("b", value=5.0)
    n = c3.number_input("n", min_value=1, max_value=100000, value=10, step=1)
    try:
        params = {}
        for p in filter(None, (s.strip() for s in params_txt.split(","))):
            k, v = p.split("=")
            params[k.strip()] = float(v)
        f, expr = ts.evaluador_simbolico(expr_str, var.strip(), params)
        st.latex("f(" + var + ")=" + __import__("sympy").latex(expr))
        n = int(n)
        x, fx, I, tabla = ts.trapecio_compuesto(f, a, b, n)
        exacto = ts.valor_exacto(f, a, b)
        err = abs(exacto - I)
        m1, m2, m3 = st.columns(3)
        m1.metric("Trapecio compuesto", f"{I:.8f}")
        m2.metric("Referencia (quad)", f"{exacto:.8f}")
        m3.metric("Error absoluto", f"{err:.3e}")
        try:
            f2 = ts.max_segunda_derivada(expr_str, var.strip(), a, b, params)
            st.write(f"Cota teórica (ec. 4): **{ts.cota_error_compuesta(f2, a, b, n):.3e}** "
                     f"(max|f''| ≈ {f2:.4g})")
        except Exception:
            pass
        graficar(f, a, b, x, fx, f"Trapecio compuesto, n = {n}")
        with st.expander("Tabla de iteraciones"):
            st.dataframe(tabla, use_container_width=True, hide_index=True)
        st.markdown("#### Convergencia")
        conv, _ = ts.analisis_convergencia(f, a, b, [4, 10, 50, 100, 1000], exacto)
        st.dataframe(conv, use_container_width=True, hide_index=True)
    except Exception as e:
        st.error(f"Entrada inválida: {e}")
