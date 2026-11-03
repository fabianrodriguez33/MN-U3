# MN-U3 · Integración Numérica (Trapecio y Simpson)

Aplicación Streamlit de la Unidad 3 de Métodos Numéricos.

- **Sesión 12:** Regla del Trapecio Compuesto (caso: tráfico de red de un servidor web).
- **Sesión 13:** Reglas de Simpson 1/3, 3/8 y combinada (caso: perfil de terreno y funciones continuas).

## Estructura

```
D:\MN-U3
├── app.py                      # UI Streamlit (navegación Sesión 12 / Sesión 13)
├── trapezoidal_solver.py       # Sesión 12: trapecio simple/compuesto, evaluador simbólico, convergencia
├── simpson_solver.py           # Sesión 13: Simpson 1/3, 3/8, combinado, datos tabulares, convergencia
├── instrucciones_sesion12.md   # Especificación Sesión 12
├── instrucciones_sesion13.md   # Especificación Sesión 13
├── README.md
├── requirements.txt            # streamlit, numpy, pandas, matplotlib, sympy, scipy
├── .gitignore
└── .claude/launch.json         # Servidor de desarrollo (puerto 8501)
```

## Teoría resumida

**Trapecio compuesto** (`h = (b−a)/n`):

    I ≈ (h/2) [f0 + 2 Σ f_i + f_n]        |E| ≤ (b−a) h² / 12 · max|f''|

**Simpson 1/3 compuesto** (`n` par):

    I ≈ (h/3) [f0 + 4 Σ_{i impar} f_i + 2 Σ_{j par} f_j + f_n]      |E| ≤ n h⁵ / 180 · max|f⁗|

**Simpson 3/8 compuesto** (`n` múltiplo de 3):

    I ≈ (3h/8) [f0 + 3 Σ_{i≠3k} f_i + 2 Σ f_{3k} + f_n]             E = −(b−a)⁵/6480 · f⁗(ξ)  (simple)

**Combinado** (cualquier `n ≥ 2`): 1/3 en los primeros subintervalos (pares) y 3/8 en los últimos 3 si `n` es impar.

## Resultados de referencia (verificados con el software)

Terreno (`h = 5 m`, `n = 6`, datos tabulares):

| Método | Área (m²) |
|---|---|
| Trapecio compuesto | 78.7500 |
| Simpson 1/3 compuesto | 78.8333 |
| Simpson 3/8 compuesto | 78.9375 |

Funciones continuas:

| Integral | Exacto | n | Método | Aproximación | Error abs. | Error rel. |
|---|---|---|---|---|---|---|
| ∫₀^1.2 eˣ cos x dx | 1.648774 | 6 | Simpson 1/3 | 1.648715 | 0.000059 | 0.0036 % |
| ∫₀^1.2 eˣ cos x dx | 1.648774 | 6 | Simpson 3/8 | 1.648640 | 0.000134 | 0.0081 % |
| ∫₁⁵ ln x dx | 4.047190 | 10 | Simpson 1/3 | 4.046953 | 0.000237 | 0.0058 % |

## Ejecución local

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Despliegue en Streamlit Community Cloud

1. Subir el repositorio a GitHub (rama `main`).
2. En <https://share.streamlit.io> elegir **New app**, repositorio, rama `main`, archivo `app.py`.
3. Streamlit instala `requirements.txt` automáticamente.
