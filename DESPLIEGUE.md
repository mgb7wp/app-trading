# Despliegue

Lo que se publica en **lalonja-trading.com** es el sitio del research: fuentes
por país, el semáforo de licencias, la matriz y lo que se puede construir con lo
que hay.

Es contenido propio. No redistribuye datos de terceros, no lleva cotizaciones y
no depende de ninguna clave de proveedor. Por eso se puede publicar hoy, y por
eso este despliegue no tiene ningún riesgo de licencia — que es más de lo que se
puede decir de casi cualquier otra página de análisis bursátil.

```bash
estrategia sitio          # genera sitio/index.html
```

Una página, sin JavaScript, sin CDN y sin una sola petición externa. Se abre
igual desde la CDN, desde el disco o desde un correo.

> **Nada de esto se ha podido probar contra Cloudflare.** El entorno donde se
> desarrolló tiene el egreso de red bloqueado por política: `curl` a
> `cloudflare.com` devuelve `403` desde el proxy, igual que a `sec.gov`. Lo que
> sigue está escrito contra la documentación de Cloudflare, y la primera
> ejecución es la que dirá si algo no encaja.

---

## 1. Crear el proyecto de Pages

`wrangler pages deploy` necesita que el proyecto exista antes. Una sola vez:

```bash
npm install -g wrangler
wrangler login
wrangler pages project create lalonja --production-branch claude/modest-wozniak-6uzjeq
```

O desde el panel: **Workers & Pages → Create → Pages → Direct Upload**, con el
nombre `lalonja`. Si eliges otro nombre, cámbialo también en `--project-name`
dentro de `.github/workflows/publicar.yml`.

## 2. Primer despliegue a mano

```bash
estrategia sitio
wrangler pages deploy sitio --project-name=lalonja
```

Cloudflare devuelve una URL `*.pages.dev`. Ábrela antes de poner el dominio: si
algo se ve mal, es más cómodo arreglarlo ahí.

## 3. El dominio

En **Workers & Pages → lalonja → Custom domains → Set up a custom domain**,
escribe `lalonja-trading.com`. Cloudflare crea el registro DNS solo, porque el
dominio ya está en tu cuenta.

Merece la pena añadir también `www.lalonja-trading.com` y dejar una **regla de
redirección** de `www` al dominio desnudo, para que no haya dos URLs con el
mismo contenido.

## 4. El token para GitHub Actions

En **My Profile → API Tokens → Create Token → Custom token**, con los permisos
mínimos:

| Tipo | Recurso | Permiso |
|---|---|---|
| Account | Cloudflare Pages | Edit |

Nada más. Un token de Pages no necesita tocar DNS, ni Workers, ni zonas.

Y en el repositorio, **Settings → Secrets and variables → Actions**:

| Secreto | De dónde sale |
|---|---|
| `CLOUDFLARE_API_TOKEN` | el token que acabas de crear |
| `CLOUDFLARE_ACCOUNT_ID` | panel de Cloudflare, barra derecha de la vista general |

**No hace falta ninguna clave de proveedor de datos.** El sitio no descarga
nada.

---

## 5. El workflow

`.github/workflows/publicar.yml` se dispara cuando cambia el registro de
fuentes, el generador del sitio o el propio workflow, y también a mano desde
**Actions → Publicar el sitio → Run workflow**. Hace, en este orden:

1. **Tests.** Entre ellos, el que comprueba que una fuente `DEVELOPMENT_ONLY` no
   arranca en producción. Si ese se rompe, el registro de licencias ha dejado de
   mandar y no se publica nada.
2. **Genera el sitio** desde `config/fuentes.yaml`.
3. **Comprueba que la página es autocontenida**: si alguna vez se cuela un
   `<script src>`, una hoja de estilo remota o un `@import`, el despliegue se
   para. Es barato y caza la clase de regresión que nadie mira.
4. **Despliega** a Cloudflare Pages.

### Por qué ya no hay ciclo semanal

Había un workflow que cada lunes descargaba precios de Yahoo, corría el backtest
y publicaba el informe. Ya no existe, y no porque se haya roto: **yfinance está
marcada `DEVELOPMENT_ONLY` en `config/fuentes.yaml`**, así que el arranque en
producción falla a propósito. Sus términos conceden una licencia personal y no
comercial, y eso no vale para un producto de pago aunque el dato no salga nunca
del servidor.

Un workflow programado que se sabe que va a fallar todos los lunes es peor que
no tenerlo. El día que se contrate una licencia de datos de mercado, el ciclo
vuelve — con la fuente en `APPROVED_WITH_RESTRICTIONS` y un nombre distinto.

El razonamiento completo está en
[`docs/data-licensing.md`](docs/data-licensing.md).

---

## 6. Antes de que el sitio tenga clientes

El sitio se puede publicar hoy. **Cobrar por lo que describe, no.**

Todo el análisis de licencias está marcado `PROVISIONAL`: se ha localizado cada
término de uso pero no se ha leído ninguno, porque el entorno donde se hizo el
research no llega a internet. La lista corta de lo que hay que verificar contra
la fuente primaria —siete páginas web, media jornada— está en
[`docs/data-licensing.md`](docs/data-licensing.md#verificación-obligatoria-antes-de-cobrar).

El propio sitio lo dice en su primer bloque, antes que ninguna otra cosa, y lo
repite en el pie con el número exacto de fuentes sin verificar. Eso es
deliberado: un documento que entierra su propia incertidumbre al final es un
documento que la está escondiendo.

---

## 7. Si algún día vuelve el panel

El panel de Streamlit (`panel/app.py`) sigue en el repositorio y sigue
funcionando en local:

```bash
streamlit run panel/app.py
```

Lee resultados ya calculados y no descarga nada, así que en local no toca el
registro de licencias. Exponerlo por **Cloudflare Tunnel** es lo que estaba
montado antes y la plantilla sigue en `despliegue/cloudflared/config.yml`; hoy
no tiene sentido porque los datos que enseñaba salían de una fuente que ya no se
puede usar en producción.
