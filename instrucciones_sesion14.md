# Especificación de Requerimientos: Sesión 14 (Ecuaciones Diferenciales Ordinarias - PVI)

## Contexto del Proyecto
Este documento contiene las instrucciones precisas para que **Claude Code** extienda la aplicación web interactiva en **Python + Streamlit.io** ubicada en `D:\MN-U3`.
Las sesiones anteriores (**Sesión 12: Método del Trapecio** y **Sesión 13: Reglas de Simpson**) deben permanecer **100% funcionales e intactas**.

---

## 1. Estructura de Archivos del Proyecto (`D:\MN-U3`)

```text
D:\MN-U3
├── app.py                      # UI Streamlit (Navegación: Sesión 12 / Sesión 13 / Sesión 14)
├── trapezoidal_solver.py       # Lógica Sesión 12 (Trapecio simple/compuesto, convergencia)
├── simpson_solver.py           # Lógica Sesión 13 (Simpson 1/3, 3/8, combinado, datos tabulares)
├── ode_solver.py               # Lógica Sesión 14 (Euler, Heun/Euler Mejorado, RK3, RK4, PVI) [NUEVO]
├── teclado.py                  # Teclado matemático en pantalla
├── parser_util.py              # Parser tolerante a expresiones matemáticas en 2 variables f(x,y)
├── instrucciones_sesion12.md   # Especificación Sesión 12
├── instrucciones_sesion13.md   # Especificación Sesión 13
├── instrucciones_sesion14.md   # Especificación Sesión 14 [NUEVO]
├── README.md                   # Documentación global del proyecto
├── requirements.txt            # streamlit, numpy, pandas, matplotlib, sympy, scipy
├── .gitignore
└── .claude/launch.json         # Configuración del servidor local (puerto 8501)
```

---

## 2. Parte Manual (Solución Analítica y Paso a Paso para Hoja/Enunciado)

### 2.1 Enunciado del Problema (PVI)
Dado el problema de valor inicial:
$$(y^2 - x^2)\,dx + x\,y\,dy = 0 \quad \text{con} \quad y(1) = 2$$

Reordenando a la forma estándar $\frac{dy}{dx} = f(x, y)$:
$$\frac{dy}{dx} = \frac{x^2 - y^2}{x\,y} = \frac{x}{y} - \frac{y}{x}$$

Objetivo: Aproximar manualmente $y(1.2)$ usando un tamaño de paso $h = 0.1$ (pasos en $x_0 = 1.0$, $x_1 = 1.1$, $x_2 = 1.2$) mediante:
1. Método de Euler.
2. Método de Euler Mejorado (Heun).
3. Comparación de errores relativos respecto al valor verdadero.

---

### 2.2 Valor Verdadero (Solución Analítica Exacta)
Haciendo la sustitución $u = y^2 \Rightarrow \frac{du}{dx} = 2y \frac{dy}{dx}$:
$$\frac{x}{2} \frac{du}{dx} + u = x^2 \implies \frac{du}{dx} + \frac{2}{x} u = 2x$$

Factor integrante $\mu(x) = x^2$:
$$\frac{d}{dx}(x^2 u) = 2x^3 \implies x^2 u = \frac{1}{2} x^4 + C \implies u(x) = \frac{x^4 + 2C}{2x^2}$$

Con $y(1) = 2 \Rightarrow u(1) = 4$:
$$4 = \frac{1 + 2C}{2} \implies 2C = 7 \implies y(x) = \sqrt{\frac{x^4 + 7}{2x^2}}$$

#### Evaluación de Puntos Exactos:
* $y(1.0) = 2.000000$
* $y(1.1) = \sqrt{\frac{1.1^4 + 7}{2(1.1^2)}} = \sqrt{\frac{1.4641 + 7}{2.42}} = \sqrt{3.497562} = \mathbf{1.870177}$
* $y(1.2) = \sqrt{\frac{1.2^4 + 7}{2(1.2^2)}} = \sqrt{\frac{2.0736 + 7}{2.88}} = \sqrt{3.150556} = \mathbf{1.774980}$

---

### 2.3 Desarrollo Paso a Paso: Método de Euler ($h = 0.1$)

Fórmula: $y_{i+1} = y_i + h \cdot f(x_i, y_i)$ donde $f(x, y) = \frac{x^2 - y^2}{x y}$.

#### Paso 1 ($x_0 = 1.0, y_0 = 2.000000 \to x_1 = 1.1$):
* $f(1.0, 2.0) = \frac{1.0^2 - 2.0^2}{1.0 \times 2.0} = \frac{-3.0}{2.0} = -1.500000$
* $y_1 = 2.000000 + 0.1 \times (-1.500000) = \mathbf{1.850000}$

#### Paso 2 ($x_1 = 1.1, y_1 = 1.850000 \to x_2 = 1.2$):
* $f(1.1, 1.85) = \frac{1.1^2 - 1.85^2}{1.1 \times 1.85} = \frac{1.21 - 3.4225}{2.0350} = -1.087224$
* $y_2 = 1.850000 + 0.1 \times (-1.087224) = \mathbf{1.741278}$

#### Error Relativo Euler en $x = 1.2$:
$$\text{Error Relativo (\%)} = \frac{|1.741278 - 1.774980|}{1.774980} \times 100\% = \mathbf{1.8988\%}$$

---

### 2.4 Desarrollo Paso a Paso: Método de Euler Mejorado / Heun ($h = 0.1$)

Fórmula Predictor-Corrector:
$$\begin{aligned}
y_{i+1}^{(0)} &= y_i + h \cdot f(x_i, y_i) \\
y_{i+1} &= y_i + \frac{h}{2} \left[ f(x_i, y_i) + f(x_{i+1}, y_{i+1}^{(0)}) \right]
\end{aligned}$$

#### Paso 1 ($x_0 = 1.0, y_0 = 2.000000 \to x_1 = 1.1$):
1. $f(1.0, 2.0) = -1.500000$
2. Predictor: $y_1^{(0)} = 1.850000$
3. Pendiente final: $f(1.1, 1.850000) = -1.087224$
4. Pendiente promedio: $f_{\text{prom}} = \frac{-1.500000 + (-1.087224)}{2} = -1.293612$
5. Corrector: $y_1 = 2.000000 + 0.1 \times (-1.293612) = \mathbf{1.870639}$

#### Paso 2 ($x_1 = 1.1, y_1 = 1.870639 \to x_2 = 1.2$):
1. $f(1.1, 1.870639) = \frac{1.21 - 3.499290}{2.057703} = -1.112546$
2. Predictor: $y_2^{(0)} = 1.870639 + 0.1 \times (-1.112546) = 1.759384$
3. Pendiente final: $f(1.2, 1.759384) = \frac{1.44 - 3.095430}{2.111261} = -0.784097$
4. Pendiente promedio: $f_{\text{prom}} = \frac{-1.112546 + (-0.784097)}{2} = -0.948321$
5. Corrector: $y_2 = 1.870639 + 0.1 \times (-0.948321) = \mathbf{1.775807}$

#### Error Relativo Heun en $x = 1.2$:
$$\text{Error Relativo (\%)} = \frac{|1.775807 - 1.774980|}{1.774980} \times 100\% = \mathbf{0.0465\%}$$

---

### 2.5 Tabla Comparativa de Resultados Manuales

| $x_i$ | $y_{\text{Exacto}}$ | $y_{\text{Euler}}$ | Error Abs. Euler | Error Rel. Euler (%) | $y_{\text{Heun}}$ | Error Abs. Heun | Error Rel. Heun (%) |
|---|---|---|---|---|---|---|---|
| **1.0** | 2.000000 | 2.000000 | 0.000000 | 0.0000% | 2.000000 | 0.000000 | 0.0000% |
| **1.1** | 1.870177 | 1.850000 | 0.020177 | 1.0789% | 1.870639 | 0.000462 | 0.0247% |
| **1.2** | 1.774980 | 1.741278 | 0.033702 | **1.8988%** | 1.775807 | 0.000827 | **0.0465%** |

---

## 3. Especificación de Software (Streamlit en `D:\MN-U3`)

### 3.1 Módulo `ode_solver.py`
Crear `ode_solver.py` con las siguientes funciones puras y parametrizables:

1. **`euler_step(f, x, y, h)`**: Retorna $y_{i+1}$ mediante Euler.
2. **`heun_step(f, x, y, h)`**: Retorna $y_{i+1}$ mediante Heun (Euler Mejorado).
3. **`rk3_step(f, x, y, h)`**: Retorna $y_{i+1}$ mediante Runge-Kutta de 3er orden:
   $$\begin{aligned}
   k_1 &= f(x, y) \\
   k_2 &= f\left(x + \frac{h}{2},\, y + \frac{h}{2} k_1\right) \\
   k_3 &= f(x + h,\, y - h k_1 + 2 h k_2) \\
   y_{i+1} &= y + \frac{h}{6}(k_1 + 4 k_2 + k_3)
   \end{aligned}$$
4. **`rk4_step(f, x, y, h)`**: Retorna $y_{i+1}$ mediante Runge-Kutta de 4to orden:
   $$\begin{aligned}
   k_1 &= f(x, y) \\
   k_2 &= f\left(x + \frac{h}{2},\, y + \frac{h}{2} k_1\right) \\
   k_3 &= f\left(x + \frac{h}{2},\, y + \frac{h}{2} k_2\right) \\
   k_4 &= f(x + h,\, y + h k_3) \\
   y_{i+1} &= y + \frac{h}{6}(k_1 + 2 k_2 + 2 k_3 + k_4)
   \end{aligned}$$
5. **`solve_pvi(f_expr, x0, y0, x_target, h, methods=['euler', 'heun', 'rk3', 'rk4'], params=None)`**:
   - Evalúa múltiples métodos en simultáneo.
   - Intenta resolver analíticamente la EDO usando `sympy.dsolve` para calcular errores exactos automáticamente.
   - Retorna un `pandas.DataFrame` con la malla de puntos $x_i$, los valores aproximados, exactos y errores absolutos/relativos.
6. **`convergence_analysis_pvi(f_expr, x0, y0, x_target, h_list)`**:
   - Genera la tabla de convergencia al disminuir $h$ ($h \in \{0.1, 0.05, 0.01, 0.005, 0.001\}$).

---

### 3.2 Modificación de `app.py`
1. **Navegación Lateral (`st.sidebar.selectbox`)**:
   - `Sesión 12: Regla del Trapecio`
   - `Sesión 13: Reglas de Simpson`
   - `Sesión 14: Ecuaciones Diferenciales Ordinarias (PVI)` [NUEVO]

2. **Pestañas de la Sesión 14 en Streamlit**:
   * **Pestaña 1: Guía Autónoma (PVI Caso de Estudio)**
     - Muestra el enunciado $(y^2 - x^2)dx + x y dy = 0$, $y(1) = 2$, $x=1.2$, $h=0.1$.
     - Despliega la tabla comparativa completa (Euler, Heun, RK3, RK4 vs Exacto).
     - Gráfico comparativo de curvas $y(x)$ vs $x$ usando `matplotlib` con la solución exacta como curva continua y los métodos numéricos como puntos/líneas discontinuas.
   * **Pestaña 2: Evaluador Personalizado de EDOs ($f(x, y)$)**
     - Permite ingresar cualquier función $f(x, y)$ (ej. `(x^2 - y^2)/(x*y)`, `exp(x+y)`, `x - y + 2`).
     - Soporta múltiples variables/parámetros dinámicos (ej. coeficientes $a, b, c$).
     - Entrada intuitiva con `teclado.py` y parsing seguro con `parser_util.py`.
     - Permite configurar $x_0$, $y_0$, $x_{\text{target}}$ y $h$ o número de pasos $n$.
     - Muestra paso a paso expandible con tablas de iteración.
   * **Pestaña 3: Análisis de Convergencia ($h \to 0$)**
     - Tabla de error relativo (%) comparando Euler, Heun, RK3 y RK4 para variados valores de $h$.
     - Gráfico logarítmico del error en función del paso $h$.

---

## 4. Actualización del README y Control de Versiones Git

### 4.1 Requerimientos para `README.md`
Actualizar `README.md` para incluir el módulo de la Sesión 14:
* Resumen de las 3 sesiones (Trapecio, Simpson, PVI/Runge-Kutta).
* Comandos de instalación y ejecución (`streamlit run app.py`).
* Descripción de los métodos numéricos soportados (Euler, Heun, RK3, RK4).

### 4.2 Instrucciones de Git (Sin Coautoría)
Ejecutar el commit y push **omitir explícitamente cualquier metadato de coautoría (`Co-authored-by`)**:

```bash
git add .
git commit -m "feat(sesion14): agregar modulo PVI (Euler, Heun, RK3, RK4) e integrar en Streamlit"
git push origin main
```
