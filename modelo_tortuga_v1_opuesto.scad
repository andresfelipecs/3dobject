/*
  Tortuga v1 vieja con el equilibrio movido al lado opuesto del cuerpo.

  Interpretacion usada:
  - El apoyo original de v1 estaba en la cabeza.
  - "Lado opuesto" = apoyar sobre el domo principal del caparazon.

  Calibracion matematica:
  - Se mantiene la geometria vieja de cuello, cabeza, aletas, patas y cola.
  - Se elimina la base de apoyo de la cabeza.
  - Se ajusta la masa frontal con:
      front_lobe_scale = 0.913
    para que la proyeccion horizontal del CM caiga sobre el apice del
    caparazon principal:
      x_support = -2.40 u = -26.4 mm

  Efecto:
  - El apoyo real pasa a ser un unico punto nominal en el domo.
  - Este punto es mas favorable para equilibrar en dedo que el domo pequeno.
*/

$fn = 56;

scale_mm = 11;
front_lobe_scale = 0.913;

shell_center = [-2.40, 0, 1.05];
shell_axes = [1.95, 1.90, 0.95];
shell_apex_z = shell_center[2] + shell_axes[2];

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

module shell_hollow() {
    difference() {
        ellipsoid(c = shell_center, a = shell_axes);
        ellipsoid(c = [-2.42, 0, 1.08], a = [1.48, 1.45, 0.62]);
    }
}

module turtle_v1_opposite_balance() {
    union() {
        shell_hollow();

        capsule(p0 = [-1.55, 0, 0.72], p1 = [-0.55, 0, 0.40], r = 0.25);
        ellipsoid(c = [-0.26, 0, 0.34], a = [0.58, 0.40, 0.28]);
        capsule(p0 = [-0.08, 0, 0.18], p1 = [0.02, 0, 0.21], r = 0.10);

        capsule(p0 = [-1.55,  0.95, 0.36], p1 = [ 1.55,  2.10, 0.24], r = 0.16);
        capsule(p0 = [-1.55, -0.95, 0.36], p1 = [ 1.55, -2.10, 0.24], r = 0.16);
        ellipsoid(c = [2.05,  2.25, 0.24], a = [1.35, 0.72, 0.16]);
        ellipsoid(c = [2.05, -2.25, 0.24], a = [1.35, 0.72, 0.16]);

        ellipsoid(c = [2.35,  2.20, 0.30], a = [1.18 * front_lobe_scale, 0.78 * front_lobe_scale, 0.08 * front_lobe_scale]);
        ellipsoid(c = [2.35, -2.20, 0.30], a = [1.18 * front_lobe_scale, 0.78 * front_lobe_scale, 0.08 * front_lobe_scale]);

        capsule(p0 = [-3.00,  1.0, 0.30], p1 = [-4.45,  1.82, 0.18], r = 0.12);
        capsule(p0 = [-3.00, -1.0, 0.30], p1 = [-4.45, -1.82, 0.18], r = 0.12);
        capsule(p0 = [-4.05, 0.0, 0.22], p1 = [-5.25, 0.0, 0.14], r = 0.08);
    }
}

// Orientacion de impresion: el apice principal del caparazon baja a z=0.
render(convexity = 12)
mirror([0, 0, 1])
translate([0, 0, -shell_apex_z])
scale([scale_mm, scale_mm, scale_mm])
turtle_v1_opposite_balance();
