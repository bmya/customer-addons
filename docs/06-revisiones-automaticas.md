# 06 · Las revisiones automáticas

Aparecen en cada PR, abajo, con un enlace *Details* que abre el detalle. Las
corre BMyA con su propia configuración: lo que haya en su repositorio no las
cambia. Para volver a correrlas: `@robbmya recheck`.

| Revisión | Qué mira | Cómo se arregla |
|---|---|---|
| `ci/commits` | Que el PR tenga **un solo commit** | `git reset --soft origin/<versión> && git commit`, y `git push --force-with-lease` |
| `ci/conflicts` | Marcadores de conflicto de git (`<<<<<<<`, `=======`, `>>>>>>>`) en cualquier archivo | Resolver el conflicto y volver a commitear |
| `ci/style` | Formato de Python con **isort** (perfil `black`) y **flake8** (líneas de hasta 120) | `isort --profile black <archivos>` y corregir lo que diga flake8 (ver [07](07-trabajar-en-su-maquina.md)) |
| `ci/odoolint` | Buenas prácticas de módulos Odoo (`oca-checks-odoo-module`): manifiesto, XML, vistas, README | El detalle dice qué regla y en qué línea |
| `ci/security` | Que cada modelo tenga permisos de acceso, y las reglas **S** de [03](03-reglas-de-codigo.md) | Agregar la línea en `security/ir.model.access.csv` (desde 20.0, `security/ir.access.csv`); para una regla S, su sección en 03 |
| `ci/policy` | Las reglas **P** de [03](03-reglas-de-codigo.md): rama, estructura, dependencias, tests | Su sección en 03 |
| `ci/version` | Que la `version` de cada módulo que cambia tenga 5 partes y empiece con su versión de Odoo (`18.0.x.y.z`) | Corregir el manifiesto |
| `runbot/tests` | Que los tests pasen en el runbot, y que corra al menos uno | El detalle trae el log de los tests |
| `runbot/coverage` | Que cada módulo que cambia tenga **70 %** de cobertura o más | Más tests sobre las líneas que el detalle marca como no ejecutadas |

## Cuándo se exige cada una

| Para… | Hace falta en verde |
|---|---|
| Subir a su test (`s+`) | Todas |
| Pasar a producción (`r+`) | Todas, más la aprobación de BMyA |

No hay forma de forzar una revisión en rojo en un repositorio de cliente.

## Si una revisión queda en amarillo mucho tiempo

Comenten `@robbmya recheck`. Si sigue igual, avísennos desde «Soporte de mis módulos», en su [panel de cliente](https://www.bmya.cl/my/customerpanel),
con el enlace al PR.

## Si creen que una revisión se equivoca

Puede pasar, sobre todo con las reglas S, que son estrictas a propósito.
Avísennos desde «Soporte de mis módulos», en su [panel de cliente](https://www.bmya.cl/my/customerpanel), con el enlace al PR y la línea. Si es un error de la regla, la
corregimos para todos; mientras tanto, el PR no se puede forzar.
