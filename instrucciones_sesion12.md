# Especificación de Requerimientos: Sesión 12 - Guía Autónoma e Integración Numérica (Regla del Trapecio)

## 1. Contexto del Proyecto y Objetivo
Desarrollar un módulo interactivo en **Streamlit** (para la Unidad 3 de Métodos Numéricos en `D:\MN-U3`) que resuelva el problema de **Estimación del Tráfico de Red en un Servidor Web** mediante la **Regla del Trapecio Compuesto** [1, 2, 3]. 

El sistema debe permitir tanto la resolución del caso de estudio teórico como la personalización de funciones analíticas arbitrarias con múltiples variables e intervalos de entrada [3].

---

## 2. Estructura de Directorios del Proyecto (`D:\MN-U3`)
```text
D:\MN-U3
├── app.py                      # UI Streamlit principales (navegación y tableros interactivos)
├── trapezoidal_solver.py       # Módulo con la lógica matemática (Trapecio Simple, Compuesto, Análisis de Convergencia)
├── instrucciones_sesion12.md   # Especificación de Requerimientos y Prompt para Claude Code
├── README.md                   # Documentación profesional del proyecto actualizada
├── requirements.txt            # Dependencias del proyecto (streamlit, numpy, pandas, matplotlib, sympy, scipy)
└── .claude/
    └── launch.json             # Configuración del servidor de desarrollo (puerto 8501)
```

---

## 3. Fundamento Teórico del Método

### 3.1. Regla del Trapecio Simple ($n = 1$)
Conecta los puntos $(x_0, f(x_0))$ y $(x_1, f(x_1))$ mediante una recta (interpolación lineal) en el intervalo $[a, b]$ de ancho $h = b - a$ [8, 9, 10]:
$$I_{\text{trapecio}} = \frac{h}{2} \left[ f(x_0) + f(x_1) \right] \tag{1}$$

Cota superior del error absoluto en la regla simple [12]:
$$|E_{T_s}| \le \frac{h^3}{12} \cdot \max_{x \in [a,b]} |f''(x)| \tag{2}$$

### 3.2. Regla del Trapecio Compuesto ($n$ subintervalos)
Divide el intervalo $[a, b]$ en $n$ subintervalos iguales de ancho $h = \frac{b - a}{n}$ con puntos $x_i = a + i \cdot h$ para $i = 0, 1, \dots, n$ [2, 5, 10]:
$$I_{\text{compuesto}} = \frac{h}{2} \left\{ f(x_0) + 2 \sum_{i=1}^{n-1} f(x_i) + f(x_n) \right\} \tag{3}$$

Cota superior del error absoluto en la regla compuesta [12]:
$$|E_{T_R}| \le \frac{n h^3}{12} \cdot \max_{x \in [a,b]} |f''(x)| = \frac{(b - a) h^2}{12} \cdot \max_{x \in [a,b]} |f''(x)| \tag{4}$$

---

## 4. Caso de Estudio: Estimación del Tráfico de Red

### 4.1. Definición del Problema
Un microservicio crítico en un centro de procesamiento de datos registra una tasa de transferencia de datos $R(t)$ en Megabits por segundo (Mbps) dada por [1, 2]:
$$R(t) = \frac{10 + 5 \sin(\pi t)}{4 + e^{0.15 t}}$$
Se desea calcular la cantidad total de datos transferidos $D$ en Megabits durante el intervalo de tiempo $t \in [0, 12]$ segundos [2]:
$$D = \int_{0}^{12} R(t) \, dt$$

---

### 4.2. Procedimiento Teórico Manual ($n = 4$)
1. **Ancho de paso ($h$)** [2]:
   $$h = \frac{12 - 0}{4} = 3.0 \text{ s}$$

2. **Malla de Puntos $t_i$ y Evaluaciones $R(t_i)$** [2]:

| $i$ | $t_i$ (seg) | Sustitución en $R(t_i)$ | $R(t_i)$ (Mbps) |
|---|---|---|---|
| 0 | 0.0 | $\frac{10 + 5\sin(0)}{4 + e^0} = \frac{10}{5}$ | 2.000000 |
| 1 | 3.0 | $\frac{10 + 5\sin(3\pi)}{4 + e^{0.45}} = \frac{10}{4 + 1.568312}$ | 1.795876 |
| 2 | 6.0 | $\frac{10 + 5\sin(6\pi)}{4 + e^{0.90}} = \frac{10}{4 + 2.459603}$ | 1.548083 |
| 3 | 9.0 | $\frac{10 + 5\sin(9\pi)}{4 + e^{1.35}} = \frac{10}{4 + 3.857426}$ | 1.272681 |
| 4 | 12.0 | $\frac{10 + 5\sin(12\pi)}{4 + e^{1.80}} = \frac{10}{4 + 6.049647}$ | 0.995060 |

3. **Cálculo de la Integral por Trapecio Compuesto ($n=4$)** [2]:
   $$I_{\text{trapecio}} = \frac{3.0}{2} \left[ 2.000000 + 2(1.795876 + 1.548083 + 1.272681) + 0.995060 \right]$$
   $$I_{\text{trapecio}} = 1.5 \times \left[ 2.000000 + 9.233280 + 0.995060 \right] = 1.5 \times 12.228340 = 18.342511 \text{ Megabits}$$

4. **Comparación con el Valor Exacto**:
   - Valor Exacto (Cuadratura de alta precisión): $18.525079 \text{ Mb}$
   - Error Absoluto: $|18.525079 - 18.342511| = 0.182568 \text{ Mb}$
   - Error Relativo Porcentual: $\frac{0.182568}{18.525079} \times 100\% = 0.9855\%$

---

### 4.3. Tabla de Convergencia del Software ($n \in \{4, 10, 50, 100, 1000\}$) [3]

| Subintervalos ($n$) | Ancho de paso ($h$) | Integral Calculada $I_{\text{trapecio}}$ (Mb) | Error Absoluto Real | Error Relativo (%) |
|---|---|---|---|---|
| **4** | 3.0000 | 18.342511 | 0.182568 | 0.9855% |
| **10** | 1.2000 | 18.263145 | 0.261934 | 1.4139% |
| **50** | 0.2400 | 18.517286 | 0.007793 | 0.0421% |
| **100** | 0.1200 | 18.523144 | 0.001935 | 0.0104% |
| **1000** | 0.0120 | 18.525060 | 0.000019 | 0.0001% |

---

## 5. Requerimientos Funcionales del Software Streamlit (`app.py` y `trapezoidal_solver.py`)

1. **Módulo de Cálculo Modular (`trapezoidal_solver.py`)**:
   - `trapecio_compuesto(f, a, b, n)`: Retorna la malla de puntos $x_i$, evaluados $f(x_i)$, el valor de la integral aproximada y la tabla de iteraciones en un DataFrame [3].
   - `evaluador_simbolico(expr_str, var_name, ...)`: Parsea funciones arbitrarias ingresadas por el usuario con SymPy/NumPy para soportar mínimo 2 variables parametrizables o funciones personalizadas.
   - `analisis_convergencia(f, a, b, lista_n)`: Genera la tabla comparativa automatizada con error absoluto y relativo real [3].

2. **Interfaz de Usuario Streamlit (`app.py`)**:
   - **Modo 1: Caso Guía Autónoma (Sesión 12)**: Carga predeterminada del problema de tráfico de red $R(t) = \frac{10 + 5\sin(\pi t)}{4 + e^{0.15 t}}$ en $[0, 12]$ con $n=4$ y la tabla de convergencia automatizada [1, 2, 3].
   - **Modo 2: Integrador Personalizado (Multi-variable / Función Arbitraria)**: Permite al usuario ingresar funciones matemáticamente personalizadas (ej. $f(x, k) = A \cdot \sin(k \cdot x) / (1 + x^2)$), ajustar límites $a, b$, número de subintervalos $n$, y evaluar el método en tiempo real.
   - **Visualización Gráfica Interactiva**: Renderizado con Matplotlib de la función continua $f(x)$ y los trapecios formados bajo la curva para visualizar el área aproximada.

---

## 6. Instrucciones para Claude Code (Control de Git y Documentación)

1. **Actualización de `README.md`**:
   - Documentar la arquitectura modular del proyecto `D:\MN-U3`.
   - Explicar las fórmulas teóricas de Newton-Cotes / Trapecio Compuesto [7, 8, 10].
   - Incluir instrucciones claras de ejecución local (`streamlit run app.py`) y despliegue en Streamlit.io.

2. **Comandos Git (Sin Co-Autoría)**:
   - Ejecutar el commit y push **estrictamente sin firmas de co-autoría** (no incluir metadatos de `Co-authored-by:` en los mensajes de commit).
   - Comandos a ejecutar:
     ```bash
     git add .
     git commit -m "feat: implement Streamlit app for Session 12 numerical integration trapezoidal method"
     git push origin main
     ```
