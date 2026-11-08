# customer-addons — módulos propios para su Odoo de BMyA

Este repositorio es la plantilla para que su equipo desarrolle **sus propios
módulos de Odoo** y los publique en su Odoo de BMyA, sin acceso a nuestros
servidores ni a nuestros repositorios.

Trae todo lo necesario:

- la documentación completa del proceso, en [`docs/`](docs/);
- un módulo de ejemplo que cumple todas las reglas: [`acme_note/`](acme_note/);
- una herramienta para revisar su código en su máquina antes de abrir un PR:
  [`tools/bmya_check.py`](tools/bmya_check.py).

## El camino de un cambio

Siempre el mismo, sin atajos:

1. Abren un **pull request** en su repositorio.
2. **Revisiones automáticas** de BMyA: estilo, seguridad, estructura.
3. **Pruebas en un Odoo efímero** (runbot) con sus módulos instalados: los
   tests tienen que pasar, con la cobertura mínima.
4. Lo suben a **su ambiente de test** cuando quieran (`@robbmya s+ <cliente>`).
5. **Revisión de BMyA**, y si se aprueba, pasa a **producción** en la ventana
   de mantenimiento.

Las revisiones las corre BMyA, no su repositorio: nada que se cambie en este
repo las salta o las modifica. Ver [docs/05-flujo-de-trabajo.md](docs/05-flujo-de-trabajo.md).

## Cómo empezar

**Si todavía no tienen un repositorio**, usen esta plantilla:

1. Botón **«Use this template» → «Create a new repository»**, marcando
   **«Include all branches»**.
2. Sigan [docs/01-puesta-en-marcha.md](docs/01-puesta-en-marcha.md).

**Si ya tienen un repositorio con módulos**, copien a su repo:

- la carpeta `tools/` y el archivo `.pre-commit-config.yaml`;
- las líneas de `.gitignore` que no tengan;

y sigan [docs/01-puesta-en-marcha.md](docs/01-puesta-en-marcha.md) desde el
paso 2. Antes del primer PR, corran `python3 tools/bmya_check.py`: les dice
qué hay que ajustar para cumplir las reglas.

## Documentación

| | |
|---|---|
| [01 · Puesta en marcha](docs/01-puesta-en-marcha.md) | Alta, ramas, instalar la App de BMyA |
| [02 · Estructura del repositorio](docs/02-estructura-del-repositorio.md) | Cómo se organiza un módulo, nombres, versiones, dependencias |
| [03 · Reglas de código](docs/03-reglas-de-codigo.md) | Qué se puede usar y qué no, con el código de cada regla |
| [04 · Tests y cobertura](docs/04-tests-y-cobertura.md) | Cómo escribir los tests y cuánta cobertura se exige |
| [05 · Flujo de trabajo](docs/05-flujo-de-trabajo.md) | PR, pruebas, ambiente de test, revisión y producción |
| [06 · Las revisiones automáticas](docs/06-revisiones-automaticas.md) | Cada revisión, qué mira y cómo se arregla |
| [07 · Trabajar en su máquina](docs/07-trabajar-en-su-maquina.md) | La herramienta local y pre-commit |
| [08 · Preguntas frecuentes](docs/08-preguntas-frecuentes.md) | |

## Ramas de esta plantilla

Hay una rama por versión de Odoo: `17.0`, `18.0`, `19.0` y `20.0`. Cada una
trae el módulo de ejemplo escrito para esa versión. Usen la de su Odoo y
borren las demás (ver la puesta en marcha).

## Sin excepciones

Las reglas valen igual para todos los clientes, y **nadie de BMyA puede
saltarlas** para un PR. Si una regla les bloquea algo legítimo, pídanlo por
ticket: se evalúa como un cambio de la regla para todos.

## Licencia

La documentación, la herramienta de `tools/` y el módulo de ejemplo son de
BMyA. Pueden usarlos, copiarlos y adaptarlos para desarrollar módulos para su
Odoo con BMyA; no se licencian para otro uso.

Los módulos que ustedes escriban son suyos, con la licencia que elijan. Esta
plantilla no trae un archivo `LICENSE` a propósito: si lo trajera, su
repositorio arrancaría declarando una licencia que no eligieron.
