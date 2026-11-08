# 01 · Puesta en marcha

Se hace una sola vez. Al terminar, cada PR de su repositorio pasa solo por las
revisiones de BMyA.

## 1. Crear el repositorio

- **Repositorio nuevo:** en <https://github.com/bmya/customer-addons>, botón
  **«Use this template» → «Create a new repository»**. Marquen
  **«Include all branches»**. Puede ser privado, en su organización de GitHub o
  en una cuenta personal.
- **Repositorio que ya existe:** copien `tools/`, `.pre-commit-config.yaml` y lo
  que falte de `.gitignore`. Los módulos tienen que estar en la **raíz** del
  repositorio, una carpeta por módulo (ver [02](02-estructura-del-repositorio.md)).

## 2. Pedir el alta

Abran un ticket en el portal de BMyA (<https://www.bmya.cl/my/tickets>) con:

- el nombre completo del repositorio: `organizacion/repositorio`
  (o `usuario/repositorio`);
- para qué Odoo es (el nombre de su empresa alcanza: nosotros sabemos qué
  versión usa).

En la respuesta les confirmamos:

- **la versión de Odoo** de su instalación (por ejemplo, `18.0`);
- **el nombre de su cliente** para el comando de pruebas (`@robbmya s+ <cliente>`).

Hasta que el alta esté hecha, las revisiones no corren: un repositorio que BMyA
no dio de alta no recibe nada, aunque tenga la App instalada.

## 3. Instalar la App de BMyA

Instalen la App **app-bot-bmya** en el repositorio, y solo en ese:
<https://github.com/apps/app-bot-bmya> → **Install** → **Only select repositories**.

La App es la que le permite a BMyA ver los PRs, publicar el resultado de las
revisiones y, cuando se aprueba un cambio, incorporarlo a su rama. Solo tiene
acceso al repositorio que ustedes elijan, y pueden quitárselo cuando quieran
desde *Settings → GitHub Apps*. Sin la App no corre ninguna revisión.

BMyA guarda una copia de lo aprobado en un repositorio privado propio, y su
Odoo (también en Odoo.sh) se instala desde esa copia. Así su producción no
depende de que su repositorio siga igual: si lo borran, lo reescriben o le
quitan la App, lo que está instalado se puede reconstruir igual.

## 4. La rama

El repositorio trabaja con **una sola rama**, con el número de su versión de
Odoo (por ejemplo `18.0`). Es lo aprobado, lo que está en producción. Todo PR
va contra esa rama, y sobre ese mismo PR se hacen las pruebas en su test
(`s+`) y la aprobación de BMyA (`r+`). No hay otra rama que crear ni mantener:
su ambiente de test lo arma BMyA por su lado.

El nombre tiene que ser exactamente el de su versión: `main`, `master`,
`produccion` o `18` no sirven, y un PR contra ellas queda en rojo
([P1](03-reglas-de-codigo.md#p1)).

Si crearon el repo desde la plantilla:

1. Dejen la rama de su versión y **borren las otras** (`17.0`, `18.0`, …).
2. Pónganla como rama por defecto: *Settings → General → Default branch*.
3. **Borren la carpeta `acme_note/`** de esa rama, en un commit directo, antes
   de proteger la rama. Es solo un ejemplo: si queda en la rama, se instala en
   su Odoo. Pueden consultarlo cuando quieran en la plantilla.

Si su repositorio ya existía y su rama principal se llama distinto (`main`,
`master`), renómbrenla a la de su versión: *Settings → Branches* o
`git branch -m main 18.0 && git push origin -u 18.0`.

**Protección de la rama (muy recomendado).** En *Settings → Rules → Rulesets*,
una regla para `<versión>` que **restrinja las actualizaciones** (*Restrict
updates*) y deje solo a la App **app-bot-bmya** en *Bypass list*. Así nadie
mergea ni pushea a mano. Un cambio que entra sin `r+` no llega a producción,
pero deja su rama distinta de lo que está instalado, y el siguiente `r+` se
frena hasta que lo deshagan ([05](05-flujo-de-trabajo.md#5-producción)).

## 5. Revisores de BMyA (solo si el repositorio es privado)

Para revisar sus PRs, las personas de BMyA que les indicamos en el ticket tienen
que poder verlos. Invítenlas como colaboradoras con permiso **Read**:
*Settings → Collaborators → Add people*. Con eso pueden leer el código y comentar,
pero no escribir en el repositorio. Si el repositorio es público, no hace falta.

## 6. Desarrolladores

Pueden operar el repositorio (abrir PRs, pedir pruebas, subir a test) todas las
personas con **permiso de escritura** en él. Para sumar o quitar a alguien,
denle o quítenle ese permiso en *Settings → Collaborators*. No hace falta
avisarnos.

La aprobación para producción la da siempre una persona de BMyA.

## 7. Primer PR

1. Instalen la herramienta local y pre-commit: [07](07-trabajar-en-su-maquina.md).
2. Para un módulo nuevo, usen `acme_note/` de la plantilla como molde: cópienlo
   con el nombre de su módulo y reemplacen `acme_note` y `acme.note` en todos
   los archivos.
3. Abran el PR contra `<versión>` y sigan [05](05-flujo-de-trabajo.md).
