"""
verificar_equilibrio_stl.py
==========================
Verifica equilibrio estatico directamente sobre una malla STL.

El script reporta:
- propiedades basicas de la malla,
- centro de masa estimado por la propia geometria,
- poses estables bajo gravedad,
- y si la proyeccion del centro de masa cae dentro de la zona de contacto.

Uso:
    python3 verificar_equilibrio_stl.py modelo_tortuga_estable_binario_impresion.stl
    python3 verificar_equilibrio_stl.py tortuga_IMPRIMIR.stl --poses 5
"""

from __future__ import annotations

import argparse
import math
from dataclasses import dataclass

import numpy as np
import trimesh


@dataclass
class PoseReport:
    index: int
    probability: float
    com_xy: np.ndarray
    com_z: float
    min_z: float
    tilt_deg: float
    contact_points: int
    hull_points: int
    inside_support: bool
    hull_bbox_min: np.ndarray
    hull_bbox_max: np.ndarray


def convex_hull_2d(points: np.ndarray) -> np.ndarray:
    """
    Convex hull 2D por monotonic chain.
    Devuelve vertices en sentido antihorario.
    """
    unique = sorted({(round(float(x), 6), round(float(y), 6)) for x, y in points})
    if len(unique) <= 1:
        return np.array(unique, dtype=float)

    def cross(o, a, b) -> float:
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])

    lower = []
    for point in unique:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], point) <= 0:
            lower.pop()
        lower.append(point)

    upper = []
    for point in reversed(unique):
        while len(upper) >= 2 and cross(upper[-2], upper[-1], point) <= 0:
            upper.pop()
        upper.append(point)

    hull = lower[:-1] + upper[:-1]
    return np.array(hull, dtype=float)


def point_in_convex_polygon(point: np.ndarray, polygon: np.ndarray, tol: float = 1e-6) -> bool:
    """Prueba de inclusion para poligonos convexos 2D."""
    if len(polygon) == 0:
        return False
    if len(polygon) == 1:
        return np.linalg.norm(point - polygon[0]) <= tol
    if len(polygon) == 2:
        a, b = polygon
        ab = b - a
        denom = max(float(ab @ ab), tol)
        t = np.clip(float((point - a) @ ab) / denom, 0.0, 1.0)
        proj = a + t * ab
        return np.linalg.norm(point - proj) <= tol

    signs = []
    for idx in range(len(polygon)):
        a = polygon[idx]
        b = polygon[(idx + 1) % len(polygon)]
        cross = (b[0] - a[0]) * (point[1] - a[1]) - (b[1] - a[1]) * (point[0] - a[0])
        if abs(cross) > tol:
            signs.append(math.copysign(1.0, cross))

    return not signs or all(s >= 0 for s in signs) or all(s <= 0 for s in signs)


def build_pose_report(
    mesh: trimesh.Trimesh,
    transform: np.ndarray,
    probability: float,
    index: int,
    contact_tol: float,
) -> PoseReport:
    verts = trimesh.transform_points(mesh.vertices, transform)
    com = trimesh.transform_points([mesh.center_mass], transform)[0]
    min_z = float(verts[:, 2].min())

    support = verts[verts[:, 2] <= min_z + contact_tol][:, :2]
    hull = convex_hull_2d(support)
    inside = point_in_convex_polygon(com[:2], hull, tol=1e-3)

    body_up = transform[:3, :3] @ np.array([0.0, 0.0, 1.0])
    tilt_deg = math.degrees(
        math.acos(np.clip(float(body_up @ np.array([0.0, 0.0, 1.0])), -1.0, 1.0))
    )

    if len(hull) == 0:
        hull_bbox_min = np.array([np.nan, np.nan])
        hull_bbox_max = np.array([np.nan, np.nan])
    else:
        hull_bbox_min = hull.min(axis=0)
        hull_bbox_max = hull.max(axis=0)

    return PoseReport(
        index=index,
        probability=float(probability),
        com_xy=com[:2],
        com_z=float(com[2]),
        min_z=min_z,
        tilt_deg=tilt_deg,
        contact_points=len(support),
        hull_points=len(hull),
        inside_support=inside,
        hull_bbox_min=hull_bbox_min,
        hull_bbox_max=hull_bbox_max,
    )


def analyze_mesh(path: str, poses_to_show: int, pose_samples: int, contact_tol: float) -> None:
    mesh = trimesh.load_mesh(path)

    print(f"Archivo: {path}")
    print(f"Vertices: {len(mesh.vertices):,}  |  Caras: {len(mesh.faces):,}")
    print(f"Watertight: {mesh.is_watertight}  |  Euler: {mesh.euler_number}")
    print(
        "Bounds [mm]: "
        f"min={np.array2string(mesh.bounds[0], precision=3, suppress_small=True)}  "
        f"max={np.array2string(mesh.bounds[1], precision=3, suppress_small=True)}"
    )
    print(f"Volumen [mm^3]: {mesh.volume:.3f}")
    print(
        "Centro de masa [mm]: "
        f"{np.array2string(mesh.center_mass, precision=4, suppress_small=True)}"
    )
    if not mesh.is_watertight:
        print("Aviso: la malla no es cerrada; trimesh estima masa/CM suponiendo orientacion consistente.")

    transforms, probabilities = mesh.compute_stable_poses(
        n_samples=pose_samples,
        sigma=0.0,
    )

    limit = min(poses_to_show, len(transforms))
    print(f"\nPoses estables detectadas: {len(transforms)}")
    for idx in range(limit):
        report = build_pose_report(
            mesh=mesh,
            transform=transforms[idx],
            probability=probabilities[idx],
            index=idx + 1,
            contact_tol=contact_tol,
        )
        print(f"\nPose {report.index}")
        print(f"  probabilidad : {report.probability:.4f}")
        print(f"  inclinacion  : {report.tilt_deg:.2f} deg")
        print(f"  z_CM         : {report.com_z:.4f} mm")
        print(f"  proy. CM XY  : ({report.com_xy[0]:.4f}, {report.com_xy[1]:.4f}) mm")
        print(f"  z_contacto   : {report.min_z:.4f} mm")
        print(
            f"  soporte      : {report.contact_points} pts minimos  |  "
            f"hull={report.hull_points} vertices"
        )
        print(
            "  bbox soporte : "
            f"x=[{report.hull_bbox_min[0]:.4f}, {report.hull_bbox_max[0]:.4f}] mm, "
            f"y=[{report.hull_bbox_min[1]:.4f}, {report.hull_bbox_max[1]:.4f}] mm"
        )
        print(
            "  equilibrio   : "
            f"{'SI' if report.inside_support else 'NO'}  "
            "(proyeccion del CM dentro de la zona de apoyo)"
        )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Verifica equilibrio estatico sobre STL.")
    parser.add_argument("stl", help="Ruta al archivo STL")
    parser.add_argument("--poses", type=int, default=5, help="Numero de poses a mostrar")
    parser.add_argument(
        "--pose-samples",
        type=int,
        default=30,
        help="Muestras usadas por trimesh para buscar poses estables",
    )
    parser.add_argument(
        "--contact-tol",
        type=float,
        default=0.05,
        help="Tolerancia vertical [mm] para construir la zona de contacto",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    analyze_mesh(
        path=args.stl,
        poses_to_show=args.poses,
        pose_samples=args.pose_samples,
        contact_tol=args.contact_tol,
    )
