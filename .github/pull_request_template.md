## Qué cambia

<!-- Una o dos frases: qué hace el cambio y por qué. -->

## Cómo probarlo

<!-- Pasos para verlo funcionar en el runbot o en su ambiente de test. -->

## Antes de pedir la revisión de BMyA

- [ ] Un solo commit, con mensaje `[TAG] modulo: qué cambia`
- [ ] Subí la `version` del manifiesto de cada módulo que cambia
- [ ] `python3 tools/bmya_check.py` sin problemas
- [ ] Todas las revisiones del PR en verde, incluidos `runbot/tests` y `runbot/coverage`
- [ ] Probado en nuestro ambiente de test con `@robbmya s+ <cliente>`
