# MN-U3 · Integración Numérica (Regla del Trapecio) — Sesión 12

Aplicación Streamlit para estimar integrales con la **Regla del Trapecio Compuesto**.
Caso guía: tráfico de red de un servidor web, `R(t) = (10 + 5 sin(πt)) / (4 + e^{0.15t})` Mbps,
con `D = ∫₀¹² R(t) dt`.

## Arquitectura

| Archivo | Rol |
|---|---|
| `app.py` | Interfaz Streamlit (Modo 1: caso guía; Modo 2: integrador personalizado; gráficos Matplotlib) |
| `trapezoidal_solver.py` | Lógica matemática: `trapecio_simple`, `trapecio_compuesto`, `evaluador_simbolico`, `analisis_convergencia`, cota de error |
| `instrucciones_sesion12.md` | Especificación de requerimientos |
| `requirements.txt` | Dependencias |
| `.claude/launch.json` | Servidor de desarrollo (puerto 8501) |

## Fundamento teórico (Newton-Cotes, n = 1)

Trapecio simple, `h = b − a`:

    I ≈ (h/2) [f(x0) + f(x1)]        |E| ≤ (h³/12) · max|f''|

Trapecio compuesto, `h = (b − a)/n`, `x_i = a + i·h`:

    I ≈ (h/2) { f(x0) + 2 Σ_{i=1}^{n-1} f(x_i) + f(x_n) }
    |E| ≤ (b − a) h² / 12 · max|f''|

El error decrece como O(h²).

## Ejecución local

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Despliegue en Streamlit Community Cloud (streamlit.io)

1. Subir el repositorio a GitHub (rama `main`).
2. En <https://share.streamlit.io> elegir **New app**, seleccionar el repositorio, rama `main` y archivo `app.py`.
3. Streamlit instalará `requirements.txt` automáticamente.
