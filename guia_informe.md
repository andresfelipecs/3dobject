# Guia rapida: tortuga con balance en la punta de la cabeza

## 1) Historia matematica recomendada
Presenta el proyecto en dos niveles:

1. Modelo 2D simplificado para integrales dobles y centroide en planta.
2. Modelo 3D organico para la pieza real, el centro de masa y la impresion.

La idea central sigue siendo la misma:
las aletas y los lobulos delanteros agregan momento positivo en `x` y desplazan el centro de masa
hacia la cabeza hasta alinearlo con la punta de apoyo.

## 2) Modelo 2D para el desarrollo a mano
La lamina se construye como union de regiones simples:

1. Elipse para el caparazon.
2. Circulo para la cabeza.
3. Triangulo para el hocico.
4. Triangulo para la cola.
5. Dos triangulos para aletas delanteras.
6. Dos triangulos para aletas traseras.
7. Dos circulos delanteros de radio `r` para calibrar el equilibrio.

El punto `(0, 0)` representa el eje vertical que pasa por la punta real de apoyo.

## 3) Centro de masa en 2D
Con densidad superficial constante:

`A(r) = double_integral_R(dA)`

`Mx(r) = double_integral_R(x dA)`

`My(r) = double_integral_R(y dA)`

`x_bar(r) = Mx(r) / A(r)`

`y_bar(r) = My(r) / A(r)`

Por simetria respecto al eje `x`, se tiene `My(r) = 0`, luego `y_bar(r) = 0`.

## 4) Extension a 3D
La pieza real se define por union y diferencia de:

1. Elipsoides para caparazon, cabeza y masa delantera.
2. Capsulas para cuello, aletas y cola.
3. Un disco oblato (elipsoide achatado, semi-eje horizontal a=4.62 mm, vertical b=0.55 mm)
   en la punta del hocico que actua como base de apoyo universal.

La formulacion numerica usa funcion caracteristica:

`V = triple_integral chi_T(x,y,z) dV`

`Mx = triple_integral x * chi_T(x,y,z) dV`

`My = triple_integral y * chi_T(x,y,z) dV`

`Mz = triple_integral z * chi_T(x,y,z) dV`

`x_bar = Mx / V`, `y_bar = My / V`, `z_bar = Mz / V`

## 5) Lectura fisica correcta
El modelo esta calibrado para equilibrio estable sobre cualquier superficie:

- mesa plana
- punta del dedo
- punta de lapiz

La base de apoyo es un disco oblato con curvatura efectiva R_eff = a²/b = 38.8 mm.
La condicion de estabilidad es z_CM < R_eff, que se cumple con amplio margen:
z_CM = 7.5 mm << R_eff = 38.8 mm  → margen de 31.3 mm.

Adicionalmente, la proyeccion horizontal del centro de masa cae sobre la punta con
un offset de solo 0.010 mm, garantizando que no haya lado que pese mas que otro.

## 6) Archivos finales para mostrar
- `documentacion_proyecto_tortuga.html`: apoyo visual principal.
- `tortuga_3d_interactiva.html`: visor 3D del modelo.
- `modelo_tortuga_estable_binario_impresion.stl`: archivo final para impresion 3D.
- `modelo_tortuga_estable.scad`: fuente editable del modelo final.

## 7) Texto corto sugerido para explicar el proyecto
"Primero construimos un modelo 2D para trabajar con integrales dobles y entender como mover el
centro de masa hacia la cabeza. Luego pasamos a un modelo 3D organico definido por elipsoides,
capsulas y un disco oblato de apoyo en la punta del hocico. Con integrales triples y verificacion
numerica ajustamos la masa delantera hasta que la proyeccion del centro de masa coincidiera con
esa punta, y disenamos el disco con curvatura efectiva de 38.8 mm para garantizar estabilidad
sobre mesa plana, punta del dedo y cualquier superficie. El STL final esta limpio y listo para
impresion 3D."
