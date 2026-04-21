/*
  Tortuga 3D para impresión.

  Ajustes aplicados a la versión imprimible:
  - Caparazón macizo para eliminar la cavidad central y sus paredes internas débiles.
  - Cuello, cabeza, aletas, patas y cola más gruesos para evitar tubos frágiles.
  - Solapes más profundos con el caparazón para evitar uniones tangenciales que rompen la malla.

  Se mantiene la orientación de exportación con el caparazón hacia la cama.
*/

$fn = 48;

scale_mm = 11;

module ellipsoid(c = [0, 0, 0], a = [1, 1, 1]) {
    translate(c) scale(a) sphere(r = 1);
}

module capsule(p0 = [0, 0, 0], p1 = [1, 0, 0], r = 0.2) {
    dx = p1[0] - p0[0];
    dy = p1[1] - p0[1];
    dz = p1[2] - p0[2];
    len = sqrt(dx * dx + dy * dy + dz * dz);
    axis = [-dy, dx, 0];
    axis_norm = sqrt(axis[0] * axis[0] + axis[1] * axis[1] + axis[2] * axis[2]);
    angle = len < 0.0001 ? 0 : acos(dz / len);

    translate(p0) rotate(a = angle, v = axis_norm < 0.0001 ? [1, 0, 0] : axis) union() {
        sphere(r = r);
        cylinder(h = len, r = r, center = false);
        translate([0, 0, len]) sphere(r = r);
    }
}

module shell_printable() {
    union() {
        ellipsoid(c = [-2.40, 0, 1.05], a = [1.95, 1.90, 0.95]);
        ellipsoid(c = [-2.52, 0, 1.46], a = [1.42, 1.46, 0.70]);
    }
}

module turtle_printable() {
    union() {
        shell_printable();

        // ── Cuello ──
        capsule(p0 = [-1.95, 0, 0.78], p1 = [-0.58, 0, 0.54], r = 0.28);

        // ── Cabeza ──
        ellipsoid(c = [-0.05, 0, 0.48], a = [0.74, 0.48, 0.40]);

        // ── Hocico ──
        capsule(p0 = [0.22, 0, 0.30], p1 = [0.42, 0, 0.33], r = 0.12);

        // Los p0 arrancan dentro del caparazón para asegurar una unión robusta.
        capsule(p0 = [-2.18,  0.72, 1.00], p1 = [ 0.95,  2.35, 0.76], r = 0.24);
        capsule(p0 = [-2.18, -0.72, 1.00], p1 = [ 0.95, -2.35, 0.76], r = 0.24);

        capsule(p0 = [-3.28,  0.82, 0.94], p1 = [-4.88,  1.78, 0.60], r = 0.20);
        capsule(p0 = [-3.28, -0.82, 0.94], p1 = [-4.88, -1.78, 0.60], r = 0.20);

        // ── Cola ──
        capsule(p0 = [-4.18, 0, 0.72], p1 = [-5.30, 0, 0.58], r = 0.12);
    }
}

// Orientación para imprimir: domo del caparazón abajo (z=0)
render(convexity = 12)
mirror([0, 0, 1])
translate([0, 0, -(1.46 + 0.70)])   // sube toda la geometría para que nada quede bajo z=0
scale([scale_mm, scale_mm, scale_mm])
turtle_printable();
