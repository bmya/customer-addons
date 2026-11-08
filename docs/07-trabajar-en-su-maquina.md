# 07 · Trabajar en su máquina

Antes de abrir un PR conviene correr en su máquina las mismas revisiones que
corre BMyA: se ahorran idas y vueltas. Nada de esto reemplaza las revisiones del
PR, que son las que cuentan.

## La herramienta de BMyA: `tools/bmya_check.py`

Revisa las reglas **S** y **P** ([03](03-reglas-de-codigo.md)) con el mismo
archivo de reglas que usa el CI de BMyA. Solo necesita Python 3.8 o más nuevo,
sin instalar nada:

```bash
python3 tools/bmya_check.py                  # todos los módulos
python3 tools/bmya_check.py acme_note        # uno o varios módulos
python3 tools/bmya_check.py --version 18.0   # además, la rama base del PR (P1)
```

Termina con código 0 si no hay problemas, y 1 si encuentra alguno. Cada línea
dice archivo, línea y código de regla:

```
ci/security: 1 problema(s)
  acme_note/models/acme_note.py:3: [S1] import no permitido: import os
ci/policy: OK
```

Lo que no puede revisar en su máquina, porque necesita saber qué tiene su Odoo,
lo revisa el CI de BMyA en el PR: dependencias que su Odoo no tiene
([P5](03-reglas-de-codigo.md#p5)) y nombres de módulo ya usados
([P7](03-reglas-de-codigo.md#p7)).

**Actualizarla:** cuando BMyA publique una versión nueva de las reglas, copien
otra vez `tools/` desde <https://github.com/bmya/customer-addons>. No modifiquen
esos archivos: el CI de BMyA usa siempre su propia copia, así que un cambio
local solo haría que su máquina diga algo distinto que el PR.

## pre-commit: todo junto, antes de cada commit

`.pre-commit-config.yaml` corre la herramienta de BMyA, **isort**, **flake8** y
**oca-checks-odoo-module** con las mismas versiones y opciones que el CI:

```bash
pip install pre-commit          # o: pipx install pre-commit
pre-commit install              # una vez por clon: corre solo en cada commit
pre-commit run --all-files      # a mano, sobre todo el repositorio
```

isort puede corregir el orden de los imports solo: si el commit se frena por
isort, revisen el cambio, agréguenlo (`git add`) y vuelvan a commitear.

## Probar en un Odoo

Los tests oficiales corren en el runbot de cada PR ([05](05-flujo-de-trabajo.md)),
con su versión de Odoo, Enterprise y los módulos de BMyA que tiene su
instalación. No hace falta montar nada en su máquina.

Si quieren probar antes un módulo que solo depende de módulos estándar de Odoo
Community, sirve la imagen oficial de Odoo para su versión. Por ejemplo, con
Docker y Odoo 18:

```bash
docker run -d --name pg -e POSTGRES_USER=odoo -e POSTGRES_PASSWORD=odoo -e POSTGRES_DB=postgres postgres:16
docker run --rm --link pg:db -v "$PWD:/mnt/extra-addons" odoo:18.0 \
    -- -d prueba -i acme_note --test-enable --test-tags /acme_note --stop-after-init
```

`--test-tags /acme_note` corre solo los tests de su módulo (cambien el nombre
por el suyo). Sin ese filtro, Odoo corre también los de `base` y `web`, que
tardan varios minutos y a veces fallan en la imagen oficial por razones ajenas
a su código.

Si el módulo depende de Enterprise o de módulos de BMyA, usen el runbot.
