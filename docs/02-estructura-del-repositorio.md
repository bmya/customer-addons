# 02 · Estructura del repositorio

```
su-repositorio/
├── acme_note/              ← un módulo (una carpeta por módulo, en la raíz)
│   ├── __init__.py
│   ├── __manifest__.py
│   ├── README.rst
│   ├── models/
│   ├── security/
│   │   └── ir.model.access.csv   (desde 20.0: ir.access.csv)
│   ├── views/
│   └── tests/              ← obligatorio
│       ├── __init__.py
│       └── test_acme_note.py
├── tools/                  ← herramienta local de BMyA (no es un módulo)
├── docs/
├── .pre-commit-config.yaml
├── .gitignore
└── README.md
```

## Módulos

- **Una carpeta por módulo, en la raíz.** Odoo carga solo las carpetas de la
  raíz que tienen `__manifest__.py`. Lo que esté en subcarpetas no se instala.
- **Nombre:** minúsculas, números y guion bajo. Tiene que ser **único**: no puede
  coincidir con un módulo de Odoo, de Odoo Enterprise ni de BMyA (regla
  [P7](03-reglas-de-codigo.md#p7)). Usen siempre un **prefijo propio**, por
  ejemplo el de su empresa: `acme_`, `acme_sale_report`, `acme_hr_bonus`.
- **Sin submódulos de git** (`.gitmodules`), regla [P4](03-reglas-de-codigo.md#p4).

## El manifiesto (`__manifest__.py`)

Un diccionario literal, sin código:

```python
{
    "name": "Acme · Notas",
    "version": "18.0.1.0.0",
    "summary": "Notas internas de ejemplo",
    "author": "Acme SpA",
    "license": "Other proprietary",
    "depends": ["base"],
    "data": [
        "security/ir.model.access.csv",
        "views/acme_note_views.xml",
    ],
    "installable": True,
}
```

- **`version`:** cinco partes, empezando por la versión de Odoo: `18.0.1.0.0`.
  Súbanla en cada cambio (`18.0.1.0.1`, `18.0.1.1.0`…): si no cambia, el módulo
  no se actualiza en su base.
- **`depends`:** solo módulos que ya están en su Odoo (estándar, Enterprise o de
  BMyA) o en este mismo repositorio (regla [P5](03-reglas-de-codigo.md#p5)). Si
  necesitan uno que su Odoo no tiene, pídanlo por ticket **antes** del PR.
- **`external_dependencies`:** solo las bibliotecas Python de la lista
  permitida (regla [P6](03-reglas-de-codigo.md#p6)). Nada de `bin`.
- **`data`, `demo`, `assets`:** rutas dentro del propio módulo, nunca de otro ni
  remotas (regla [S9](03-reglas-de-codigo.md#s9)).
- **Permisos de acceso en Odoo 20.0:** `ir.model.access` ya no existe. Los
  permisos van en `security/ir.access.csv`, con las columnas
  `id,name,model_id,group_id/id,operation,domain`: `model_id` es el nombre del
  modelo (`acme.note`) y `operation`, las letras de lo permitido (`crud`, `r`,
  `cru`…). Hasta 19.0 sigue siendo `security/ir.model.access.csv`. La rama
  `20.0` de la plantilla trae el ejemplo.
- **`license`:** la que elijan, entre las que Odoo acepta. Los módulos son suyos.
  El ejemplo usa `Other proprietary`, que no publica nada: cámbienla si quieren
  abrir el código.

## Archivos que no pueden estar

- **Configuración de herramientas** (`setup.cfg`, `pyproject.toml`, `tox.ini`,
  `.flake8`, `.isort.cfg`, `.pylintrc`, `.coveragerc`, `requirements.txt`…),
  regla [P3](03-reglas-de-codigo.md#p3). Las revisiones de BMyA corren con su
  propia configuración, que es igual para todos los clientes.
- **Binarios y ejecutables** (`.so`, `.pyc`, `.exe`, `.sh`, `.zip`, `.whl`…) y
  **enlaces simbólicos**, regla [S7](03-reglas-de-codigo.md#s7).

Dentro de un módulo se aceptan: `.py`, `.xml`, `.csv`, `.po`, `.pot`, `.js`,
`.scss`, `.css`, `.html`, `.md`, `.rst`, `.txt`, `.json`, imágenes (`.png`,
`.jpg`, `.jpeg`, `.gif`, `.svg`, `.ico`, `.webp`), fuentes (`.woff`, `.woff2`,
`.ttf`), `.pdf` y `.xlsx`.

## La carpeta `tools/`

Es la herramienta de BMyA para revisar su código en su máquina
([07](07-trabajar-en-su-maquina.md)). No es un módulo y Odoo no la carga. Cuando
publiquemos una versión nueva de las reglas, actualícenla copiándola de la
plantilla.
