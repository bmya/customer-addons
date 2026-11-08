# 04 · Tests y cobertura

Todo módulo tiene tests, y los tests corren en cada PR en un Odoo efímero con
sus módulos instalados (el **runbot**). Para subir a su ambiente de test y para
pasar a producción, tienen que estar en verde:

- **`runbot/tests`**: todos los tests pasan, y se corrió al menos uno.
- **`runbot/coverage`**: cada módulo que el PR toca tiene **70 % de cobertura o
  más**. El número es el mismo para todos los clientes.

## Dónde van

```
acme_note/
└── tests/
    ├── __init__.py          ← from . import test_acme_note
    └── test_acme_note.py
```

Un test que no se importa en `tests/__init__.py` no corre.

## Cómo se escriben

```python
from odoo.exceptions import ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestAcmeNote(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.note = cls.env["acme.note"].create({"name": "Primera"})

    def test_done_closes_the_note(self):
        self.note.action_done()
        self.assertTrue(self.note.done)

    def test_empty_name_is_rejected(self):
        with self.assertRaises(ValidationError):
            self.env["acme.note"].create({"name": "   "})
```

- **`post_install`, `-at_install`:** el test corre con todos los módulos
  instalados, que es como corre su Odoo.
- **Datos en `setUpClass`**, creados con el ORM. No dependan de datos que ya
  estén en una base.
- **Un test por comportamiento**, con un nombre que diga qué se espera.
- **Que el test falle si el código está mal.** Un test que solo llama al método
  sin revisar el resultado no prueba nada, y en la revisión de BMyA se rechaza.
- **Nada de red en los tests.** El runbot no tiene salida a internet. Si su
  módulo llama a otro sistema con `requests`, simulen la respuesta con
  `unittest.mock.patch` en el test. En `tests/` se puede importar `unittest.mock`
  aunque no esté en la lista de [03](03-reglas-de-codigo.md): las reglas de
  imports se aplican igual a los tests, salvo esa excepción.

## La cobertura

La cobertura es la proporción de líneas del módulo que los tests ejecutan. Se
mide sobre los archivos `.py` del módulo, sin contar `tests/` ni
`__manifest__.py`. Si `runbot/coverage` queda debajo de 70 %, el detalle del
check dice qué archivos y líneas no se ejecutaron: agreguen tests que pasen por
ahí.

No se puede bajar con configuración ni con comentarios: un `.coveragerc` hace
fallar `ci/policy` ([P3](03-reglas-de-codigo.md#p3)) y un `# pragma: no cover`,
también ([P2](03-reglas-de-codigo.md#p2)).

## Pedir los tests a mano

Los tests corren solos con cada push al PR. Para volver a correrlos, comenten en
el PR:

| Comando | Qué corre |
|---|---|
| `@robbmya pr-test` | Los tests de los módulos que el PR modifica |
| `@robbmya repo-test` | Los tests de todos los módulos del repositorio |
