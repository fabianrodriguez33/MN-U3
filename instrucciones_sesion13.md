# ESPECIFICACIÓN TÉCNICA: SESIÓN 13 - REGLAS DE SIMPSON E INTEGRACIÓN NUMÉRICA

## 1. OBJETIVO
Guiar a Claude Code en la implementación del módulo de la **Sesión 13 (Reglas de Simpson 1/3 y 3/8)** en el proyecto `D:\MN-U3`. El módulo debe integrarse a la aplicación Streamlit existente sin alterar la funcionalidad previa de la Sesión 12 (Regla del Trapecio).

---

## 2. ESTRUCTURA DEL PROYECTO
El proyecto mantendrá y expandirá la siguiente arquitectura modular:

```
D:\MN-U3
├── app.py                      # UI Streamlit (Navegación: Sesión 12 / Sesión 13)
├── trapezoidal_solver.py       # Módulo Sesión 12: Trapecio Simple/Compuesto
├── simpson_solver.py           # Módulo Sesión 13: Simpson 1/3, 3/8, Combinado y Datos Tabulares
├── instrucciones_sesion12.md   # Especificación Sesión 12
├── instrucciones_sesion13.md   # Especificación Sesión 13 (Este archivo)
├── README.md                   # Documentación profesional del proyecto
├── requirements.txt            # streamlit, numpy, pandas, matplotlib, sympy, scipy
├── .gitignore
└── .claude/launch.json         # Configuración del servidor Streamlit (puerto 8501)
```

---

## 3. FUNDAMENTACIÓN TEÓRICA Y FÓRMULAS (SESIÓN 13)

### 3.1. Regla de Simpson 1/3 Simple ($n = 2$)
Aproxima $f(x)$ mediante un polinomio interpolante de grado 2 (parábola) que pasa por 3 puntos igualmente espaciados $x_0, x_1, x_2$ con $h = \frac{b-a}{2}$:
$$I_{S1/3} = \frac{h}{3} \left[ f(x_0) + 4 f(x_1) + f(x_2) \right]$$
**Cota superior del error:**
$$|E_s| \le \frac{h^5}{90} \cdot \max_{x \in [a,b]} |f^{(4)}(x)|$$

### 3.2. Regla de Simpson 1/3 Compuesta ($n$ par)
Divide el intervalo $[a,b]$ en $n$ subintervalos de ancho $h = \frac{b-a}{n}$ (donde $n$ debe ser un número par):
$$I_{S1/3,C} = \frac{h}{3} \left[ f(x_0) + 4 \sum_{i=1,3,5}^{n-1} f(x_i) + 2 \sum_{j=2,4,6}^{n-2} f(x_j) + f(x_n) \right]$$
**Cota superior del error:**
$$|E_s| \le \frac{n \cdot h^5}{180} \cdot \max_{x \in [a,b]} |f^{(4)}(x)|$$

### 3.3. Regla de Simpson 3/8 Simple ($n = 3$)
Aproxima $f(x)$ mediante un polinomio interpolante de grado 3 pasando por 4 puntos $x_0, x_1, x_2, x_3$ con $h = \frac{b-a}{3}$:
$$I_{S3/8} = \frac{3h}{8} \left[ f(x_0) + 3 f(x_1) + 3 f(x_2) + f(x_3) \right]$$
**Cota superior del error:**
$$E_t = -\frac{(b-a)^5}{6480} f^{(4)}(\xi)$$

### 3.4. Regla de Simpson 3/8 Compuesta ($n$ múltiplo de 3)
Aplica la regla de 3/8 cuando $n$ es múltiplo de 3:
$$I_{S3/8,C} = \frac{3h}{8} \left[ f(x_0) + 3 \sum_{i \neq 3k} f(x_i) + 2 \sum_{k=1}^{(n/3)-1} f(x_{3k}) + f(x_n) \right]$$

### 3.5. Regla Combinada de Simpson (Cualquier $n$)
Para casos donde $n$ no es estrictamente par ni múltiplo de 3, o para máxima precisión, se aplica Simpson 1/3 en los primeros subintervalos pares y Simpson 3/8 en los últimos 3 subintervalos.

---

## 4. CASOS DE ESTUDIO Y RESULTADOS DE REFERENCIA (SIN INVENTAR DATOS)

### Caso 1: Estimación del Área Superficial de Terreno (Perfil de Elevación - Datos Tabulares)
Un terreno fue medido transversalmente cada 5 metros en una distancia total de 30 metros ($n = 6$, $h = 5\text{ m}$):

| Distancia $x$ (m) | 0 | 5 | 10 | 15 | 20 | 25 | 30 |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Elevación $y$ (m)** | 2.1 | 2.4 | 2.9 | 3.0 | 2.8 | 2.5 | 2.2 |

#### Procedimiento y Resultados Calculados:
1. **Simpson 1/3 Compuesto ($n=6$, $h=5$):**
   $$I = \frac{5}{3} \left[ 2.1 + 4(2.4 + 3.0 + 2.5) + 2(2.9 + 2.8) + 2.2 \right] = \frac{5}{3} [2.1 + 31.6 + 11.4 + 2.2] = \mathbf{78.8333\text{ m}^2}$$
2. **Simpson 3/8 Compuesto ($n=6$, $h=5$):**
   $$I = \frac{15}{8} \left[ 2.1 + 3(2.4 + 2.9) + 2(3.0) + 3(2.8 + 2.5) + 2.2 \right] = \frac{15}{8} [2.1 + 15.9 + 6.0 + 15.9 + 2.2] = \mathbf{78.9375\text{ m}^2}$$
3. **Comparación con Trapecio Compuesto ($n=6$):**
   $$I_{\text{Trap}} = \frac{5}{2} \left[ 2.1 + 2(2.4 + 2.9 + 3.0 + 2.8 + 2.5) + 2.2 \right] = \mathbf{78.7500\text{ m}^2}$$

### Caso 2: Evaluación Teórica de Funciones Continuas

1. **Integral $I = \int_0^{1.2} e^x \cos(x) \, dx$** (Valor exacto: $1.648774$):
   * Con $n = 6$, $h = 0.2$:
     * **Simpson 1/3:** $1.648715$ (Error Abs: $0.000059$, Error Rel: $0.0036\%$)
     * **Simpson 3/8:** $1.648640$ (Error Abs: $0.000134$, Error Rel: $0.0081\%$)

2. **Integral $I = \int_1^5 \ln(x) \, dx$** (Valor exacto: $4.047190$):
   * Con $n = 10$, $h = 0.4$:
     * **Simpson 1/3:** $4.046953$ (Error Abs: $0.0000236$, Error Rel: $0.0058\%$)

---

## 5. REQUERIMIENTOS DE IMPLEMENTACIÓN PARA CLAUDE CODE

### A. Módulo Backend (`simpson_solver.py`)
Implementar las siguientes funciones en Python:
1. `simpson_13_compuesto(f_or_y, a=None, b=None, n=None, x=None)`:
   - Funciona con función $f(x)$ y límites $[a,b]$ o arreglos discretos de puntos $(x, y)$.
   - Si $n$ es impar para Simpson 1/3, notificar/lanzar advertencia o conmutar al método combinado.
2. `simpson_38_compuesto(f_or_y, a=None, b=None, n=None, x=None)`:
   - Implementa la regla 3/8 para $n$ múltiplo de 3 o arreglos tabulares.
3. `simpson_combinado(y, x)`:
   - Algoritmo generalizado que aplica Simpson 1/3 + 3/8 para cualquier número de puntos.
4. `evaluador_simbolico(expr_str, variables_dict, x_var)`:
   - Soporte para expresiones dinámicas con parámetros y variables personalizadas usando `sympy`.
5. `analisis_convergencia_simpson(expr_str, a, b, n_list)`:
   - Genera DataFrame con columnas: `n`, `h`, `I_Simpson13`, `I_Simpson38`, `Error_Abs_13`, `Error_Rel_%_13`.

### B. Interfaz de Usuario Streamlit (`app.py`)
1. **Menú Lateral de Navegación**:
   - Radio button / Selectbox para elegir entre:
     - 📌 **Sesión 12: Regla del Trapecio (Tráfico de Red)**
     - 📌 **Sesión 13: Reglas de Simpson (Terreno e Integración Curva)**
2. **Pestañas / Modos en Sesión 13**:
   - **Modo 1: Datos Tabulares (Caso Terreno / Entrada Personalizada)**:
     - Carga precargada con la tabla del perfil de terreno ($x \in [0, 30]$, $y \in [2.1, 2.2]$).
     - Componente `st.data_editor` para permitir al usuario ingresar o modificar filas/columnas de puntos $(x_i, y_i)$ fácilmente.
     - Comparativa de resultados (Trapecio vs. Simpson 1/3 vs. Simpson 3/8).
     - Gráfico interactivo con `matplotlib` mostrando el perfil de elevación y las zonas cuadradas bajo la curva.
   - **Modo 2: Función Continua y Personalizada**:
     - Input de texto para función $f(x)$ (soporta variables personalizadas $x, t, u$ y parámetros adicionales).
     - Selección de método (Simpson 1/3, Simpson 3/8, Combinado).
     - Tabla de convergencia dinámica para $n \in [2, 4, 6, 10, 20, 50, 100]$.
     - Visualización gráfica del polinomio interpolante parabólico en cada subintervalo.

### C. Trabajo Manual vs. Automatizado
* **Parte Manual (Enunciado / Hoja)**: La deducción analítica de la parábola de Lagrange de grado 2 y la sustitución algebraica paso a paso para $n=2$ se registran manualmente en la hoja del informe.
* **Parte Software (Streamlit)**: Todos los cálculos, construcción de mallas, tablas de convergencia, errores numéricos y gráficos son ejecutados automáticamente por el código.

---

## 6. INSTRUCCIONES DE CONTROL DE VERSIONES Y DOCUMENTACIÓN

Claude Code debe ejecutar las siguientes tareas finales:
1. **Actualizar `README.md`**:
   - Estructura limpia y profesional del repositorio $D:\text{MN-U3}$.
   - Explicación teórica resumida de la Sesión 12 (Trapecio) y Sesión 13 (Simpson 1/3 y 3/8).
   - Guía de ejecución con `streamlit run app.py`.
   - Tablas comparativas con los resultados exactos del terreno y funciones de prueba.
2. **Git Commit & Push (CRÍTICO - SIN COAUTORÍA)**:
   - Ejecutar en la terminal de `D:\MN-U3`:
     ```bash
     git add .
     git commit -m "feat: implement Session 13 Simpson integration solvers and interactive UI"
     git push origin main
     ```
   - **RESTRICCIÓN OBLIGATORIA**: No incluir ningún tag o metadato de coautoría (NO agregar líneas `Co-authored-by: ...` ni firmas de IA en el mensaje del commit).

---
*Documento de especificación generado para ejecución directa en Claude Code.*
