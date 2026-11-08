#!/usr/bin/env python3
"""Revisa este repositorio con las reglas de BMyA (ci/security y ci/policy).

Uso, desde la raíz del repositorio:

    python3 tools/bmya_check.py                    # todos los módulos
    python3 tools/bmya_check.py acme_note otro     # solo esos módulos
    python3 tools/bmya_check.py --version 18.0     # además, la rama del PR (P1)

Es la misma revisión que corre el CI de BMyA, con el mismo archivo de reglas
(tools/bmya_policy.py). Lo que no puede revisar acá, porque necesita saber qué
tiene su Odoo (P5, P7), lo revisa el CI de BMyA en el PR.

Solo necesita Python 3.8 o más nuevo, sin instalar nada.

Este archivo y bmya_policy.py vienen de https://github.com/bmya/customer-addons.
Para actualizarlos, cópienlos de nuevo desde ahí: no los modifiquen, porque el
CI de BMyA usa siempre su propia copia.
"""
import argparse
import os
import subprocess
import sys


def _current_branch(root):
    try:
        out = subprocess.run(
            ["git", "-C", root, "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True, text=True, check=True,
        )
        return out.stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return None


def main(argv=None):
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import bmya_policy

    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("modules", nargs="*", help="módulos a revisar (por defecto, todos)")
    parser.add_argument("--version", help="su versión de Odoo, ej. 18.0: revisa también la rama base (P1)")
    parser.add_argument("--base", help="rama a la que va a apuntar el PR (por defecto, la de --version)")
    parser.add_argument("--root", default=".", help="raíz del repositorio")
    args = parser.parse_args(argv)

    root = os.path.abspath(args.root)
    if not any(os.path.isfile(os.path.join(root, d, "__manifest__.py")) for d in os.listdir(root)):
        print("No encontré módulos en", root, "— corran el comando desde la raíz del repositorio.")
        return 2

    ctx = bmya_policy.Context(
        odoo_version=args.version,
        base_branch=(args.base or args.version) if args.version else None,
    )
    only = set(args.modules) if args.modules else None
    violations = bmya_policy.check_repository(root, ctx, only_modules=only)
    security, policy = bmya_policy.split_by_check(violations)

    for title, items in (("ci/security", security), ("ci/policy", policy)):
        state = "OK" if not items else f"{len(items)} problema(s)"
        print(f"{title}: {state}")
        for v in items:
            print(f"  {v}")
    print()
    print("Reglas (versión", bmya_policy.POLICY_VERSION + "): docs/03-reglas-de-codigo.md")
    print("P5 y P7 los revisa el CI de BMyA en el PR. Cobertura mínima en el runbot:",
          f"{bmya_policy.COVERAGE_MIN} %.")
    branch = _current_branch(root)
    if args.version and branch and branch not in (args.version,) and not branch.startswith("HEAD"):
        print(f"(Están en la rama {branch}; el PR tiene que apuntar a {args.version}.)")
    return 1 if violations else 0


if __name__ == "__main__":
    sys.exit(main())
