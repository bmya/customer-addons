# 08 · Preguntas frecuentes

**¿Tenemos que darle a BMyA acceso a nuestro repositorio?**
A la App **app-bot-bmya**, solo para ese repositorio: pueden quitársela cuando
quieran. Si el repositorio es privado, además invitan con permiso **Read** a las
personas de BMyA que revisan sus PRs ([01](01-puesta-en-marcha.md)). Nadie de
BMyA necesita permiso de escritura.

**¿Nosotros necesitamos acceso a algo de BMyA?**
No. Ni a servidores, ni a repositorios. Todo pasa por su repositorio y por el
portal de tickets.

**¿Podemos cambiar las revisiones o su configuración?**
No. Las corre BMyA con su configuración, igual para todos los clientes. Un
archivo de configuración de herramientas en su repositorio hace fallar
`ci/policy` ([P3](03-reglas-de-codigo.md#p3)).

**Una revisión quedó en amarillo mucho tiempo.**
Comenten `@robbmya recheck`. Si sigue igual, avísennos por ticket.

**`@robbmya s+` no hizo nada.**
El bot siempre responde. Si no hubo respuesta: revisen que la App siga
instalada en el repositorio y que quien comentó tenga permiso de escritura.
Si dice que faltan revisiones en verde, es que alguna está en rojo o todavía
corriendo.

**Necesitamos una biblioteca de Python que no está en la lista.**
Pídanla por ticket antes del PR. Si se acepta, entra a la lista para todos.

**Necesitamos un módulo de Odoo o de BMyA que nuestro Odoo no tiene.**
Por ticket, antes del PR. Lo agregamos a su instalación y después la
dependencia pasa ([P5](03-reglas-de-codigo.md#p5)).

**Necesitamos SQL para un reporte pesado.**
Usen `read_group` / `_read_group` del ORM, que agrupa en la base. Si no alcanza,
pídanlo por ticket: lo evaluamos como cambio de la regla
([S5](03-reglas-de-codigo.md#s5)).

**¿Por qué no podemos leer archivos del servidor?**
Su código corre en el mismo servidor que el de Odoo y el de BMyA. Los archivos
que su módulo necesita van en `static/` del módulo, o los sube el usuario como
adjuntos.

**¿Quién puede aprobar para producción?**
Solo una persona de BMyA, comentando `@robbmya r+`. El permiso para hacerlo no
depende de su repositorio: aunque alguien de su equipo lo comente, el bot no lo
acepta.

**¿Qué pasa si alguien mergea un PR a mano?**
Ese cambio no se despliega: su Odoo se instala desde la copia de lo aprobado
que guarda BMyA, y ahí solo entra lo que pasó por `r+`. Pero su rama queda
distinta de producción, y el siguiente `r+` se frena hasta que lo deshagan con
un `git revert`. Protejan la rama para que no pueda pasar
([01](01-puesta-en-marcha.md#4-la-rama)).

**¿Necesitamos una rama para el test?**
No. Trabajan siempre contra la rama de su versión, y el mismo PR sirve para
probar (`s+`) y para producción (`r+`). La combinación de PRs que va a su test
la arma BMyA por su lado, sin tocar su repositorio.

**Queremos cambiar de versión de Odoo.**
La migración de su Odoo va por ticket. Mientras tanto, pueden ir preparando
sus módulos en la rama de la versión siguiente, con revisiones y runbot
([05](05-flujo-de-trabajo.md#7-preparar-una-migración)).

**¿El módulo `acme_note` queda en nuestro Odoo?**
Solo si lo dejan en la rama de su versión. Es un ejemplo: bórrenlo al crear el
repositorio ([01](01-puesta-en-marcha.md)).
