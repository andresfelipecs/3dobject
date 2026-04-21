"""
calculo_cm_montecarlo.py
========================
Cálculo del Centro de Masa de la tortuga 3D mediante integración de Monte Carlo.

Objetivo: determinar (x̄, ȳ, z̄) tal que el CM caiga sobre el ápex del caparazón,
garantizando equilibrio estable con R_eff = a²/c = 44.0 mm > z_CM.

Integrales evaluadas (densidad uniforme ρ=1):

    V   = ∭ χ_T(x,y,z) dV                    ← volumen de la pieza
    Mx  = ∭ x · χ_T(x,y,z) dV               ← momento en x
    My  = ∭ y · χ_T(x,y,z) dV               ← momento en y  (≈0 por simetría)
    Mz  = ∭ z · χ_T(x,y,z) dV               ← momento en z
    x̄   = Mx / V,   ȳ = My / V,   z̄ = Mz / V

χ_T(x,y,z) = 1 si el punto está dentro de la tortuga, 0 en caso contrario.

Uso:
    python3 calculo_cm_montecarlo.py [--samples N] [--scale F]
"""

import numpy as np
import argparse, time

# ── Parámetros geométricos (unidades SCAD; 1 u = 11 mm) ──────────────────────
SCALE_MM      = 11.0          # mm por unidad SCAD
FRONT_SCALE   = 0.913         # front_lobe_scale calibrado para CM sobre caparazón

# Caparazón exterior: elipsoide  center=(-2.40, 0, 1.05), semi-ejes=(1.95,1.90,0.95)
SHELL_CENTER  = np.array([-2.40, 0.0, 1.05])
SHELL_A       = np.array([ 1.95, 1.90, 0.95])   # semi-ejes exterior
SHELL_HOLLOW  = np.array([ 1.48, 1.45, 0.62])   # semi-ejes del vaciado interior
SHELL_HOLE_C  = np.array([-2.42, 0.0, 1.08])    # centro del vaciado

# Punto de apoyo (ápex del caparazón en la orientación original, boca-arriba)
SHELL_APEX    = SHELL_CENTER + np.array([0, 0, SHELL_A[2]])   # z_apex = 2.00 u
X_CAPARAZON   = SHELL_APEX[0] * SCALE_MM   # proyección x del contacto = -26.4 mm

# ── Funciones de forma ────────────────────────────────────────────────────────

def in_ellipsoid(pts, center, axes):
    """χ para un elipsoide: ((x-cx)/ax)² + ((y-cy)/ay)² + ((z-cz)/az)² ≤ 1"""
    d = (pts - center) / axes
    return (d**2).sum(axis=1) <= 1.0

def in_capsule(pts, p0, p1, r):
    """χ para una cápsula (hull de dos esferas)."""
    axis = p1 - p0
    L2   = axis @ axis
    t    = np.clip(((pts - p0) @ axis) / L2, 0.0, 1.0)
    proj = p0 + t[:, None] * axis
    return ((pts - proj)**2).sum(axis=1) <= r * r

def in_turtle(pts, front_scale=FRONT_SCALE):
    """
    Función característica χ_T de la tortuga.
    Devuelve array booleano (True = dentro).
    """
    mask = np.zeros(len(pts), dtype=bool)

    # Caparazón (exterior − interior hueco)
    shell_out   = in_ellipsoid(pts, SHELL_CENTER, SHELL_A)
    shell_inner = in_ellipsoid(pts, SHELL_HOLE_C, SHELL_HOLLOW)
    mask |= (shell_out & ~shell_inner)

    # Cuello
    mask |= in_capsule(pts, np.array([-1.55, 0, 0.72]),
                            np.array([-0.55, 0, 0.40]), 0.25)
    # Cabeza
    mask |= in_ellipsoid(pts, np.array([-0.26, 0, 0.34]),
                              np.array([ 0.58, 0.40, 0.28]))
    # Hocico
    mask |= in_capsule(pts, np.array([-0.08, 0, 0.18]),
                            np.array([ 0.02, 0, 0.21]), 0.10)

    # Brazos anteriores (sin cambio)
    mask |= in_capsule(pts, np.array([-1.55,  0.95, 0.36]),
                            np.array([ 1.55,  2.10, 0.24]), 0.16)
    mask |= in_capsule(pts, np.array([-1.55, -0.95, 0.36]),
                            np.array([ 1.55, -2.10, 0.24]), 0.16)
    # Aletas anteriores
    mask |= in_ellipsoid(pts, np.array([2.05,  2.25, 0.24]),
                              np.array([1.35,  0.72, 0.16]))
    mask |= in_ellipsoid(pts, np.array([2.05, -2.25, 0.24]),
                              np.array([1.35,  0.72, 0.16]))

    # Lóbulos frontales — calibrados por bisección
    fs = front_scale
    mask |= in_ellipsoid(pts, np.array([2.35,  2.20, 0.30]),
                              np.array([1.18*fs, 0.78*fs, 0.08*fs]))
    mask |= in_ellipsoid(pts, np.array([2.35, -2.20, 0.30]),
                              np.array([1.18*fs, 0.78*fs, 0.08*fs]))

    # Patas traseras
    mask |= in_capsule(pts, np.array([-3.00,  1.0, 0.30]),
                            np.array([-4.45,  1.82, 0.18]), 0.12)
    mask |= in_capsule(pts, np.array([-3.00, -1.0, 0.30]),
                            np.array([-4.45, -1.82, 0.18]), 0.12)
    # Cola
    mask |= in_capsule(pts, np.array([-4.05, 0.0, 0.22]),
                            np.array([-5.25, 0.0, 0.14]), 0.08)

    return mask


def monte_carlo_cm(n_samples=3_000_000, front_scale=FRONT_SCALE, seed=42):
    """
    Estima el centro de masa por Monte Carlo.

    Integrales:
        V  = ∭ χ_T dV  ≈  V_box · (M_in / N)
        Mx = ∭ x·χ_T dV ≈  V_box · (Σ x_i·χ_i / N)
        etc.
    """
    rng = np.random.default_rng(seed)

    # Bounding box (unidades SCAD)
    lo = np.array([-5.35, -3.10, 0.05])
    hi = np.array([ 3.55,  3.10, 2.10])
    V_box = np.prod(hi - lo)

    t0 = time.time()

    # Muestreo por lotes para eficiencia de memoria
    batch = min(n_samples, 500_000)
    n_done = 0
    sum_in = 0
    sum_x = sum_y = sum_z = 0.0

    while n_done < n_samples:
        n_batch = min(batch, n_samples - n_done)
        pts = rng.uniform(lo, hi, size=(n_batch, 3))
        inside = in_turtle(pts, front_scale)
        w = inside.astype(np.float64)
        sum_in += w.sum()
        sum_x  += (pts[:,0] * w).sum()
        sum_y  += (pts[:,1] * w).sum()
        sum_z  += (pts[:,2] * w).sum()
        n_done += n_batch

    elapsed = time.time() - t0

    V  = V_box * sum_in / n_samples        # ← ∭ χ_T dV  (unidades SCAD³)
    xb = (V_box * sum_x / n_samples) / V  # ← Mx / V
    yb = (V_box * sum_y / n_samples) / V  # ← My / V
    zb = (V_box * sum_z / n_samples) / V  # ← Mz / V

    return {
        'x_cm_scad': xb, 'y_cm_scad': yb, 'z_cm_scad': zb,
        'x_cm_mm':   xb * SCALE_MM,
        'y_cm_mm':   yb * SCALE_MM,
        'z_cm_mm':   zb * SCALE_MM,
        'volume_scad': V,
        'n_samples': n_samples,
        'elapsed_s': elapsed,
        # Offset respecto al ápex del caparazón (objetivo: 0)
        'delta_x_mm': xb * SCALE_MM - X_CAPARAZON,
    }


def stability_analysis(z_cm_mm):
    """
    Verifica la condición de estabilidad con el caparazón como superficie de contacto.

    R_eff = a² / c  (curvatura principal del elipsoide en su polo)
    Estable iff  z_CM  <  R_eff

    Para dedo (convexo en convexo):
        R_comb = R_caparazon · R_dedo / (R_caparazon - R_dedo)
    """
    a_mm   = SHELL_A[0] * SCALE_MM   # 21.45 mm
    c_mm   = SHELL_A[2] * SCALE_MM   # 10.45 mm
    R_eff  = a_mm**2 / c_mm          # 44.0 mm

    print("\n── Física del equilibrio ─────────────────────────────")
    print(f"  Contacto      : ápex del caparazón (orientación boca-abajo)")
    print(f"  a (horizontal): {a_mm:.2f} mm   c (vertical): {c_mm:.2f} mm")
    print(f"  R_eff = a²/c  : {R_eff:.1f} mm   ← curvatura en el polo")
    print(f"  z_CM          : {z_cm_mm:.2f} mm  (sobre el ápex)")
    print(f"  Condición     : z_CM < R_eff  →  {z_cm_mm:.2f} < {R_eff:.1f}  {'✓ ESTABLE' if z_cm_mm < R_eff else '✗ INESTABLE'}")
    print(f"  Margen        : {R_eff - z_cm_mm:.1f} mm")

    for R_dedo in [8, 10, 12, 15]:
        R_comb = (R_eff * R_dedo) / (R_eff - R_dedo)
        ok = z_cm_mm < R_comb
        print(f"  Dedo {R_dedo:2d} mm   : R_comb={R_comb:.1f} mm  {'✓' if ok else '✗'}  z_CM {'<' if ok else '>'} R_comb")


# ── Ejecución directa ─────────────────────────────────────────────────────────
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='CM Monte Carlo — tortuga equilibrada en caparazón')
    parser.add_argument('--samples', type=int, default=3_000_000)
    parser.add_argument('--scale',   type=float, default=FRONT_SCALE)
    args = parser.parse_args()

    print(f"Calculando CM: {args.samples:,} muestras  |  front_lobe_scale={args.scale}")
    print(f"Objetivo: x_CM = {X_CAPARAZON:.2f} mm  (ápex caparazón)")

    r = monte_carlo_cm(args.samples, args.scale)

    print(f"\n── Resultado ─────────────────────────────────────────")
    print(f"  x̄ = {r['x_cm_mm']:+.4f} mm   (objetivo: {X_CAPARAZON:.2f} mm)")
    print(f"  ȳ = {r['y_cm_mm']:+.4f} mm   (debería ≈ 0 por simetría)")
    print(f"  z̄ = {r['z_cm_mm']:+.4f} mm   (en coords originales SCAD)")
    print(f"  Δx = {r['delta_x_mm']:+.4f} mm  (offset respecto al ápex)")
    print(f"  V  = {r['volume_scad']:.4f} u³  →  {r['volume_scad']*SCALE_MM**3/1e3:.2f} cm³")
    print(f"  Tiempo: {r['elapsed_s']:.1f} s  |  muestras: {r['n_samples']:,}")

    # z_CM en la nueva orientación (boca-abajo): distancia desde el ápex hacia arriba
    z_apex_scad = SHELL_APEX[2]   # 2.00 u
    z_cm_new = (z_apex_scad - r['z_cm_scad']) * SCALE_MM
    print(f"\n  z_CM (nuevo, desde ápex): {z_cm_new:.2f} mm")
    stability_analysis(z_cm_new)
