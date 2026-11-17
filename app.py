"""UI Streamlit - Unidad 3: Integración numérica (Sesión 12: Trapecio, Sesión 13: Simpson)."""
import warnings

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import sympy as sp
import streamlit as st

import ode_solver as od
import simpson_solver as ss
import trapezoidal_solver as ts
from parser_util import evaluar_numero
from teclado import entrada_funcion, limite, parametros_auto

st.set_page_config(page_title="Integración Numérica", layout="wide")

SESION_12 = "📌 Sesión 12: Regla del Trapecio (Tráfico de Red)"
SESION_13 = "📌 Sesión 13: Reglas de Simpson (Terreno e Integración Curva)"
SESION_14 = "📌 Sesión 14: Ecuaciones Diferenciales Ordinarias (PVI)"
sesion = st.sidebar.selectbox("Sesión", [SESION_12, SESION_13, SESION_14])


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
        var = st.selectbox("Variable de integración", ["x", "t", "u"], key="v12")
        expr_str = entrada_funcion("f12", "A*sin(k*x)/(1+x^2)", var, "f(variable, parámetros)")
        params = parametros_auto("f12", expr_str, var)
        c1, c2, c3 = st.columns(3)
        n = c3.number_input("n", min_value=1, max_value=100000, value=10, step=1)
        try:
            a = limite("a", "0", "a12", c1)
            b = limite("b", "5", "b12", c2)
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


def _tramos_idx(xs):
    """Pares (inicio, fin) de índices de cada tramo de paso uniforme."""
    d, out, i = np.diff(xs), [], 0
    while i < len(d):
        j = i
        while j + 1 < len(d) and np.isclose(d[j + 1], d[i], rtol=1e-9, atol=1e-12):
            j += 1
        out.append((i, j + 1))
        i = j + 1
    return out


def vista_sesion_13():
    st.title("Integración Numérica: Reglas de Simpson 1/3 y 3/8")
    with st.expander("Fórmulas"):
        st.latex(r"I_{S1/3}=\frac h3\Big[f_0+4\sum_{impar}f_i+2\sum_{par}f_j+f_n\Big],\quad n\ \text{par}")
        st.latex(r"I_{S3/8}=\frac{3h}8\Big[f_0+3\sum_{i\ne 3k}f_i+2\sum_{k}f_{3k}+f_n\Big],\quad n\ \text{múltiplo de }3")
        st.latex(r"|E_{1/3}|\le \frac{n h^5}{180}\max|f^{(4)}|")
    tab1, tab2, tab3 = st.tabs(["Modo 1: Datos tabulares", "Modo 2: Función continua",
                                "Modo 3: Datos con paso variable"])

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
        var = st.selectbox("Variable", ["x", "t", "u"], key="v13")
        expr_str = entrada_funcion("f13", "exp(x)*cos(x)", var, "f(variable, parámetros)")
        params = parametros_auto("f13", expr_str, var)
        c1, c2, c3, c4 = st.columns(4)
        n = int(c3.number_input("n", min_value=2, max_value=100000, value=6, step=1, key="n13"))
        metodo = c4.selectbox("Método", ["Simpson 1/3", "Simpson 3/8", "Combinado"], key="m13")
        try:
            a = limite("a", "0", "a13", c1)
            b = limite("b", "1.2", "b13", c2)
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

    with tab3:
        st.subheader("Datos con paso variable (varios tramos)")
        st.caption("Si el paso cambia a mitad de los datos, se parte en tramos de paso uniforme y a cada tramo "
                   "se le aplica la regla que corresponde a su número de subintervalos.")
        base3 = pd.DataFrame({"t": [0, 5, 10, 15, 20, 25, 30, 40, 50, 60],
                              "P": [120, 131, 151, 163, 158, 147, 140, 152, 171, 165]}).astype(float)
        df3 = st.data_editor(base3, num_rows="dynamic", width="stretch", key="paso_variable").dropna()
        c1, c2 = st.columns(2)
        factor = c1.number_input("Dividir la integral entre (conversión de unidades)", value=60.0,
                                 min_value=1e-9, format="%g", key="fac3",
                                 help="Ej.: t en minutos y P en kW → dividir entre 60 da kWh")
        dur = c2.text_input("Duración del intervalo en las unidades finales (para el promedio)", "1", key="dur3")
        try:
            df3 = df3.sort_values("t")
            tabla3, total = ss.integrar_por_tramos(df3["t"].to_numpy(float), df3["P"].to_numpy(float))
            st.dataframe(tabla3.style.format({"h": "{:g}", "Integral": "{:.4f}"}), width="stretch", hide_index=True)
            tr = sum(ss.trapecio_datos(df3["P"].to_numpy(float)[a_:b_ + 1], df3["t"].to_numpy(float)[a_:b_ + 1])
                     for a_, b_ in _tramos_idx(df3["t"].to_numpy(float)))
            T = evaluar_numero(dur)
            m1, m2, m3 = st.columns(3)
            m1.metric("Integral total", f"{total:.4f}")
            m2.metric("Convertida (÷ factor)", f"{total / factor:.4f}")
            m3.metric("Promedio sobre la duración", f"{total / factor / T:.4f}")
            st.caption(f"Trapecio compuesto por tramos, para comparar: {tr / factor:.4f} "
                       f"(diferencia {abs(total - tr) / factor:.4f}).")
            ts_ = df3["t"].to_numpy(float)
            fig, ax = plt.subplots(figsize=(9, 4.5))
            ax.plot(ts_, df3["P"], "o-", color="tab:blue", label="datos")
            for k, (a_, b_) in enumerate(_tramos_idx(ts_)):
                px, py = ts_[a_:b_ + 1], df3["P"].to_numpy(float)[a_:b_ + 1]
                ax.fill_between(px, 0, py, alpha=0.3, color=["tab:orange", "tab:green"][k % 2],
                                label=f"{tabla3['Regla'][k]} {tabla3['Tramo'][k]}")
            ax.set_xlabel("t")
            ax.set_ylabel("P")
            ax.grid(alpha=0.3)
            ax.legend()
            st.pyplot(fig)
            plt.close(fig)
        except Exception as e:
            st.error(f"Entrada inválida: {e}")

# ----------------------------------------------------------------------------- Sesión 14
COLORES = {"Euler": "tab:red", "Heun": "tab:orange", "RK3": "tab:green", "RK4": "tab:purple"}
CASO_F = "(x^2-y^2)/(x*y)"
CASO_EXACTA = "sqrt((x^4+7)/(2*x^2))"


def graficar_pvi(df, titulo=""):
    """Curva exacta continua (o de referencia) y cada método como puntos + línea discontinua."""
    fig, ax = plt.subplots(figsize=(9, 4.5))
    x = df["x_i"].to_numpy()
    curva = df.attrs.get("curva", {"x": x, "y": df["y_Exacto"]})
    xd, yd = curva["x"], curva["y"]
    ax.plot(xd, yd, "-", color="tab:blue", lw=2, label="Exacta / referencia")
    for nm, col in COLORES.items():
        if f"y_{nm}" in df:
            ax.plot(x, df[f"y_{nm}"], "o--", color=col, ms=4 if len(x) < 60 else 0, lw=1.2, label=nm)
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.set_title(titulo)
    ax.grid(alpha=0.3)
    ax.legend()
    st.pyplot(fig)
    plt.close(fig)


def seleccion_metodos(key):
    sel = st.multiselect("Métodos", list(od.NOMBRES.values()), default=list(od.NOMBRES.values()), key=key)
    inv = {v: k for k, v in od.NOMBRES.items()}
    return [inv[s] for s in sel]


def formato_pvi(df):
    fmt = {c: "{:.6f}" for c in df.columns if c.startswith(("y_", "Error_Abs")) or c == "x_i"}
    fmt.update({c: "{:.4f}" for c in df.columns if c.startswith("Error_Rel")})
    return df.style.format(fmt, na_rep="—")


def metricas_pvi(df, metodos, etiqueta_exacta):
    fin = df.iloc[-1]
    cols = st.columns(len(metodos) + 1)
    cols[0].metric(etiqueta_exacta, f"{fin['y_Exacto']:.6f}")
    for col, m in zip(cols[1:], metodos):
        nm = od.NOMBRES[m]
        err = fin[f"Error_Rel_%_{nm}"]
        col.metric(nm, f"{fin[f'y_{nm}']:.6f}", f"{err:.4f} % error" if np.isfinite(err) else None,
                   delta_color="off")


def vista_sesion_14():
    st.title("Ecuaciones Diferenciales Ordinarias: Problemas de Valor Inicial")
    tab1, tab2, tab3 = st.tabs(["Guía autónoma (caso de estudio)", "Evaluador personalizado f(x, y)",
                                "Análisis de convergencia (h → 0)"])

    with tab1:
        st.subheader("PVI del caso de estudio")
        st.latex(r"(y^2-x^2)\,dx + x\,y\,dy = 0,\quad y(1)=2"
                 r"\;\Rightarrow\; \frac{dy}{dx}=\frac{x^2-y^2}{xy}=\frac{x}{y}-\frac{y}{x}")
        st.latex(r"y(x)=\sqrt{\dfrac{x^4+7}{2x^2}}\quad\text{(solución exacta)}")
        c1, c2 = st.columns(2)
        h = c1.selectbox("Paso h", [0.1, 0.05, 0.025, 0.01], key="h14g")
        xt = c2.number_input("x objetivo", value=1.2, min_value=1.05, max_value=5.0, step=0.1, key="xt14g")
        df = od.solve_pvi(CASO_F, 1, 2, xt, h, exacta=CASO_EXACTA)
        metricas_pvi(df, list(od.NOMBRES), f"y({xt:g}) exacto")
        st.markdown("#### Tabla comparativa")
        st.dataframe(formato_pvi(df), width="stretch", hide_index=True)
        graficar_pvi(df, f"y(x): exacta vs métodos numéricos (h = {df.attrs['h']:.4g})")
        with st.expander("Paso a paso: Euler y Heun"):
            for m in ("euler", "heun"):
                st.markdown(f"**{od.NOMBRES[m]}**")
                det = od.iteraciones_detalle(CASO_F, 1, 2, xt, m, h=h)
                st.dataframe(det.style.format("{:.6f}", subset=[c for c in det.columns if c != "i"]),
                             width="stretch", hide_index=True)

    with tab2:
        st.subheader("Evaluador personalizado de EDOs")
        st.latex(r"\frac{dy}{dx}=f(x,y),\qquad y(x_0)=y_0")
        expr_str = entrada_funcion("f14", "x - y + 2", ("x", "y"), "f(x, y, parámetros)")
        params = parametros_auto("f14", expr_str, ("x", "y"))
        c1, c2, c3 = st.columns(3)
        modo = st.radio("Definir la malla con", ["Paso h", "Número de pasos n"], horizontal=True, key="modo14")
        try:
            x0 = limite("x₀", "0", "x014", c1)
            y0 = limite("y₀", "1", "y014", c2)
            xt = limite("x objetivo", "1", "xt14", c3)
            if modo == "Paso h":
                h = st.number_input("h", value=0.1, min_value=1e-6, format="%g", key="h14")
                n = None
            else:
                n = int(st.number_input("n", value=10, min_value=1, max_value=200000, step=1, key="n14"))
                h = None
            metodos = seleccion_metodos("met14")
            if not metodos:
                st.warning("Seleccione al menos un método.")
            else:
                _, expr = od.construir_f(expr_str, params)
                st.latex(r"\frac{dy}{dx}=" + sp.latex(expr))
                with st.spinner("Resolviendo…"):
                    df = od.solve_pvi(expr_str, x0, y0, xt, h, metodos, params, n=n)
                st.session_state["pvi_custom"] = dict(expr=expr_str, params=params, x0=x0, y0=y0, xt=xt)
                fuente = df.attrs["fuente_exacta"]
                st.caption(f"n = {df.attrs['n']} pasos, h = {df.attrs['h']:.6g}. Valores exactos: {fuente}.")
                if not np.isfinite(df["y_Exacto"]).all():
                    st.warning("La solución exacta/de referencia no existe en todo el intervalo "
                               "(posible singularidad); los errores no se pueden calcular ahí.")
                metricas_pvi(df, metodos, "y exacto" if "dsolve" in fuente else "y referencia")
                st.dataframe(formato_pvi(df), width="stretch", hide_index=True)
                graficar_pvi(df, "Solución del PVI")
                with st.expander("Paso a paso (tablas de iteración)"):
                    for m in metodos:
                        st.markdown(f"**{od.NOMBRES[m]}**")
                        det = od.iteraciones_detalle(expr_str, x0, y0, xt, m, h=h, n=n, params=params)
                        st.dataframe(det.style.format("{:.6f}", subset=[c for c in det.columns if c != "i"]),
                                     width="stretch", hide_index=True)
        except Exception as e:
            st.session_state.pop("pvi_custom", None)
            st.error(f"Entrada inválida: {e}")

    with tab3:
        st.subheader("Convergencia al disminuir h")
        opciones = ["Caso guía"] + (["Función de la pestaña 2"] if "pvi_custom" in st.session_state else [])
        origen = st.radio("PVI", opciones, horizontal=True, key="orig14")
        if origen == "Caso guía":
            args = dict(f_expr=CASO_F, x0=1, y0=2, x_target=1.2, exacta=CASO_EXACTA)
            st.caption("(y² − x²)dx + xy dy = 0, y(1) = 2, en x = 1.2")
        else:
            c = st.session_state["pvi_custom"]
            args = dict(f_expr=c["expr"], x0=c["x0"], y0=c["y0"], x_target=c["xt"], params=c["params"])
            st.caption(f"y' = {c['expr']}, y({c['x0']:g}) = {c['y0']:g}, en x = {c['xt']:g}")
        h_txt = st.text_input("Valores de h (separados por coma)", "0.1, 0.05, 0.01, 0.005, 0.001", key="hl14")
        try:
            h_list = [float(v) for v in h_txt.split(",") if v.strip()]
            if not h_list or min(h_list) <= 0:
                raise ValueError("h debe ser positivo")
            conv = od.convergence_analysis_pvi(h_list=h_list, **args)
            st.caption(f"Valores exactos: {conv.attrs['fuente_exacta']}.")
            rel = conv[["h", "n"] + [c for c in conv.columns if c.startswith("Error_Rel")]]
            rel = rel.rename(columns=lambda c: c.replace("Error_Rel_%_", "Error rel. % "))
            st.markdown("#### Error relativo (%) en x objetivo")
            fmt = {c: "{:.3e}" for c in rel.columns if c.startswith("Error")}
            fmt["h"] = "{:.4g}"
            st.dataframe(rel.style.format(fmt, na_rep="—"), width="stretch", hide_index=True)
            with st.expander("Tabla completa (valores y errores absolutos)"):
                st.dataframe(conv, width="stretch", hide_index=True)
            fig, ax = plt.subplots(figsize=(8, 4.5))
            for nm, col in COLORES.items():
                e = conv[f"Error_Rel_%_{nm}"].to_numpy()
                ok = np.isfinite(e) & (e > 0)
                if ok.any():
                    ax.loglog(conv["h"][ok], e[ok], "o-", color=col, label=nm)
            ax.set_xlabel("h")
            ax.set_ylabel("Error relativo (%)")
            ax.set_title("Error vs. tamaño de paso (escala log-log)")
            ax.grid(alpha=0.3, which="both")
            ax.legend()
            st.pyplot(fig)
            plt.close(fig)
            st.caption("La pendiente de cada recta indica el orden del método: Euler ≈ 1, Heun ≈ 2, RK3 ≈ 3, "
                       "RK4 ≈ 4. Las curvas que se aplanan o desaparecen llegaron al límite de precisión de la máquina.")
        except Exception as e:
            st.error(f"Entrada inválida: {e}")


if sesion == SESION_12:
    vista_sesion_12()
elif sesion == SESION_13:
    vista_sesion_13()
else:
    vista_sesion_14()
