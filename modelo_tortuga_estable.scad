/*
  Tortuga 3D equilibrada sobre la punta de la cabeza.

  Criterio fisico:
  - La punta real de apoyo es el punto (0, 0, 0).
  - El centro de masa se calibra para caer sobre esa vertical.
  - Base disco oblato: radio horizontal a=0.42, radio vertical b=0.05
    → curvatura efectiva R_eff = a^2/b = 3.53 unidades = 38.8 mm
    → z_CM ≈ 0.68 unidades << R_eff  → estable en mesa plana y dedo
*/

$fn = 96;

scale_mm = 11;
front_lobe_scale = 2.604525;  // recalibrado con disco oblato a=0.42 b=0.05
support_a = 0.42;             // semi-eje horizontal del disco de apoyo
support_b = 0.05;             // semi-eje vertical  (R_eff = a^2/b = 3.528)

module ellipsoid(c = [0, 0, 0], a = [1, 1, 1]) {
    translate(c) scale(a) sphere(r = 1);
}

module capsule(p0 = [0, 0, 0], p1 = [1, 0, 0], r = 0.2) {
    hull() {
        translate(p0) sphere(r = r);
        translate(p1) sphere(r = r);
    }
}

module support_head_tip() {
    // Disco oblato: toca z=0 en (0,0,0), curvatura efectiva = a^2/b
    translate([0, 0, support_b]) scale([support_a, support_a, support_b]) sphere(r = 1);
}

module shell_hollow() {
    difference() {
        union() {
            ellipsoid(c = [-2.40, 0, 1.05], a = [1.95, 1.90, 0.95]);
            ellipsoid(c = [-2.55, 0, 1.48], a = [1.45, 1.50, 0.74]);
        }
        ellipsoid(c = [-2.42, 0, 1.08], a = [1.48, 1.45, 0.62]);
    }
}

module turtle_head_tip_balance() {
    union() {
        shell_hollow();

        capsule(p0 = [-1.55, 0, 0.72], p1 = [-0.55, 0, 0.40], r = 0.25);
        ellipsoid(c = [-0.26, 0, 0.34], a = [0.58, 0.40, 0.28]);
        capsule(p0 = [-0.08, 0, 0.18], p1 = [0.02, 0, 0.21], r = 0.10);
        support_head_tip();

        capsule(p0 = [-1.55, 0.95, 0.36], p1 = [1.55, 2.10, 0.24], r = 0.16);
        capsule(p0 = [-1.55, -0.95, 0.36], p1 = [1.55, -2.10, 0.24], r = 0.16);
        ellipsoid(c = [2.05, 2.25, 0.24], a = [1.35, 0.72, 0.16]);
        ellipsoid(c = [2.05, -2.25, 0.24], a = [1.35, 0.72, 0.16]);

        ellipsoid(c = [2.35, 2.20, 0.30], a = [1.18 * front_lobe_scale, 0.78 * front_lobe_scale, 0.08 * front_lobe_scale]);
        ellipsoid(c = [2.35, -2.20, 0.30], a = [1.18 * front_lobe_scale, 0.78 * front_lobe_scale, 0.08 * front_lobe_scale]);

        capsule(p0 = [-3.00, 1.0, 0.30], p1 = [-4.45, 1.82, 0.18], r = 0.12);
        capsule(p0 = [-3.00, -1.0, 0.30], p1 = [-4.45, -1.82, 0.18], r = 0.12);
        capsule(p0 = [-4.05, 0.0, 0.22], p1 = [-5.25, 0.0, 0.14], r = 0.08);
    }
}

scale([scale_mm, scale_mm, scale_mm]) turtle_head_tip_balance();
