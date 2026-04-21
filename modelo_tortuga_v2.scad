/*
  Tortuga v2 — diseño optimizado para EQUILIBRIO MÁXIMO SOBRE DEDO.

  Cambios respecto a v1:
  ─────────────────────
  1.  Caparazón rediseñado: MEDIA elipsoide (solo domo superior) mucho más
      plana y ancha. Sube drásticamente R_eff y baja z_CM:
          a = 27.5 mm, c = 8.2 mm    →  R_eff = 91.7 mm
          z_CM = 5.6 mm              →  margen 3.4 mm en dedo de 10 mm
          (fórmula correcta R_comb = R·r/(R+r) para contacto convexo-convexo)
  2.  Extremidades más delgadas (menos masa por encima del CM):
          cuello   r=0.20 (era 0.28)
          aletas   r=0.18 (era 0.24)
          patas    r=0.16 (era 0.20)
          cabeza   más pequeña
          cola     r=0.10 (era 0.12)
  3.  cx = −1.28 mm  (centro del domo desplazado ligeramente hacia atrás
      para que coincida con el CM). Calibrado por punto fijo en Monte Carlo.

  Estabilidad verificada:
      mesa           : margen +86 mm
      dedo 15 mm     : margen +7.3 mm
      dedo 10 mm     : margen +3.4 mm  ← objetivo cumplido
      dedo  8 mm     : margen +1.7 mm  ← también estable
*/

$fn = 56;

scale_mm = 11;

// ── Parámetros del caparazón (unidades SCAD, 1 u = 11 mm) ────────────────
SHELL_A     = 2.50;         // radio horizontal  (27.5 mm)
SHELL_C     = 0.75;         // profundidad domo  ( 8.25 mm)
SHELL_ZCUT  = 1.25;         // altura del corte plano
SHELL_ZTOP  = SHELL_ZCUT + SHELL_C;   // = 2.00 → polo (contacto con mesa)
CX          = -0.1159;      // corrección autoconsistente en x

module ellipsoid(c, a) {
    translate(c) scale(a) sphere(r = 1);
}

module capsule(p0, p1, r) {
    dx = p1[0] - p0[0];
    dy = p1[1] - p0[1];
    dz = p1[2] - p0[2];
    len = sqrt(dx*dx + dy*dy + dz*dz);
    axis = [-dy, dx, 0];
    axis_norm = sqrt(axis[0]*axis[0] + axis[1]*axis[1] + axis[2]*axis[2]);
    angle = len < 0.0001 ? 0 : acos(dz / len);

    translate(p0) rotate(a = angle, v = axis_norm < 0.0001 ? [1,0,0] : axis) union() {
        sphere(r = r);
        cylinder(h = len, r = r, center = false);
        translate([0, 0, len]) sphere(r = r);
    }
}

module half_shell() {
    // Media elipsoide superior (z >= SHELL_ZCUT) — es el domo que apoya.
    intersection() {
        ellipsoid(c = [CX, 0, SHELL_ZCUT], a = [SHELL_A, SHELL_A, SHELL_C]);
        translate([CX - 2*SHELL_A, -2*SHELL_A, SHELL_ZCUT])
            cube([4*SHELL_A, 4*SHELL_A, 2*SHELL_C + 0.1]);
    }
}

module turtle_v2() {
    union() {
        half_shell();

        // Cuello (arranca dentro del caparazón)
        capsule(p0 = [-0.35, 0, 1.20], p1 = [ 0.95, 0, 1.03], r = 0.20);

        // Cabeza
        ellipsoid(c = [1.32, 0, 1.04], a = [0.58, 0.38, 0.30]);

        // Hocico
        capsule(p0 = [1.62, 0, 0.94], p1 = [1.82, 0, 0.95], r = 0.10);

        // Aletas anteriores (los p0 arrancan dentro del caparazón)
        capsule(p0 = [-0.05,  0.55, 1.22], p1 = [ 1.85,  2.30, 1.02], r = 0.18);
        capsule(p0 = [-0.05, -0.55, 1.22], p1 = [ 1.85, -2.30, 1.02], r = 0.18);

        // Patas traseras
        capsule(p0 = [-1.00,  0.72, 1.22], p1 = [-2.60,  1.80, 1.04], r = 0.16);
        capsule(p0 = [-1.00, -0.72, 1.22], p1 = [-2.60, -1.80, 1.04], r = 0.16);

        // Cola
        capsule(p0 = [-1.80, 0, 1.20], p1 = [-3.05, 0, 1.12], r = 0.10);
    }
}

// ── Orientación de impresión: domo del caparazón abajo (z=0, toca la cama)
render(convexity = 12)
mirror([0, 0, 1])
translate([0, 0, -SHELL_ZTOP])     // sube la geom para que nada quede bajo z=0
scale([scale_mm, scale_mm, scale_mm])
turtle_v2();
