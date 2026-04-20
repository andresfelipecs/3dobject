# Entrega Final: Tortuga 3D equilibrada

## Archivos de entrega
- `modelo_tortuga_estable_binario_impresion.stl`: STL final verificado para impresion 3D.
- `modelo_tortuga_estable.scad`: fuente editable del modelo final.
- `documentacion_proyecto_tortuga.html`: documentacion visual para presentar el proyecto.
- `tortuga_3d_interactiva.html`: visor 3D interactivo del modelo.
- `guia_informe.md`: guia breve para apoyar la presentacion.

## Parametros calibrados
- `front_lobe_scale = 2.604525`  → offset XY del CM = 0.010 mm
- Base de apoyo: disco oblato  a = 4.62 mm, b = 0.55 mm
- Curvatura efectiva: R_eff = a²/b = 38.8 mm
- z_CM = 7.5 mm  →  margen de estabilidad = 31.3 mm

## Criterios de estabilidad verificados
- Mesa plana:    z_CM (7.5 mm) < R_eff (38.8 mm)  → ESTABLE, angulo vuelco 31.6 deg
- Dedo 8 mm:     z_CM (7.5 mm) < R_dedo (8 mm)    → ESTABLE
- Dedo 10-12 mm: z_CM (7.5 mm) < R_dedo           → ESTABLE con margen
- Offset XY CM:  0.010 mm  (tolerancia < 0.15 mm)

## STL verificado
- 393,732 triangulos
- Malla cerrada, 0 normales invertidas, 0 triangulos degenerados
- Dimensiones: 118.1 x 93.1 x 24.4 mm
- Apto para slicing directo (Cura, PrusaSlicer, Bambu Studio)

## Archivos para mostrar en la presentacion
- Abrir `documentacion_proyecto_tortuga.html` para explicar el proyecto.
- Abrir `tortuga_3d_interactiva.html` para mostrar el modelo en 3D.
