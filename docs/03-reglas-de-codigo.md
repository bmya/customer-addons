# 03 · Reglas de código

Su código corre en el mismo Odoo y en el mismo servidor que los módulos de BMyA
y los de Odoo. Por eso hay reglas sobre **qué puede usar** el código, además de
las de estilo. Las aplican dos revisiones automáticas:

- **`ci/security`** — reglas **S**: qué puede hacer el código.
- **`ci/policy`** — reglas **P**: cómo se organiza el repositorio.

Cada mensaje de error empieza con el código de la regla (`[S1]`, `[P8]`…), que
lleva a su sección acá. Las mismas reglas las corre `tools/bmya_check.py` en su
máquina ([07](07-trabajar-en-su-maquina.md)).

**No hay excepciones por PR.** Si una regla les impide algo legítimo, pídanlo
por ticket: si se acepta, cambia la regla para todos los clientes.

---

## Qué pueden importar

Solo lo de esta lista. Todo lo demás se rechaza ([S1](#s1)).

| Módulo | Qué se puede importar |
|---|---|
| `odoo` y sus submódulos, incluidos `odoo.addons.*` | Todo, salvo `odoo.cli`, `odoo.modules`, `odoo.service`, `odoo.sql_db`, `odoo.tools.config`, `odoo.tools.misc`, `odoo.tools.safe_eval` y `odoo.tools.sql` |
| `base64`, `calendar`, `collections`, `contextlib`, `copy`, `csv`, `dataclasses`, `datetime`, `decimal`, `enum`, `functools`, `hashlib`, `hmac`, `html`, `itertools`, `json`, `logging`, `math`, `random`, `re`, `secrets`, `statistics`, `string`, `textwrap`, `time`, `typing`, `unicodedata`, `urllib.parse`, `uuid`, `zoneinfo` | Todo |
| `ast` | Solo `literal_eval` |
| `io` | Solo `BytesIO` y `StringIO` |
| `operator` | Funciones de comparación y aritmética, e `itemgetter`. No `attrgetter` ni `methodcaller` |
| `dateutil`, `markupsafe`, `pytz`, `requests`, `xlsxwriter`, `werkzeug.exceptions` | Todo |
| `lxml` | `etree` y `html`, sin `etree.parse` ni `iterparse` |
| Su propio módulo (`from . import …`, `from .models import …`) | Todo |

**Para hablar con otros sistemas** (APIs, servicios web) usen `requests`, siempre
con `timeout`.

**Lo que no está a propósito:** `os`, `sys`, `subprocess`, `socket`, `shutil`,
`pathlib`, `glob`, `importlib`, `inspect`, `pickle`, `marshal`, `ctypes`,
`threading`, `multiprocessing`, `urllib.request`, `xmlrpc`, `openpyxl`, entre
otros. Leen archivos del servidor, ejecutan procesos o permiten llegar a
cualquiera de esas cosas de forma indirecta.

---

## Reglas S · `ci/security`

<a id="s1"></a>
### S1 · Import no permitido

Un `import` o `from … import …` que no está en la tabla de arriba. También
`from x import *`.

<a id="s2"></a>
### S2 · Función de Python prohibida

`open`, `eval`, `exec`, `compile`, `__import__`, `globals`, `locals`, `vars`,
`input`, `breakpoint`, `exit`, `quit`. Leen archivos o ejecutan código armado
en el momento.

- ¿Necesitan un archivo? Que lo suba el usuario y llegue como adjunto
  (`ir.attachment`, campo `Binary`), o que viva en `static/` de su módulo y se
  sirva por URL.
- ¿Necesitan evaluar una expresión? `ast.literal_eval` para literales; para
  dominios, los campos de dominio de Odoo.

<a id="s3"></a>
### S3 · Atributo o nombre interno de Python (dunder)

Nombres con doble guion bajo como `__dict__`, `__globals__`, `__file__`,
`__builtins__`, `__subclasses__`, también dentro de un string de formato
(`"{x.__init__…}"`). Se permiten `__name__`, `__all__`, `__init__` y
`__class__`.

<a id="s4"></a>
### S4 · Acceso a archivos del servidor o a la configuración de Odoo

Funciones y atributos que leen archivos o la configuración del servidor:
`file_open`, `file_path`, `get_module_path`, `get_resource_path`,
`get_module_resource`, `tools.config`, `addons_path`, `root_path`, el
filestore por ruta (`_full_path`, `_file_read`), `etree.parse`, `iterparse`,
`XInclude`, `fileConfig`, y los submódulos `odoo.service`, `odoo.sql_db`,
`odoo.modules`, `odoo.tools.misc` usados como atributo.

Para leer un adjunto usen el ORM: `attachment.raw` o `attachment.datas`.

<a id="s5"></a>
### S5 · SQL o cursor directo: usar el ORM

`self.env.cr`, `self._cr`, `.execute(…)`, `SQL(…)`, `.cursor()`. Todo acceso a
datos va por el ORM: `search`, `read_group` / `_read_group`, `search_count`,
`write`, `create`.

¿Por qué tan estricto? Una consulta SQL corre con los permisos del servidor de
base de datos, no con los del usuario de Odoo, y desde ahí se puede leer o
ejecutar cosas en el servidor. El ORM respeta permisos y reglas de acceso.

<a id="s6"></a>
### S6 · getattr/setattr dinámico sobre algo importado

`getattr(modulo, nombre_variable)` sobre un módulo importado, o
`getattr(x, "nombre_prohibido")`. Sobre registros sí se puede:
`getattr(record, field_name)`.

<a id="s7"></a>
### S7 · Tipo de archivo no permitido o enlace simbólico

Binarios, bibliotecas compiladas, scripts de shell, comprimidos y **enlaces
simbólicos**, en cualquier parte del repositorio. Dentro de un módulo, cualquier
tipo que no esté en la lista de [02](02-estructura-del-repositorio.md#archivos-que-no-pueden-estar).

<a id="s8"></a>
### S8 · JavaScript que ejecuta código armado en el momento

`eval(…)` y `new Function(…)` en archivos `.js`.

<a id="s9"></a>
### S9 · Manifiesto con recursos fuera del módulo o remotos

En `data`, `demo` y `assets` del manifiesto: rutas de otro módulo, con `..`,
absolutas o URLs (`https://…`). Los assets de su módulo empiezan con
`<su_modulo>/static/…`.

<a id="s10"></a>
### S10 · Archivo Python que no se puede analizar

Un `.py` con un error de sintaxis, o un manifiesto que no es un diccionario
literal. Se rechaza porque no se puede revisar.

<a id="s11"></a>
### S11 · Archivo de datos que lee un archivo fuera del módulo

Un `file="…"` en un XML de datos que apunta a otro módulo o sale del propio
(`..`, ruta absoluta). Tiene que empezar con `<su_modulo>/`.

---

## Reglas P · `ci/policy`

<a id="p1"></a>
### P1 · Rama base no permitida

El PR tiene que apuntar a la rama de su versión, con ese nombre exacto (`18.0`).
Nunca a `main`, `master`, `18.0-dev` ni ninguna otra: el repositorio trabaja con
una sola rama ([01](01-puesta-en-marcha.md#4-la-rama)).

La única otra base aceptada es la **versión siguiente** (`19.0` si están en
`18.0`), para preparar una migración: esos PRs pasan por las revisiones y el
runbot, pero `s+` y `r+` los rechazan hasta que su Odoo se migre. Ver
[05](05-flujo-de-trabajo.md#7-preparar-una-migración).

<a id="p2"></a>
### P2 · Comentario que apaga un control

`# noqa`, `# nosec`, `# pylint: disable`, `# isort: skip`,
`# pragma: no cover`, `# type: ignore`. Arreglen el código en vez de
silenciarlo.

<a id="p3"></a>
### P3 · Configuración de herramientas en el repositorio

`setup.cfg`, `setup.py`, `pyproject.toml`, `tox.ini`, `.flake8`, `.isort.cfg`,
`.pylintrc`, `.coveragerc`, `.bmya-ci.yml`, `requirements.txt`,
`test-requirements.txt`. Las revisiones usan la configuración de BMyA.

<a id="p4"></a>
### P4 · Submódulos de git

Un `.gitmodules` en el repositorio.

<a id="p5"></a>
### P5 · Dependencia de un módulo que no está en el proyecto

Un módulo en `depends` que su Odoo no tiene y que tampoco está en este
repositorio. Pidan por ticket que se agregue a su Odoo antes del PR. La revisa
solo el CI de BMyA: su máquina no sabe qué módulos tiene su Odoo.

<a id="p6"></a>
### P6 · Dependencia Python o de sistema no permitida

En `external_dependencies`: en `python`, solo `dateutil` (o `python-dateutil`),
`lxml`, `markupsafe`, `pytz`, `requests` y `xlsxwriter`. En `bin`, nada. En los
servidores de BMyA no se instala nada desde internet.

<a id="p7"></a>
### P7 · Nombre de módulo que ya usa Odoo o BMyA

Un módulo con el mismo nombre que uno de Odoo, de Odoo Enterprise o de BMyA lo
reemplazaría. Usen su prefijo. La revisa solo el CI de BMyA.

<a id="p8"></a>
### P8 · Módulo sin tests

Cada módulo tiene `tests/__init__.py` que importa al menos un archivo con una
clase de test (`TransactionCase` o `HttpCase`). Ver
[04](04-tests-y-cobertura.md).

---

## Lo que revisa una persona de BMyA antes de aprobar

Además de lo automático, antes del paso a producción revisamos:

- que los tests prueben lo que el módulo hace, con asserts que fallarían si el
  módulo estuviera mal;
- `sudo()` solo donde hace falta, con el motivo en un comentario;
- que las llamadas a otros sistemas tengan `timeout` y manejen los errores;
- que nada cambie el comportamiento de otros módulos de forma que una
  actualización los rompa;
- que nada intente esquivar estas reglas. Un cambio que lo intente se rechaza,
  aunque las revisiones automáticas den verde.
