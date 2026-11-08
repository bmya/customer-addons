"""Reglas para el código de los repos de módulos propios de clientes.

Fuente única de las reglas. Se usa en dos lugares, con este mismo archivo:

- el CI de BMyA (`ci/security` y `ci/policy` sobre un repo de cliente), que es
  el que decide; el cliente no puede cambiarlo;
- `tools/bmya_policy.py` del repo público `bmya/customer-addons`, copia
  byte a byte de este archivo (un test lo exige), para que el cliente corra
  lo mismo en su máquina antes de abrir el PR.

Solo stdlib y sin imports de la app: tiene que correr suelto en la laptop
del cliente.

Por qué una lista PERMITIDA de imports y no una prohibida: el código de un
cliente corre en el mismo proceso que nuestros módulos y en el mismo disco
que su código fuente. Una lista prohibida siempre deja un camino que no se
pensó (lxml lee archivos, openpyxl lee archivos, logging.config lee
archivos…). Con una permitida, lo que no está no entra, y agregar algo es una
decisión que vale para todos los clientes.

Ningún análisis estático hace imposible el código malicioso: Python es
demasiado dinámico. Esto sube el costo y vuelve visible el intento (para
esquivarlo hay que escribir algo raro, y eso lo ve el review del `r+`). Las
otras capas: el runbot del cliente corre sin red y sin token, y el `r+` lo da
una persona de BMyA.

Cada regla tiene un código fijo (S…, P…) que la documentación del cliente cita.
Un código no se reutiliza para otra cosa.
"""
from __future__ import annotations

import ast
import os
import re
from dataclasses import dataclass

POLICY_VERSION = "2"

# Cobertura mínima de tests por módulo tocado (runbot/coverage). Una sola para
# todos los clientes: no hay umbral por cliente que se pueda pedir bajar.
COVERAGE_MIN = 70

# --------------------------------------------------------------------------
# Imports permitidos. Clave: módulo (o prefijo de paquete con ".*").
# Valor: "*" = cualquier nombre; un conjunto = solo esos nombres en
# `from x import ...`.
# --------------------------------------------------------------------------
ALLOWED_IMPORTS: dict[str, object] = {
    # Odoo: todo, salvo los submódulos de DENIED_ODOO_MODULES.
    "odoo": "*",
    "odoo.*": "*",
    # Biblioteca estándar sin acceso a archivos, procesos ni introspección.
    "ast": {"literal_eval"},
    "base64": "*",
    "calendar": "*",
    "collections": "*",
    "collections.abc": "*",
    "contextlib": "*",
    "copy": "*",
    "csv": "*",
    "dataclasses": "*",
    "datetime": "*",
    "decimal": "*",
    "enum": "*",
    "functools": "*",
    "hashlib": "*",
    "hmac": "*",
    "html": "*",
    "io": {"BytesIO", "StringIO"},
    "itertools": "*",
    "json": "*",
    "logging": "*",
    "math": "*",
    # Sin attrgetter/methodcaller: llegan a cualquier atributo por nombre.
    "operator": {"itemgetter", "add", "sub", "mul", "truediv", "floordiv", "mod",
                 "neg", "eq", "ne", "lt", "le", "gt", "ge", "and_", "or_", "not_",
                 "contains"},
    "random": "*",
    "re": "*",
    "secrets": "*",
    "statistics": "*",
    "string": "*",
    "textwrap": "*",
    "time": "*",
    "typing": "*",
    "unicodedata": "*",
    "urllib.parse": "*",
    "uuid": "*",
    "zoneinfo": "*",
    # Terceros que ya trae la imagen.
    "dateutil": "*",
    "dateutil.*": "*",
    "lxml": {"etree", "html"},
    "lxml.etree": "*",
    "markupsafe": "*",
    "pytz": "*",
    "requests": "*",
    "requests.*": "*",
    "werkzeug.exceptions": "*",
    "xlsxwriter": "*",
}

# Solo dentro de `<modulo>/tests/`: los tests corren en el runbot, sin red, y
# simulan las respuestas de otros sistemas con mock.
TEST_ONLY_IMPORTS: dict[str, object] = {
    "unittest": "*",
    "unittest.mock": "*",
}

# Submódulos de odoo que dan acceso a la configuración del servidor (con la
# clave de la base), a cursores crudos, a rutas del disco o a la línea de
# comandos.
DENIED_ODOO_MODULES = (
    "odoo.cli",
    "odoo.modules",
    "odoo.service",
    "odoo.sql_db",
    "odoo.tools.config",
    "odoo.tools.misc",
    "odoo.tools.safe_eval",
    "odoo.tools.sql",
)

# Dependencias Python que un manifiesto puede declarar: las que la imagen ya
# trae y la lista de imports permite. Nada se instala de PyPI en nuestros
# servidores.
ALLOWED_PY_DEPENDENCIES = frozenset({
    "dateutil", "python-dateutil", "lxml", "markupsafe", "pytz", "requests",
    "xlsxwriter",
})

# Funciones de Python que leen archivos, ejecutan código armado en el
# momento o exponen el intérprete.
FORBIDDEN_BUILTINS = frozenset({
    "__import__", "breakpoint", "compile", "eval", "exec", "exit", "globals",
    "input", "locals", "open", "quit", "vars",
})

# Nombres "dunder" que sí se pueden usar.
ALLOWED_DUNDER_NAMES = frozenset({"__name__", "__all__"})
ALLOWED_DUNDER_ATTRS = frozenset({"__init__", "__name__", "__class__"})

# Archivos sin extensión que se aceptan dentro de un módulo.
MODULE_PLAIN_FILES = frozenset({"LICENSE", "COPYING", ".gitkeep"})

# Atributos y nombres que dan acceso a archivos del servidor, a la
# configuración de Odoo o al filestore por ruta.
FILE_ACCESS_NAMES = frozenset({
    "addons_path", "config", "file_open", "file_path", "fileConfig", "filestore",
    "get_module_path", "get_module_resource", "get_resource_from_path",
    "get_resource_path", "iterparse", "root_path", "xinclude", "XInclude",
    "_file_read", "_filestore", "_full_path", "_get_path",
})

# Los mismos submódulos de DENIED_ODOO_MODULES, alcanzados como atributo
# (`odoo.service.db.exp_dump`, `tools.misc.file_open`) en vez de importados.
DENIED_ODOO_ATTRS = frozenset({"cli", "misc", "modules", "safe_eval", "service", "sql", "sql_db"})

# SQL y cursores: el usuario de Postgres de la flota es superusuario, así que
# un `COPY ... FROM PROGRAM` o un `pg_read_file` ejecuta comandos o lee
# archivos en el servidor. Solo ORM.
SQL_NAMES = frozenset({
    "SQL", "copy_expert", "copy_from", "copy_to", "cr", "_cr", "cursor",
    "execute", "executemany", "mogrify",
})

# getattr/setattr con un nombre armado en el momento sobre algo importado
# llega a cualquier cosa de ese módulo, incluidas las prohibidas.
DYNAMIC_ATTR_FUNCS = frozenset({"delattr", "getattr", "hasattr", "setattr"})

# Comentarios que apagan un control.
SUPPRESSION_RE = re.compile(
    r"#\s*(noqa\b|nosec\b|pylint:\s*disable|isort:\s*(skip|off)|"
    r"pragma:\s*no\s*cover|type:\s*ignore)",
    re.IGNORECASE,
)

# Config de herramientas que un repo de cliente no puede traer: el CI de
# BMyA corre con la suya, y estos archivos cambian lo que se revisa (o, en el
# caso de pyproject.toml, lo que se instala).
REPO_CONFIG_FILES = frozenset({
    ".bmya-ci.yml", ".coveragerc", ".flake8", ".isort.cfg", ".oca_hooks.cfg", ".pylintrc",
    "pylintrc", "pyproject.toml", "setup.cfg", "setup.py", "tox.ini",
    "requirements.txt", "test-requirements.txt",
})

# Tipos de archivo dentro de un módulo. Todo lo demás (binarios, bibliotecas
# compiladas, scripts de shell, comprimidos) se rechaza.
MODULE_FILE_SUFFIXES = frozenset({
    ".py", ".xml", ".csv", ".po", ".pot", ".js", ".scss", ".css", ".html",
    ".md", ".rst", ".txt", ".json",
    ".png", ".jpg", ".jpeg", ".gif", ".svg", ".ico", ".webp",
    ".woff", ".woff2", ".ttf", ".pdf", ".xlsx",
})

# Los únicos binarios aceptados fuera de los módulos son imágenes de la doc.
BINARY_SUFFIXES = frozenset({
    ".so", ".pyd", ".pyc", ".pyo", ".dll", ".dylib", ".exe", ".bin", ".sh",
    ".bash", ".zip", ".tar", ".gz", ".tgz", ".bz2", ".xz", ".7z", ".whl",
    ".egg", ".jar", ".class", ".deb", ".rpm",
})

# "{x.__init__.__globals__}".format(x=...) llega a lo mismo que un atributo
# dunder, pero dentro de un string.
FORMAT_DUNDER_RE = re.compile(r"\{[^{}]*\.__\w+__")
JS_FORBIDDEN_RE = re.compile(r"\beval\s*\(|\bnew\s+Function\s*\(|(?<![\w.])Function\s*\(")
XML_FILE_ATTR_RE = re.compile(rb"""\bfile\s*=\s*["']([^"']+)["']""")
TEST_CASE_BASE_RE = re.compile(r"(TransactionCase|HttpCase|SavepointCase|SingleTransactionCase|Case)$")

RULES = {
    "S1": "import no permitido",
    "S2": "función de Python prohibida",
    "S3": "atributo o nombre interno de Python (dunder)",
    "S4": "acceso a archivos del servidor o a la configuración de Odoo",
    "S5": "SQL o cursor directo: usar el ORM",
    "S6": "getattr/setattr dinámico sobre algo importado",
    "S7": "tipo de archivo no permitido o enlace simbólico",
    "S8": "JavaScript que ejecuta código armado en el momento",
    "S9": "manifiesto con recursos fuera del módulo o remotos",
    "S10": "archivo Python que no se puede analizar",
    "S11": "archivo de datos que lee un archivo fuera del módulo",
    "P1": "rama base no permitida",
    "P2": "comentario que apaga un control",
    "P3": "configuración de herramientas en el repositorio",
    "P4": "submódulos de git",
    "P5": "dependencia de un módulo que no está en el proyecto",
    "P6": "dependencia Python o de sistema no permitida",
    "P7": "nombre de módulo que ya usa Odoo o BMyA",
    "P8": "módulo sin tests",
    "P9": "clave de manifiesto no permitida",
}


@dataclass(frozen=True)
class Violation:
    code: str
    path: str
    line: int
    detail: str

    def __str__(self) -> str:
        where = f"{self.path}:{self.line}" if self.line else self.path
        return f"{where}: [{self.code}] {RULES[self.code]}: {self.detail}"


# --------------------------------------------------------------------------
# Python
# --------------------------------------------------------------------------

def _import_allowed(module: str, test: bool = False) -> object:
    """Lo que se permite importar de `module`, o None si el módulo no entra."""
    if test and module in TEST_ONLY_IMPORTS:
        return TEST_ONLY_IMPORTS[module]
    if module == "odoo" or module.startswith("odoo."):
        if any(module == d or module.startswith(d + ".") for d in DENIED_ODOO_MODULES):
            return None
        return "*"
    if module in ALLOWED_IMPORTS:
        return ALLOWED_IMPORTS[module]
    parts = module.split(".")
    for i in range(len(parts) - 1, 0, -1):
        if ".".join(parts[:i]) + ".*" in ALLOWED_IMPORTS:
            return "*"
    return None


def _root_name(node: ast.AST) -> str | None:
    while isinstance(node, (ast.Attribute, ast.Subscript, ast.Call)):
        node = node.func if isinstance(node, ast.Call) else node.value
    return node.id if isinstance(node, ast.Name) else None


def _is_dunder(name: str) -> bool:
    return len(name) > 4 and name.startswith("__") and name.endswith("__")


def _from_import_ok(module: str, name: str, test: bool = False) -> bool:
    if module == "odoo" or module.startswith("odoo."):
        # `from odoo import service`, `from odoo.tools import config`
        return _import_allowed(module) is not None and _import_allowed(f"{module}.{name}") is not None
    allowed = _import_allowed(module, test)
    if allowed == "*":
        return True
    if isinstance(allowed, (set, frozenset)) and name in allowed:
        return True
    # `from urllib import parse` entra porque `urllib.parse` entra.
    return _import_allowed(f"{module}.{name}", test) == "*"


def _is_test_file(rel: str) -> bool:
    return "tests" in rel.replace("\\", "/").split("/")[1:-1]


def check_python_source(source: str, rel: str) -> list[Violation]:
    try:
        tree = ast.parse(source, filename=rel)
    except SyntaxError as e:
        return [Violation("S10", rel, e.lineno or 0, str(e.msg))]

    out: list[Violation] = []

    # Primera pasada: imports. La segunda necesita saber todo lo importado.
    imported: set[str] = set()
    test = _is_test_file(rel)
    for node in ast.walk(tree):
        line = getattr(node, "lineno", 0)
        if isinstance(node, ast.Import):
            for alias in node.names:
                if _import_allowed(alias.name, test) != "*":
                    out.append(Violation("S1", rel, line, f"import {alias.name}"))
                imported.add((alias.asname or alias.name).split(".")[0])
        elif isinstance(node, ast.ImportFrom):
            for alias in node.names:
                imported.add(alias.asname or alias.name)
                if node.level:  # relativo: código del propio módulo
                    continue
                module = node.module or ""
                if alias.name == "*" or not _from_import_ok(module, alias.name, test):
                    out.append(Violation("S1", rel, line, f"from {module} import {alias.name}"))
                if alias.name in FILE_ACCESS_NAMES:
                    out.append(Violation("S4", rel, line, alias.name))
                if alias.name in SQL_NAMES:
                    out.append(Violation("S5", rel, line, alias.name))

    for node in ast.walk(tree):
        line = getattr(node, "lineno", 0)
        if isinstance(node, ast.Name):
            if node.id in FORBIDDEN_BUILTINS:
                out.append(Violation("S2", rel, line, node.id))
            elif _is_dunder(node.id) and node.id not in ALLOWED_DUNDER_NAMES:
                out.append(Violation("S3", rel, line, node.id))
        elif isinstance(node, ast.Attribute):
            if _is_dunder(node.attr) and node.attr not in ALLOWED_DUNDER_ATTRS:
                out.append(Violation("S3", rel, line, f".{node.attr}"))
            elif node.attr in FILE_ACCESS_NAMES or node.attr in DENIED_ODOO_ATTRS:
                out.append(Violation("S4", rel, line, f".{node.attr}"))
            elif node.attr in SQL_NAMES:
                out.append(Violation("S5", rel, line, f".{node.attr}"))
            elif node.attr == "parse" and _root_name(node.value) in ("etree", "lxml"):
                out.append(Violation("S4", rel, line, "etree.parse"))
        elif isinstance(node, ast.Constant) and isinstance(node.value, str):
            if FORMAT_DUNDER_RE.search(node.value):
                out.append(Violation("S3", rel, line, "atributo dunder dentro de un string de formato"))
        elif isinstance(node, ast.Call):
            func = node.func
            if isinstance(func, ast.Name) and func.id in DYNAMIC_ATTR_FUNCS and len(node.args) >= 2:
                target, name = node.args[0], node.args[1]
                if isinstance(name, ast.Constant) and isinstance(name.value, str):
                    forbidden = FILE_ACCESS_NAMES | SQL_NAMES | FORBIDDEN_BUILTINS | DENIED_ODOO_ATTRS
                    if _is_dunder(name.value):
                        out.append(Violation("S3", rel, line, f"{func.id}(…, {name.value!r})"))
                    elif name.value in forbidden:
                        out.append(Violation("S6", rel, line, f"{func.id}(…, {name.value!r})"))
                elif _root_name(target) in imported:
                    out.append(Violation("S6", rel, line, f"{func.id}({_root_name(target)}, …)"))

    for i, text in enumerate(source.splitlines(), 1):
        m = SUPPRESSION_RE.search(text)
        if m:
            out.append(Violation("P2", rel, i, m.group(0).strip()))
    return sorted(out, key=lambda v: (v.line, v.code))


# --------------------------------------------------------------------------
# Manifiesto, datos, JS
# --------------------------------------------------------------------------

def _paths_in_assets(assets) -> list[str]:
    out: list[str] = []
    for entries in (assets or {}).values():
        for e in entries or []:
            if isinstance(e, str):
                out.append(e)
            elif isinstance(e, (list, tuple)):
                out.extend(x for x in e[1:] if isinstance(x, str))
    return out


# Claves del manifiesto que un repo de cliente no puede declarar. `cloc_exclude`
# saca archivos de la medición de líneas con que se cotiza el soporte de sus
# módulos (`odoo-bin cloc`): declararla achicaría la medición a voluntad.
FORBIDDEN_MANIFEST_KEYS = frozenset({"cloc_exclude"})


def check_manifest(source: str, rel: str, module: str) -> tuple[list[Violation], dict]:
    try:
        data = ast.literal_eval(source)
    except (ValueError, SyntaxError) as e:
        return [Violation("S10", rel, 0, f"el manifiesto no es un literal: {e}")], {}
    if not isinstance(data, dict):
        return [Violation("S10", rel, 0, "el manifiesto no es un diccionario")], {}

    out: list[Violation] = []
    for key in ("data", "demo", "qweb"):
        for p in data.get(key) or []:
            if not isinstance(p, str) or p.startswith(("/", "..")) or "/../" in f"/{p}":
                out.append(Violation("S9", rel, 0, f"{key}: {p!r}"))
    for p in _paths_in_assets(data.get("assets")):
        if "//" in p or p.startswith(("http:", "https:")):
            out.append(Violation("S9", rel, 0, f"assets remoto: {p!r}"))
        elif ".." in p.split("/") or not p.startswith(f"{module}/"):
            out.append(Violation("S9", rel, 0, f"assets fuera del módulo: {p!r}"))

    for key in sorted(FORBIDDEN_MANIFEST_KEYS & set(data)):
        out.append(Violation("P9", rel, 0, key))

    ext = data.get("external_dependencies") or {}
    for dep in ext.get("python") or []:
        if str(dep).lower() not in ALLOWED_PY_DEPENDENCIES:
            out.append(Violation("P6", rel, 0, f"python: {dep}"))
    for dep in ext.get("bin") or []:
        out.append(Violation("P6", rel, 0, f"bin: {dep}"))
    return out, data


def check_data_file(content: bytes, rel: str, module: str) -> list[Violation]:
    out: list[Violation] = []
    for m in XML_FILE_ATTR_RE.finditer(content):
        path = m.group(1).decode("utf-8", "replace")
        line = content.count(b"\n", 0, m.start()) + 1
        if ".." in path.split("/") or path.startswith("/") or not path.startswith(f"{module}/"):
            out.append(Violation("S11", rel, line, f"file={path!r}"))
    return out


def check_js(source: str, rel: str) -> list[Violation]:
    out: list[Violation] = []
    for i, text in enumerate(source.splitlines(), 1):
        stripped = text.strip()
        if stripped.startswith(("//", "*", "/*")):
            continue
        if JS_FORBIDDEN_RE.search(text):
            out.append(Violation("S8", rel, i, stripped[:80]))
    return out


def _has_tests(module_dir: str) -> bool:
    init = os.path.join(module_dir, "tests", "__init__.py")
    if not os.path.isfile(init):
        return False
    try:
        tree = ast.parse(open(init, encoding="utf-8").read())
    except (OSError, SyntaxError):
        return False
    names = [a.name for n in ast.walk(tree) if isinstance(n, ast.ImportFrom) and n.level
             for a in n.names]
    for name in names:
        path = os.path.join(module_dir, "tests", f"{name}.py")
        try:
            t = ast.parse(open(path, encoding="utf-8").read())
        except (OSError, SyntaxError):
            continue
        for node in ast.walk(t):
            if isinstance(node, ast.ClassDef):
                for base in node.bases:
                    base_name = base.attr if isinstance(base, ast.Attribute) else getattr(base, "id", "")
                    if TEST_CASE_BASE_RE.search(base_name or ""):
                        return True
    return False


# --------------------------------------------------------------------------
# Repositorio completo
# --------------------------------------------------------------------------

@dataclass
class Context:
    """Lo que el CI de BMyA sabe y la laptop del cliente no. None = no se
    revisa acá (la regla la aplica el CI de BMyA)."""
    odoo_version: str | None = None       # serie del cliente, ej. "18.0"
    base_branch: str | None = None        # rama destino del PR
    # La versión siguiente a la del cliente (catalog/branches.yml), para
    # preparar una migración: acepta PRs con CI y runbot, nunca s+ ni r+.
    migration_version: str | None = None
    available_modules: frozenset | None = None   # módulos del proyecto del cliente
    reserved_names: frozenset | None = None      # nombres de Odoo + BMyA en esa serie


def _modules(root: str) -> list[str]:
    return sorted(
        d for d in os.listdir(root)
        if os.path.isfile(os.path.join(root, d, "__manifest__.py"))
    )


def check_repository(root: str, ctx: Context | None = None,
                     only_modules: set[str] | None = None) -> list[Violation]:
    """Todas las reglas sobre el árbol en `root`. `only_modules`: limitar las
    reglas por módulo a esos (los que toca un PR); las del repo corren igual."""
    ctx = ctx or Context()
    out: list[Violation] = []

    if ctx.base_branch is not None and ctx.odoo_version:
        # Una sola rama por versión en el repo del cliente: el test lo arma el
        # bot en el espejo de BMyA, nunca con otra rama en su repo.
        allowed = [ctx.odoo_version] + ([ctx.migration_version] if ctx.migration_version else [])
        if ctx.base_branch not in allowed:
            out.append(Violation("P1", ctx.base_branch, 0,
                                 f"el PR apunta a {ctx.base_branch}; solo {' o '.join(allowed)}"))

    modules = _modules(root)
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d != ".git"]
        rel_dir = os.path.relpath(dirpath, root)
        top = rel_dir.split(os.sep)[0]
        in_module = top in modules
        for name in dirnames + filenames:
            path = os.path.join(dirpath, name)
            rel = os.path.normpath(os.path.join(rel_dir, name))
            if os.path.islink(path):
                out.append(Violation("S7", rel, 0, "enlace simbólico"))
                continue
            if name not in filenames:
                continue
            suffix = os.path.splitext(name)[1].lower()
            if rel_dir == "." and name == ".gitmodules":
                out.append(Violation("P4", rel, 0, ".gitmodules"))
            if name in REPO_CONFIG_FILES:
                out.append(Violation("P3", rel, 0, name))
            if suffix in BINARY_SUFFIXES:
                out.append(Violation("S7", rel, 0, f"tipo {suffix}"))
            elif (in_module and suffix not in MODULE_FILE_SUFFIXES
                  and name != "__manifest__.py" and name not in MODULE_PLAIN_FILES):
                out.append(Violation("S7", rel, 0, f"tipo {suffix or 'sin extensión'}"))

    for module in modules:
        if only_modules is not None and module not in only_modules:
            continue
        mdir = os.path.join(root, module)
        if ctx.reserved_names is not None and module in ctx.reserved_names:
            out.append(Violation("P7", module, 0, module))
        manifest_rel = f"{module}/__manifest__.py"
        with open(os.path.join(mdir, "__manifest__.py"), encoding="utf-8") as f:
            violations, manifest = check_manifest(f.read(), manifest_rel, module)
        out += violations
        if ctx.available_modules is not None:
            for dep in manifest.get("depends") or []:
                if dep not in ctx.available_modules and dep not in modules:
                    out.append(Violation("P5", manifest_rel, 0, dep))
        if not _has_tests(mdir):
            out.append(Violation("P8", module, 0, "falta tests/ con al menos un TransactionCase o HttpCase"))
        for dirpath, dirnames, filenames in os.walk(mdir):
            for name in filenames:
                path = os.path.join(dirpath, name)
                rel = os.path.relpath(path, root)
                if os.path.islink(path) or name == "__manifest__.py":
                    continue
                suffix = os.path.splitext(name)[1].lower()
                if suffix not in (".py", ".js", ".xml", ".csv"):
                    continue
                with open(path, "rb") as f:
                    raw = f.read()
                if suffix == ".py":
                    out += check_python_source(raw.decode("utf-8", "replace"), rel)
                elif suffix == ".js":
                    out += check_js(raw.decode("utf-8", "replace"), rel)
                elif suffix == ".xml":
                    out += check_data_file(raw, rel, module)
    return out


def split_by_check(violations: list[Violation]) -> tuple[list[Violation], list[Violation]]:
    """(ci/security, ci/policy)."""
    sec = [v for v in violations if v.code.startswith("S")]
    pol = [v for v in violations if v.code.startswith("P")]
    return sec, pol
