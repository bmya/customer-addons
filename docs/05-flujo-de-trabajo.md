# 05 · Flujo de trabajo

```
 rama de trabajo ──PR──▶ revisiones ──▶ runbot ──s+──▶ su test ──revisión BMyA──▶ r+ ──▶ producción
                         automáticas    (tests)        (cuando     (persona)              (ventana
                                                        quieran)                           05:00)
```

## 1. El cambio

- Una rama por cambio, desde `<versión>`: `git switch -c acme-nota-vencimiento 18.0`.
- **Un PR = un commit.** Si tienen varios, júntenlos antes de pedir revisión:
  `git reset --soft origin/18.0 && git commit` y `git push --force-with-lease`.
- Mensaje del commit: `[TAG] modulo: qué cambia`, con un tag de
  `[ADD]` (módulo nuevo), `[IMP]` (mejora), `[FIX]` (corrección), `[REF]`
  (reorganización sin cambio de comportamiento), `[REM]` (se saca algo).
  Ejemplo: `[FIX] acme_note: no permitir notas sin nombre`.
- **Suban la `version` del manifiesto** de cada módulo que cambian.

## 2. El PR

Ábranlo contra `<versión>` (por ejemplo `18.0`). Es el único PR del cambio:
sobre él corren las revisiones, se sube a su test y lo aprueba BMyA. Contra
cualquier otra rama, las revisiones lo rechazan
([P1](03-reglas-de-codigo.md#p1)). La única excepción es la versión siguiente,
para preparar una migración ([7](#7-preparar-una-migración)).

Apenas lo abren, aparecen las revisiones en el PR. **Todas tienen que quedar en
verde** ([06](06-revisiones-automaticas.md)). Cada una tiene un enlace
*Details* con el detalle. Para volver a correrlas: `@robbmya recheck`.

## 3. El runbot

Con cada push al PR se arma un **Odoo efímero** con sus módulos instalados y se
corren los tests. El bot deja un comentario en el PR con la dirección del Odoo
y el usuario y la clave para entrar. Ese Odoo tiene datos de demostración, no
los de su base.

- No tiene salida a internet: si su módulo llama a otro sistema, en el runbot
  la llamada falla. Por eso los tests simulan esas respuestas
  ([04](04-tests-y-cobertura.md)).
- Dura mientras el PR esté abierto y se reemplaza con cada push.

## 4. Su ambiente de test

Con todas las revisiones en verde, cualquier persona con permiso de escritura
en el repositorio puede subir el PR a su ambiente de test, comentando en el PR:

```
@robbmya s+ <cliente>
```

(`<cliente>` es el nombre que les dimos en el alta). El bot lo sube, actualiza
los módulos en su base de test y comenta el resultado en el PR. No hace falta
ninguna otra rama ni otro PR: la combinación que va a su test la arma BMyA por
su lado.

- Pueden tener varios PRs en test a la vez: su test es lo aprobado más todos los
  PRs que mandaron con `s+` y siguen abiertos. El bot marca esos PRs con la
  etiqueta `staging`. Si le sacan la etiqueta a uno, sale del test en la
  próxima subida.
- Si suben un push nuevo al PR, vuelvan a comentar `s+` para que el test tenga
  la última versión.
- Su ambiente de test tiene su propia base, separada de la de producción. Lo
  que prueben ahí no afecta a producción.
- `s+` solo sube a **su** test, y solo desde **su** repositorio.

## 5. Producción

Cuando el cambio esté probado:

1. Pidan la revisión de BMyA desde su panel de cliente (<https://www.bmya.cl/my/customerpanel>, sección «Desarrollo propio»),
   con el botón «Pedir revisión para producción» y el enlace al PR.
2. Revisamos el código y los tests (ver el final de [03](03-reglas-de-codigo.md)).
   Si hay que cambiar algo, lo comentamos en el PR.
3. Si está bien, una persona de BMyA comenta `@robbmya r+`. El bot
   incorpora el PR a `<versión>` (queda como *merged*) y lo programa para la
   **próxima ventana de mantenimiento: de lunes a viernes, a las 05:00 (hora de
   Chile)**. El bot comenta en el PR la hora exacta y, después, el resultado.

El PR tiene que estar al día con `<versión>`: si entró otro cambio mientras
tanto, el bot pide actualizarlo (`git rebase origin/18.0` y
`git push --force-with-lease`) antes de aprobarlo.

**Solo llega a producción lo que se aprueba con `r+`.** Si alguien mergea un PR
a mano o pushea directo a `<versión>`, ese cambio **no se despliega**. Pero su
rama queda distinta de lo que está en producción, y el siguiente `r+` se frena
hasta que lo deshagan (con `git revert`, en un PR). Para que no pase, protejan
la rama ([01](01-puesta-en-marcha.md#4-la-rama)).

## 6. Si algo sale mal en producción

Avísennos desde su panel de cliente (<https://www.bmya.cl/my/customerpanel>, sección «Desarrollo propio»), con «Soporte de mis
módulos». El paso a producción guarda el estado anterior: si la
actualización falla, su Odoo sigue con la versión anterior y el bot lo comenta
en el PR.

## 7. Preparar una migración

Para adelantar el trabajo de pasar sus módulos a la versión siguiente de Odoo
(por ejemplo, de `18.0` a `19.0`):

1. Creen la rama `19.0` desde `18.0`.
2. Trabajen como siempre: una rama por cambio (`19.0-mig-acme_note`) y un PR
   contra `19.0`.
3. Esos PRs pasan por las revisiones automáticas y el runbot de 19.0, así que
   pueden probar sus módulos en un Odoo 19.0 real.
4. `s+` y `r+` **no** aceptan esos PRs mientras su Odoo siga en 18.0. Cuando BMyA
   migre su instalación (por ticket), `19.0` pasa a ser su rama de producción.

Solo se acepta la versión **siguiente**: un cliente en `18.0` no puede abrir PRs
contra `20.0`.

## Comandos

Se comentan en el PR. La mención `@robbmya` es obligatoria.

| Comando | Quién | Qué hace |
|---|---|---|
| `@robbmya recheck` | Con permiso de escritura | Vuelve a correr las revisiones automáticas |
| `@robbmya pr-test` | Con permiso de escritura | Vuelve a correr los tests de los módulos que cambian |
| `@robbmya repo-test` | Con permiso de escritura | Corre los tests de todos los módulos |
| `@robbmya s+ <cliente>` | Con permiso de escritura | Sube el PR a su ambiente de test |
| `@robbmya r+` | Solo BMyA | Aprueba para producción |

## Sin excepciones

Las reglas y las revisiones valen igual para todos los clientes. **Nadie de
BMyA puede saltarlas para un PR**: no existe forma de forzar una revisión en
rojo en un repositorio de cliente. Si una regla les bloquea algo legítimo,
pídanlo por ticket: se evalúa como un cambio de la regla para todos.
