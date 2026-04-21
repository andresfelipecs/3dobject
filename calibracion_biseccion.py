"""
calibracion_biseccion.py
========================
Calibración del parámetro front_lobe_scale mediante búsqueda binaria (bisección).

Problema: encontrar el valor de `s` tal que el centro de masa (x̄) caiga
exactamente sobre la proyección del ápex del caparazón.

    f(s) = x̄(s) − x_caparazón = 0

donde  x_caparazón = −26.4 mm  (en la escala 11 mm/u del modelo SCAD).

Propiedad usada: f(s) es monótona — aumentar s añade masa frontal (x > 0),
desplazando x̄ hacia adelante (f aumenta).

Algoritmo (Teorema del Valor Intermedio):
    1. Encontrar a, b tal que  f(a) < 0  y  f(b) > 0
    2. Evaluar m = (a+b)/2
    3. Si f(m) < 0: a ← m,  si f(m) > 0: b ← m
    4. Repetir hasta |f(m)| < tolerancia

Complejidad: O(log₂((b−a)/tol)) iteraciones, cada una con N_MC muestras.

Uso:
    python3 calibracion_biseccion.py [--tol 0.05] [--samples 500000]
"""

import numpy as np
import argparse, time
from calculo_cm_montecarlo import monte_carlo_cm, X_CAPARAZON, SCALE_MM

def f_bisect(scale, n_samples=500_000, seed=42):
    """
    Función a anular: f(scale) = x̄(scale) − x_caparazón
    Positivo → CM demasiado adelante; negativo → CM demasiado atrás.
    """
    r = monte_carlo_cm(n_samples=n_samples, front_scale=scale, seed=seed)
    return r['delta_x_mm']   # x_cm_mm − X_CAPARAZON

def biseccion(a=0.3, b=1.5, tol=0.05, n_samples=500_000, max_iter=20):
    """
    Búsqueda binaria sobre front_lobe_scale.

    Precondición: f(a) < 0 y f(b) > 0  (se verifica automáticamente).

    Retorna: (scale_opt, delta_x_opt, historial)
    """
    print("── Bisección: buscando front_lobe_scale ─────────────────────")
    print(f"   Objetivo: x̄ = {X_CAPARAZON:.2f} mm  (ápex del caparazón)")
    print(f"   Tolerancia: |Δx| < {tol} mm  |  Muestras/iter: {n_samples:,}\n")
    print(f"{'Iter':>4}  {'scale':>7}  {'Δx (mm)':>10}  {'intervalo':>18}")
    print("─" * 46)

    fa = f_bisect(a, n_samples)
    fb = f_bisect(b, n_samples)

    # Verificar que el intervalo inicial sea válido
    if fa * fb > 0:
        # Intentar invertir
        if fa > 0:
            a, b = b, a
            fa, fb = fb, fa
        else:
            raise ValueError(f"f({a})={fa:.3f} y f({b})={fb:.3f} tienen el mismo signo. "
                             "Amplíe el intervalo [a, b].")

    history = []
    for it in range(1, max_iter + 1):
        m  = (a + b) / 2.0
        fm = f_bisect(m, n_samples, seed=it)
        history.append({'iter': it, 'scale': m, 'delta_x': fm, 'a': a, 'b': b})

        print(f"{it:>4}  {m:>7.4f}  {fm:>+10.4f}  [{a:.4f}, {b:.4f}]")

        if abs(fm) < tol:
            print(f"\n   ✓  Convergido: scale = {m:.6f}  |  Δx = {fm:+.4f} mm")
            return m, fm, history

        if fm < 0:
            a = m   # CM demasiado atrás → aumentar scale (más masa frontal)
        else:
            b = m   # CM demasiado adelante → reducir scale

    print(f"\n   ⚠  Máximo de iteraciones alcanzado: scale ≈ {m:.4f}, Δx = {fm:+.4f} mm")
    return m, fm, history


def analisis_sensibilidad(scale_opt, n_samples=500_000, delta=0.05):
    """
    Calcula dx̄/ds numéricamente en el punto óptimo.
    Útil para estimar la tolerancia de fabricación.
    """
    f_plus  = f_bisect(scale_opt + delta, n_samples)
    f_minus = f_bisect(scale_opt - delta, n_samples)
    dfdx = (f_plus - f_minus) / (2 * delta)
    print(f"\n── Sensibilidad ──────────────────────────────────────────────")
    print(f"   dx̄/ds ≈ {dfdx:.3f} mm/u   (variación del CM por unidad de scale)")
    print(f"   Para Δx < 0.15 mm → escala tolerada: ±{0.15/abs(dfdx):.3f} u")
    return dfdx


# ── Ejecución directa ─────────────────────────────────────────────────────────
if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Bisección para calibrar front_lobe_scale (equilibrio en caparazón)')
    parser.add_argument('--tol',     type=float, default=0.05,
                        help='Tolerancia en mm del offset del CM (default 0.05)')
    parser.add_argument('--samples', type=int,   default=500_000,
                        help='Muestras Monte Carlo por iteración (default 500 000)')
    parser.add_argument('--a',       type=float, default=0.3,
                        help='Límite inferior inicial del intervalo')
    parser.add_argument('--b',       type=float, default=1.5,
                        help='Límite superior inicial del intervalo')
    parser.add_argument('--sensitivity', action='store_true',
                        help='Calcular sensibilidad dx̄/ds tras converger')
    args = parser.parse_args()

    t0 = time.time()
    scale_opt, delta_opt, history = biseccion(
        a=args.a, b=args.b, tol=args.tol, n_samples=args.samples)

    print(f"\n── Resumen final ─────────────────────────────────────────────")
    print(f"   front_lobe_scale = {scale_opt:.6f}")
    print(f"   Offset XY final  = {delta_opt:+.4f} mm  (tolerancia < 0.15 mm  {'✓' if abs(delta_opt)<0.15 else '✗'})")
    print(f"   Iteraciones      = {len(history)}")
    print(f"   Tiempo total     = {time.time()-t0:.1f} s")

    if args.sensitivity:
        analisis_sensibilidad(scale_opt, args.samples)

    # Confirmación con alta resolución
    print("\n── Verificación final (1 000 000 muestras) ───────────────────")
    r_final = monte_carlo_cm(n_samples=1_000_000, front_scale=scale_opt)
    z_apex  = 2.00 * SCALE_MM   # 22 mm en coords originales
    z_cm_nuevo = z_apex - r_final['z_cm_mm']
    R_eff   = (1.95 * SCALE_MM)**2 / (0.95 * SCALE_MM)
    print(f"   x̄ = {r_final['x_cm_mm']:+.4f} mm  (objetivo {X_CAPARAZON:.2f} mm)")
    print(f"   z̄ = {r_final['z_cm_mm']:+.4f} mm  (coords originales SCAD)")
    print(f"   z_CM (sobre ápex, nueva orientación) = {z_cm_nuevo:.2f} mm")
    print(f"   R_eff = {R_eff:.1f} mm")
    print(f"   Estabilidad: z_CM < R_eff  →  {z_cm_nuevo:.2f} < {R_eff:.1f}  "
          f"{'✓ ESTABLE' if z_cm_nuevo < R_eff else '✗ INESTABLE'}")
