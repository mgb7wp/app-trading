# La Lonja

Research de fuentes de datos para un SaaS de análisis bursátil con IA en
🇺🇸 EE. UU., 🇪🇸 España, 🇧🇷 Brasil e 🇮🇳 India, con una restricción que manda
sobre todo lo demás: **coste de fuentes 0 €**, y —mucho más difícil— que esas
fuentes sean **legalmente utilizables en un producto comercial**.

El sitio se publica en **[lalonja-trading.com](https://lalonja-trading.com)**.

```bash
pip install -e ".[dev]"
estrategia sitio          # genera sitio/index.html
```

---

## La respuesta corta

> **¿Se puede construir una aplicación de análisis bursátil para esos cuatro
> mercados usando solo fuentes gratuitas y sin pagar por market data?**
>
> Sí, pero no la aplicación que uno se imagina.

El patrón que explica casi todos los hallazgos:

**El regulador publica porque su mandato es la transparencia. La bolsa vende
porque el market data es su negocio.**

Así que los fundamentales son gratis y son legales —SEC, CNMV, CVM—, y los
precios no lo son en ninguno de los cuatro mercados. B3, BME, NSE y BSE lo
prohíben; Yahoo lo prohíbe; las capas gratuitas de todos los agregadores lo
prohíben. Los índices, igual.

Y eso tiene una consecuencia que conviene leer dos veces: **sin licencia de
precios no hay valoración, ni análisis técnico, ni comparación con benchmark.**
No es una limitación técnica —el código para calcularlo está escrito y probado en
este repositorio— es de licencia.

Queda en pie un analista de fundamentales, gobierno corporativo, flujos,
iniciados, macro, divisas y noticias: **once de las catorce capas** del producto,
a coste cero. Las tres que faltan dependen todas del mismo dato, así que una sola
licencia de unos 20–100 €/mes las enciende las tres, y de paso trae India.

## ⚠️ Nada de esto está verificado

El entorno donde se hizo el research tiene el egreso de red bloqueado por
política:

```
$ curl -sS https://www.sec.gov/os/webmaster-faq
curl: (56) CONNECT tunnel failed, response 403
```

La búsqueda web sí funciona, así que se ha podido **localizar** cada término de
uso y formarse un hallazgo, pero **no leerlo**. Todo va marcado `PROVISIONAL`.

Un `PROVISIONAL` favorable no es permiso para usar una fuente con clientes de
pago. La lista corta de lo que hay que comprobar contra la fuente primaria
—siete páginas web, media jornada— está en
[`docs/data-licensing.md`](docs/data-licensing.md#verificación-obligatoria-antes-de-cobrar).

Esto no es exceso de celo. Durante el research, una búsqueda sobre el copyright
de la SEC devolvió un texto rotundo que prohibía la redistribución de datos de
EDGAR… y resultó venir de los *filings* de una empresa llamada EDGAR Online Inc.,
no de la SEC. Escrito sin comprobar la procedencia, este trabajo habría
descartado su fuente más importante por confundir a una empresa con el regulador.

## Los documentos

| Documento | Qué contiene |
|---|---|
| [`docs/data-sources.md`](docs/data-sources.md) | Ficha por fuente, calidad, riesgos y las nueve respuestas del §33 |
| [`docs/data-matrix.md`](docs/data-matrix.md) | La matriz dato × país, con los huecos marcados como huecos |
| [`docs/data-licensing.md`](docs/data-licensing.md) | Licencia, uso comercial, almacenamiento y redistribución, con enlace oficial |
| [`docs/mvp-data-plan.md`](docs/mvp-data-plan.md) | Qué entra en V1 y cuánto cuesta encender lo que falta |
| [`docs/arquitectura.md`](docs/arquitectura.md) | Modelo canónico, motor de puntuación, calidad de datos, analista IA y screener |
| [`DESPLIEGUE.md`](DESPLIEGUE.md) | Cómo se publica el sitio en Cloudflare |

## El registro de fuentes manda de verdad

`config/fuentes.yaml` no es documentación: es un control que se aplica al
arrancar.

| Estado | Efecto en ejecución |
|---|---|
| `APPROVED` | Se usa en producción |
| `APPROVED_WITH_RESTRICTIONS` | Se usa, y sus condiciones se anotan en cada fila |
| `DEVELOPMENT_ONLY` | Funciona en local. **En producción, el arranque falla** |
| `REJECTED` / `NEEDS_REVIEW` | No se instancia nunca |

`registro.crear()` —por donde pasa toda construcción de una fuente— lo
comprueba antes de construir nada, y hay un test que lo demuestra. Así, «no
depender accidentalmente de una fuente con problemas de licencia» deja de ser una
intención y pasa a ser un arranque que falla.

Dos decisiones que van en contra de lo cómodo, las dos a propósito:

**El entorno por defecto es producción.** Si el defecto fuera `desarrollo`,
olvidar la variable en el despliegue dejaría correr una fuente con problemas de
licencia en silencio. Así, olvidarla en local da un error que se arregla en diez
segundos. Se elige el error barato.

```bash
LALONJA_ENTORNO=desarrollo estrategia ...   # para trabajar en local
```

**Una fuente sin ficha no se instancia.** Dar de alta un adaptador obliga a
escribir su licencia y su enlace. Es la única forma de que el documento y el
código no se separen con el tiempo.

## El sitio

Se genera desde el mismo `config/fuentes.yaml` que el código obedece, así que el
semáforo de la página y lo que el sistema deja usar no pueden separarse.

Una página, sin JavaScript, sin CDN y sin una sola petición externa, en claro y
en oscuro. El workflow comprueba lo segundo antes de publicar.

## Arquitectura

```
src/estrategia/
  datos/
    licencias.py    El registro de fuentes, aplicado al arrancar.
    proveedor.py    Interfaz de fuente y declaración de capacidades.
    registro.py     Nombre → constructor. Aquí se comprueba la licencia.
    enrutador.py    El único punto por el que pasan todos los datos.
    contrato.py     Base del motor de calidad. Rechaza lotes mal formados.
    almacen.py      Vista a fecha de corte, contra el sesgo de anticipación.
  sitio_research.py El sitio, generado desde el registro.
  calendario.py     Sesiones por mercado. Ya cubre los cuatro.
  indicadores.py    Todo el §16, en funciones puras y causales sobre OHLCV.
  fundamental.py    Percentiles de Hazen, trampas de signo, puntuación 0-100.
  diagnostico.py    Qué resuelve cada fuente y qué no, ticker a ticker.
  informe_html.py   Página autocontenida con SVG en línea.
```

El resto —`backtest.py`, `cartera.py`, `ordenes.py`, `riesgo.py`, `salidas.py`,
`seleccion.py`, `validacion.py`— es el motor de la estrategia de trading que era
este repositorio antes. Está escrito y probado, y se conserva: el día que haya un
producto de carteras, ese motor existe. Lo que ya no puede hacer es correr en
producción, porque su fuente de precios era yfinance.

## Tests

```bash
pytest
```

Los que más valen:

- **`test_licencias.py`** — que una fuente `DEVELOPMENT_ONLY` no arranque en
  producción. Si alguien lo pone verde relajando la comprobación en vez de
  arreglando la causa, el registro vuelve a ser documentación.
- **`test_sitio.py`** — que la página no pida nada a nadie, y que el semáforo
  salga del registro y no de una copia a mano.
- **`test_anti_sesgo.py`** — que ninguna decisión mire un día más allá de su
  fecha de corte. Es la condición de entrada de todo lo demás.

Hay un test que afirma el estado honesto del proyecto: **ninguna fuente de
producción está verificada todavía**. Debe fallar el día que se verifiquen, y ese
fallo es la señal de que toca quitarlo.

## Lo que queda fuera de V1

India, por falta de fuente: NSE y BSE prohíben recolectar, y SEBI no publica
datos estructurados. Los estados financieros españoles, porque la CNMV publica
documentos y no campos, y extraerlos es un pipeline propio. Y todo lo que
necesita un precio.

> Esto no es asesoramiento de inversión ni asesoramiento legal. El análisis de
> licencias es una lectura de buena fe hecha por búsqueda web, no por un abogado,
> y está expresamente marcada como no verificada.
