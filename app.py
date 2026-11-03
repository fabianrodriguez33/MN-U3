"""UI Streamlit - Unidad 3: Integración numérica (Sesión 12: Trapecio, Sesión 13: Simpson)."""
import warnings

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import sympy as sp
import streamlit as st

import simpson_solver as ss
import trapezoidal_solver as ts

st.set_page_config(page_title="Integración Numérica", layout="wide")

SESION_12 = "📌 Sesión 12: Regla del Trapecio (Tráfico de Red)"
SESION_13 = "📌 Sesión 13: Reglas de Simpson (Terreno e Integración Curva)"
sesion = st.sidebar.radio("Sesión", [SESION_12, SESION_13])


# ----------------------------------------------------------------------------- Sesión 12
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


def vista_sesion_12():
    st.title("Integración Numérica: Regla del Trapecio Compuesto")
    modo = st.sidebar.radio(
        "Modo", ["1. Caso Guía Autónoma (Sesión 12)", "2. Integrador Personalizado"], key="modo12"
    )
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
        st.dataframe(tabla, width="stretch", hide_index=True)
        st.markdown("#### Tabla de convergencia")
        conv, _ = ts.analisis_convergencia(ts.R_trafico, a, b, [4, 10, 50, 100, 1000], exacto)
        st.dataframe(conv.style.format({"h": "{:.4f}", "Integral": "{:.6f}",
                                        "Error absoluto": "{:.6f}", "Error relativo (%)": "{:.4f}"}),
                     width="stretch", hide_index=True)
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
            params = parse_params(params_txt)
            f, expr = ts.evaluador_simbolico(expr_str, var.strip(), params)
            st.latex("f(" + var + ")=" + sp.latex(expr))
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
                st.dataframe(tabla, width="stretch", hide_index=True)
            st.markdown("#### Convergencia")
            conv, _ = ts.analisis_convergencia(f, a, b, [4, 10, 50, 100, 1000], exacto)
            st.dataframe(conv, width="stretch", hide_index=True)
        except Exception as e:
            st.error(f"Entrada inválida: {e}")


def parse_params(txt):
    params = {}
    for p in filter(None, (s.strip() for s in txt.split(","))):
        k, v = p.split("=")
        params[k.strip()] = float(v)
    return params


# ----------------------------------------------------------------------------- Sesión 13
def graficar_simpson(xs, ys, metodo, titulo, f=None):
    """Curva (o polilínea de datos), puntos y polinomio interpolante de cada tramo."""
    fig, ax = plt.subplots(figsize=(9, 4.5))
    if f is not None:
        xx = np.linspace(xs[0], xs[-1], 1000)
        ax.plot(xx, f(xx), color="tab:blue", lw=1.2, label="f(x)")
    else:
        ax.plot(xs, ys, color="tab:blue", lw=1.2, label="perfil medido")
    colores = ["tab:orange", "tab:green"]
    for k, (x0, x1, coef) in enumerate(ss.segmentos_interpolantes(xs, ys, metodo)):
        px = np.linspace(x0, x1, 100)
        py = np.polyval(coef, px)
        ax.fill_between(px, 0, py, color=colores[k % 2], alpha=0.3)
        ax.plot(px, py, "--", color="k", lw=0.9, label="polinomio interpolante" if k == 0 else None)
    ax.plot(xs, ys, "o", color="tab:red", ms=4 if len(xs) < 40 else 1.5)
    ax.set_title(titulo)
    ax.grid(alpha=0.3)
    ax.legend()
    st.pyplot(fig)
    plt.close(fig)


def vista_sesion_13():
    st.title("Integración Numérica: Reglas de Simpson 1/3 y 3/8")
    with st.expander("Fórmulas"):
        st.latex(r"I_{S1/3}=\frac h3\Big[f_0+4\sum_{impar}f_i+2\sum_{par}f_j+f_n\Big],\quad n\ \text{par}")
        st.latex(r"I_{S3/8}=\frac{3h}8\Big[f_0+3\sum_{i\ne 3k}f_i+2\sum_{k}f_{3k}+f_n\Big],\quad n\ \text{múltiplo de }3")
        st.latex(r"|E_{1/3}|\le \frac{n h^5}{180}\max|f^{(4)}|")
    tab1, tab2 = st.tabs(["Modo 1: Datos tabulares", "Modo 2: Función continua"])

    with tab1:
        st.subheader("Perfil de elevación de un terreno")
        base = pd.DataFrame({"x (m)": [0, 5, 10, 15, 20, 25, 30],
                             "y (m)": [2.1, 2.4, 2.9, 3.0, 2.8, 2.5, 2.2]}).astype(float)
        df = st.data_editor(base, num_rows="dynamic", width="stretch", key="terreno")
        df = df.dropna()
        if len(df) < 3:
            st.warning("Ingrese al menos 3 puntos.")
        else:
            xs, ys = df["x (m)"].to_numpy(float), df["y (m)"].to_numpy(float)
            try:
                N = len(xs) - 1
                res = {"Trapecio compuesto": ss.trapecio_datos(ys, xs)}
                res["Simpson 1/3"] = ss.simpson_13_compuesto(ys, x=xs)[2] if N % 2 == 0 else None
                res["Simpson 3/8"] = ss.simpson_38_compuesto(ys, x=xs)[2] if N % 3 == 0 else None
                res["Simpson combinado"] = ss.simpson_combinado(ys, xs)[2]
                comp = pd.DataFrame({"Método": list(res), "Área (m²)": list(res.values())})
                comp["Nota"] = ["", "requiere n par" if res["Simpson 1/3"] is None else "",
                                "requiere n múltiplo de 3" if res["Simpson 3/8"] is None else "", ""]
                st.write(f"n = {N} subintervalos, h = {(xs[1] - xs[0]):g} m")
                st.dataframe(comp.style.format({"Área (m²)": "{:.4f}"}, na_rep="—"),
                             width="stretch", hide_index=True)
                disp = [m for m, v in [("13", res["Simpson 1/3"]), ("38", res["Simpson 3/8"]),
                                       ("combinado", res["Simpson combinado"])] if v is not None]
                nombres = {"13": "Simpson 1/3", "38": "Simpson 3/8", "combinado": "Simpson combinado"}
                m = st.radio("Graficar con", disp, format_func=nombres.get, horizontal=True, key="m_terreno")
                graficar_simpson(xs, ys, m, f"Perfil de elevación — {nombres[m]}")
            except ValueError as e:
                st.error(str(e))

    with tab2:
        st.subheader("Función continua y personalizada")
        c1, c2 = st.columns([3, 1])
        expr_str = c1.text_input("f(var, parámetros)", "exp(x)*cos(x)", key="e13")
        var = c2.selectbox("Variable", ["x", "t", "u"], key="v13")
        params_txt = st.text_input("Parámetros (nombre=valor, separados por coma)", "", key="p13")
        c1, c2, c3, c4 = st.columns(4)
        a = c1.number_input("a", value=0.0, key="a13")
        b = c2.number_input("b", value=1.2, key="b13")
        n = int(c3.number_input("n", min_value=2, max_value=100000, value=6, step=1, key="n13"))
        metodo = c4.selectbox("Método", ["Simpson 1/3", "Simpson 3/8", "Combinado"], key="m13")
        try:
            params = parse_params(params_txt) if params_txt.strip() else {}
            f, expr = ss.evaluador_simbolico(expr_str, params, var)
            st.latex(f"f({var})=" + sp.latex(expr))
            exacto = ts.valor_exacto(f, a, b)
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                if metodo == "Simpson 1/3":
                    xs, ys, I, tabla = ss.simpson_13_compuesto(f, a, b, n)
                    clave = "13" if n % 2 == 0 else "combinado"
                    if n % 2:
                        st.info("n impar: se aplicó Simpson combinado (1/3 + 3/8).")
                elif metodo == "Simpson 3/8":
                    xs, ys, I, tabla = ss.simpson_38_compuesto(f, a, b, n)
                    clave = "38"
                else:
                    xs = np.linspace(a, b, n + 1)
                    xs, ys, I, tabla = ss.simpson_combinado(f(xs), xs)
                    clave = "combinado"
            err = abs(exacto - I)
            m1, m2, m3, m4 = st.columns(4)
            m1.metric(metodo, f"{I:.6f}")
            m2.metric("Referencia (quad)", f"{exacto:.6f}")
            m3.metric("Error absoluto", f"{err:.3e}")
            m4.metric("Error relativo", f"{err / abs(exacto) * 100:.4f} %" if exacto else "—")
            try:
                cota, m4d = ss.cota_error_13(expr_str, a, b, n if n % 2 == 0 else n + 1, params, var)
                st.caption(f"Cota teórica Simpson 1/3 (n par): {cota:.3e}  (max|f⁽⁴⁾| ≈ {m4d:.4g})")
            except Exception:
                pass
            graficar_simpson(xs, ys, clave, f"{metodo}, n = {n}", f)
            with st.expander("Malla, evaluaciones y pesos"):
                st.dataframe(tabla, width="stretch", hide_index=True)
            st.markdown("#### Tabla de convergencia")
            conv, _ = ss.analisis_convergencia_simpson(expr_str, a, b, [2, 4, 6, 10, 20, 50, 100], params, var)
            st.dataframe(conv.style.format({"h": "{:.4f}", "I_Simpson13": "{:.6f}", "I_Simpson38": "{:.6f}",
                                            "Error_Abs_13": "{:.3e}", "Error_Rel_%_13": "{:.4e}"}, na_rep="—"),
                         width="stretch", hide_index=True)
            st.caption("— : el método no aplica para ese n (1/3 requiere n par; 3/8 requiere n múltiplo de 3).")
        except Exception as e:
            st.error(f"Entrada inválida: {e}")


if sesion == SESION_12:
    vista_sesion_12()
else:
    vista_sesion_13()
