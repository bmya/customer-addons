============
Acme · Notas
============

Módulo de ejemplo de la plantilla `bmya/customer-addons
<https://github.com/bmya/customer-addons>`_: notas internas con fecha límite.

Muestra, en poco código, todo lo que un módulo de cliente necesita para pasar
las revisiones de BMyA: modelo, permisos de acceso, vistas, una validación y
tests con la cobertura mínima.

Uso
===

*Ajustes → Técnico → Notas Acme* (con el modo desarrollador activo). Una nota se
marca como hecha con el botón **Hecha**; si tiene fecha límite y no está hecha,
queda marcada como vencida cuando la fecha pasa.

Para usarlo como molde, copien la carpeta con el nombre de su módulo y
reemplacen ``acme_note`` y ``acme.note`` en todos los archivos.
