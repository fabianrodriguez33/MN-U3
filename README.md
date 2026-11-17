# MN-U3 · Métodos Numéricos, Unidad 3

Aplicación Streamlit con tres sesiones:

- **Sesión 12:** Regla del Trapecio Compuesto (tráfico de red de un servidor web).
- **Sesión 13:** Reglas de Simpson 1/3, 3/8 y combinada (perfil de terreno y funciones continuas).
- **Sesión 14:** Ecuaciones diferenciales ordinarias, problemas de valor inicial (Euler, Heun, RK3, RK4).

## Estructura

```
D:\MN-U3
├── app.py                      # UI Streamlit (navegación Sesión 12 / 13 / 14)
├── trapezoidal_solver.py       # Sesión 12: trapecio simple/compuesto, convergencia
├── simpson_solver.py           # Sesión 13: Simpson 1/3, 3/8, combinado, datos tabulares
├── ode_solver.py               # Sesión 14: Euler, Heun, RK3, RK4, PVI y convergencia
├── teclado.py                  # Teclado en pantalla, parámetros automáticos, límites tipo "pi/2"
├── parser_util.py              # Parser tolerante (2x, ^, ln, sen, pi, e; una o dos variables)
├── README.md
├── requirements.txt            # streamlit, numpy, pandas, matplotlib, sympy, scipy
└── .gitignore
```

## Instalación y ejecución

```bash
pip install -r requirements.txt
streamlit run app.py
```

Las funciones se escriben con el teclado en pantalla o a mano: acepta `^`, `2x`, `ln`, `sen`, `pi`, `e`. Los
parámetros (`A`, `k`, `a`, `b`…) se detectan solos y se piden como campos numéricos.

## Sesión 12 · Trapecio compuesto (`h = (b−a)/n`)

    I ≈ (h/2) [f0 + 2 Σ f_i + f_n]        |E| ≤ (b−a) h² / 12 · max|f''|

## Sesión 13 · Simpson

    1/3 (n par):         I ≈ (h/3) [f0 + 4 Σ_impar f_i + 2 Σ_par f_j + f_n]     |E| ≤ n h⁵/180 · max|f⁗|
    3/8 (n múltiplo 3):  I ≈ (3h/8) [f0 + 3 Σ_{i≠3k} f_i + 2 Σ f_{3k} + f_n]
    Combinado (n ≥ 2):   1/3 en los primeros subintervalos pares y 3/8 en los últimos 3 si n es impar

**Modo 3 · Datos con paso variable:** parte los datos en tramos de paso uniforme y elige la regla de cada uno
(`n = 1` trapecio, `n` par Simpson 1/3, `n` múltiplo de 3 Simpson 3/8, otro impar combinado). Ejemplo: potencia de un
rack con lecturas cada 5 min en [0, 30] y cada 10 min en [30, 60] → Simpson 1/3 (4403.33) + Simpson 3/8 (4777.50)
= 9180.83 kW·min = **153.01 kWh**, potencia promedio 153.01 kW.

Terreno (`h = 5 m`, `n = 6`): Trapecio 78.7500 m², Simpson 1/3 78.8333 m², Simpson 3/8 78.9375 m².

| Integral | Exacto | n | Método | Aproximación | Error abs. | Error rel. |
|---|---|---|---|---|---|---|
| ∫₀^1.2 eˣ cos x dx | 1.648774 | 6 | Simpson 1/3 | 1.648715 | 0.000059 | 0.0036 % |
| ∫₀^1.2 eˣ cos x dx | 1.648774 | 6 | Simpson 3/8 | 1.648640 | 0.000134 | 0.0081 % |
| ∫₁⁵ ln x dx | 4.047190 | 10 | Simpson 1/3 | 4.046953 | 0.000237 | 0.0058 % |

## Sesión 14 · PVI `dy/dx = f(x, y)`, `y(x₀) = y₀`

Métodos de un paso (`y_{i+1}` a partir de `y_i`, ancho `h`):

| Método | Orden | Fórmula |
|---|---|---|
| Euler | 1 | `y + h·f(x, y)` |
| Heun (Euler mejorado) | 2 | `y + h/2 · [f(x, y) + f(x+h, y + h·f(x, y))]` |
| RK3 | 3 | `k1=f(x,y)`, `k2=f(x+h/2, y+h/2·k1)`, `k3=f(x+h, y−h·k1+2h·k2)`, `y + h/6 (k1+4k2+k3)` |
| RK4 | 4 | `k1..k4` clásicos, `y + h/6 (k1+2k2+2k3+k4)` |

Valores exactos: se intenta resolver con `sympy.dsolve`; si no hay solución explícita se usa una referencia
numérica de alta precisión (DOP853, tolerancia 1e-12) y la app lo indica.

Caso guía: `(y² − x²)dx + xy dy = 0`, `y(1) = 2`, solución `y = √((x⁴+7)/(2x²))`, `h = 0.1`:

| x | Exacto | Euler | Error rel. Euler | Heun | Error rel. Heun | RK3 | RK4 |
|---|---|---|---|---|---|---|---|
| 1.0 | 2.000000 | 2.000000 | 0 % | 2.000000 | 0 % | 2.000000 | 2.000000 |
| 1.1 | 1.870177 | 1.850000 | 1.0789 % | 1.870639 | 0.0247 % | 1.870156 | 1.870178 |
| 1.2 | 1.774980 | 1.741278 | 1.8988 % | 1.775807 | 0.0465 % | 1.774944 | 1.774982 |

La pestaña de convergencia muestra el error relativo en `x = 1.2` para `h ∈ {0.1, 0.05, 0.01, 0.005, 0.001}` y su
gráfico log-log (pendientes ≈ 1, 2, 3, 4).

## Despliegue en Streamlit Community Cloud

1. Subir el repositorio a GitHub (rama `main`).
2. En <https://share.streamlit.io> elegir **New app**, repositorio, rama `main`, archivo `app.py`.
3. Streamlit instala `requirements.txt` automáticamente.
