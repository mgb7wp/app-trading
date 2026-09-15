# Research de fuentes de datos — La Lonja

Fuentes para un SaaS de análisis bursátil en 🇺🇸 EE. UU., 🇪🇸 España, 🇧🇷 Brasil e
🇮🇳 India, con la restricción de que el coste de las fuentes sea **0 €** y —lo que
resulta ser mucho más difícil— que esas fuentes sean **legalmente utilizables en
un producto comercial**.

| | |
|---|---|
| Fecha del research | 15 de septiembre de 2026 |
| Método | Búsqueda web. **Sin lectura de fuente primaria** (ver abajo) |
| Documentos hermanos | [`data-matrix.md`](data-matrix.md) · [`data-licensing.md`](data-licensing.md) · [`mvp-data-plan.md`](mvp-data-plan.md) · [`arquitectura.md`](arquitectura.md) |

---

> ## ⚠️ Estado de verificación: nada está verificado
>
> Ninguna afirmación de licencia de este documento se ha comprobado contra el
> texto oficial. El entorno donde se hizo el research tiene el egreso de red
> bloqueado por política: `curl https://www.sec.gov/…` devuelve `403` desde el
> proxy, y lo mismo pasa con `cnmv.es`, `ecb.europa.eu`, `b3.com.br` y el resto.
> La búsqueda web sí funciona, así que se ha podido **localizar** cada término de
> uso y formarse un hallazgo, pero no **leerlo**.
>
> Cada afirmación va marcada:
>
> | Marca | Qué significa |
> |---|---|
> | `VERIFICADO` | Alguien ha abierto el enlace oficial y leído la cláusula. **Hoy no hay ninguna.** |
> | `PROVISIONAL` | Hallazgo por búsqueda, con el enlace oficial localizado. Nadie ha leído el texto. |
> | `NO LOCALIZADO` | No se ha encontrado el texto que resolvería la pregunta. |
>
> La lista corta de lo que hay que convertir en `VERIFICADO` **antes de cobrarle a
> nadie** está en [`data-licensing.md`](data-licensing.md#verificación-obligatoria-antes-de-cobrar).
>
> Este aviso no es una formalidad. Durante el research, una búsqueda sobre el
> copyright de la SEC devolvió un texto contundente que prohibía la
> redistribución… y resultó que ese texto venía de los *filings* de una empresa
> llamada EDGAR Online Inc., no de la política de la SEC. Un documento escrito
> sin esa distinción habría descartado EDGAR por error.

---

## 1. Resumen ejecutivo

La pregunta del §33 era: *¿podemos construir una aplicación de análisis bursátil
para EE. UU., España, Brasil e India usando únicamente fuentes gratuitas y sin
pagar por market data durante el MVP?*

**Sí, pero no la aplicación que uno se imagina por defecto.**

El research se parte en dos mitades que no se comportan igual, y la línea que las
separa no es técnica sino de modelo de negocio:

> **El regulador publica porque su mandato es la transparencia.
> La bolsa vende porque el market data es su negocio.**

Esa frase predice casi todos los hallazgos.

### Lo que sí se puede

**Los fundamentales son gratis y son legales**, y salen del regulador, no de la
bolsa:

| | Regulador | Qué publica en abierto | Estado |
|---|---|---|---|
| 🇺🇸 | **SEC EDGAR** | XBRL completo, filings, insiders (Forms 3/4/5) | Tier 1 |
| 🇪🇸 | **CNMV** | Información periódica, hechos relevantes, cortos, directivos | Tier 2 |
| 🇧🇷 | **CVM** | DFP, ITR, FRE, VLMO (insiders) | Tier 1 |
| 🇮🇳 | **SEBI** | Nada estructurado. El dato vive en NSE/BSE | ❌ hueco |

Y son gratis también la macro (BCE, Banco Mundial, FRED con cuidado), las divisas
(BCE), las noticias (GDELT) y el short interest de EE. UU. (FINRA) y España
(CNMV).

### Lo que no se puede

**Los precios no son gratis en ningún sitio.** No es un problema de encontrar la
API adecuada: es que las cuatro bolsas y todos los agregadores gratuitos dicen lo
mismo con palabras distintas.

| Fuente | Qué dice | `PROVISIONAL` |
|---|---|---|
| **B3** 🇧🇷 | El usuario final no puede distribuir, retransmitir, reformatear ni publicar market data | [términos](https://www.b3.com.br/pt_br/termos-de-uso-e-protecao-de-dados/termos-de-uso/) |
| **NSE** 🇮🇳 | Prohibida la recolección sistemática o automatizada sin consentimiento escrito | [términos](https://www.nseindia.com/static/nse-terms-of-use) |
| **BSE** 🇮🇳 | Uso personal, no comercial o educativo | [términos](https://www.bseindia.com/static/about/website_policy.html) |
| **BME** 🇪🇸 | Uso interno exclusivamente; lo demás exige autorización expresa | [web](https://www.bolsasymercados.es/) |
| **Yahoo** 🌍 | «You must not redistribute information displayed on or provided by Yahoo Finance» | [términos](https://guce.yahoo.com/terms) |
| Alpha Vantage, Tiingo, Finnhub, EODHD, Marketstack | Capa gratuita = licencia no comercial | ver [`data-licensing.md`](data-licensing.md) |

Y lo mismo, en bloque, con los **índices**: S&P Dow Jones Indices prohíbe
expresamente la reproducción sin permiso escrito, y IBEX 35, Ibovespa, NIFTY 50 y
SENSEX son productos licenciados de sus respectivas bolsas. Los benchmarks tienen
exactamente el mismo problema que los precios.

### La consecuencia dura, que conviene leer dos veces

**Sin licencia de precios no hay capa de valoración y no hay capa técnica.**

No es un matiz. Se cae, entero:

- capitalización bursátil, PER, PER adelantado, P/S, P/B, EV/EBITDA, EV/Sales, FCF yield;
- SMA, EMA, RSI, MACD, estocástico, Bollinger, ATR, OBV, volatilidad histórica, beta;
- rendimiento relativo contra índice, alfa, máximo drawdown;
- y la mitad de las preguntas del §25 («¿está cara respecto a su histórico?»).

Queda en pie, y es más de lo que parece: crecimiento, márgenes, ROE/ROA/ROIC,
estructura de balance, cobertura de intereses, flujo de caja, actividad de
iniciados, posiciones cortas, hechos relevantes, gobierno corporativo, contexto
macro, divisas y noticias.

### Un matiz que hay que decir bien, porque es fácil equivocarse

Durante el research apareció una idea atractiva: *si los precios son una entrada
interna y no una salida —si publicamos el score y no la serie OHLCV— quizá no
necesitemos licencia*.

**Eso es medio cierto y medio falso, y la mitad falsa es la peligrosa.**

Es falso para Yahoo: sus términos conceden una licencia *personal, no
transferible y no comercial*. Usar sus datos dentro de un producto de pago
incumple esos términos aunque el dato nunca salga del servidor. La distinción
entrada/salida no salva a Yahoo.

Es cierto para el **precio de la licencia**. Una licencia de *uso derivado sin
redistribución* cuesta decenas de euros al mes; una de *redistribución* cuesta
miles y exige contrato con cada bolsa. Que el producto no publique la serie no
elimina la necesidad de licencia: la abarata uno o dos órdenes de magnitud.

### La recomendación

**Lanzar V1 sin precios.** Un analista de fundamentales, gobierno corporativo,
flujos e iniciados, con contexto macro y de noticias, para EE. UU., España y
Brasil. Coste de fuentes: 0 €. Riesgo de licencia: bajo y documentado. Es un
producto real y, de hecho, es el segmento que peor cubren los agregadores
gratuitos, que van todos sobrados de precios y cortos de filings.

Y dejar la capa de precios **construida pero apagada**, detrás del registro de
fuentes, de modo que el día que se firmen 20–60 €/mes de licencia EOD se encienda
con un cambio de configuración. El detalle, en
[`mvp-data-plan.md`](mvp-data-plan.md).

India se queda fuera de V1. No por falta de ganas: por falta de fuente. Es el
único de los cuatro mercados donde ni siquiera los fundamentales tienen un camino
limpio.

---

## 2. Arquitectura de datos

La cadena que pide el §1, con la anotación de dónde está cada control:

```
FUENTES EXTERNAS
      │        ← registro de fuentes: si el estado no es apto, no se instancia
      ▼
DATA INGESTION          /connectors/{sec,cnmv,cvm,fred,ecb,worldbank,gdelt,ir}
      │        ← un conector por fuente, sustituible, sin lógica de producto
      ▼
RAW DATA                se guarda el original tal cual llegó, con su hash
      │        ← nunca se descarta: si el parseo cambia, se re-parsea sin re-descargar
      ▼
NORMALIZATION           unidades, divisa, signo, periodo fiscal, identificadores
      │        ← motor de calidad: aquí se rechaza, no más abajo
      ▼
CANONICAL DATA MODEL    §21 — el mismo modelo para los cuatro mercados
      │        ← toda fila lleva fuente, url, retrieved_at, published_at, confianza
      ▼
DATABASE
      │
      ▼
ANALYTICS ENGINE        ratios y técnicos calculados en casa, nunca comprados
      │
      ▼
SCORING ENGINE          determinista, reproducible, versionado
      │        ← la IA no entra aquí
      ▼
AI ANALYST              interpreta el contexto estructurado. No inventa.
      │        ← si falta un dato: «No disponemos de este dato.»
      ▼
FRONTEND / API
```

Tres decisiones de diseño que vienen del research y no de la teoría:

**El registro de fuentes se aplica en ejecución, no es documentación.**
`config/fuentes.yaml` guarda el estado de cada fuente (`APPROVED`,
`APPROVED_WITH_RESTRICTIONS`, `DEVELOPMENT_ONLY`, `REJECTED`, `NEEDS_REVIEW`) y
el enrutador —el único sitio por el que pasan todos los datos— se niega a
instanciar una fuente `DEVELOPMENT_ONLY` cuando el entorno es de producción. Así
«no depender accidentalmente de una fuente con problemas de licencia» deja de ser
una intención y pasa a ser un arranque que falla. El día que la verificación
primaria cambie un estado, el efecto es inmediato.

**La capa de precios es opcional por diseño.** No es un parche para el problema de
licencia: es lo que permite que el producto exista hoy a 0 € y crezca sin
reescribirse. Cada métrica declara de qué capas depende; si la capa de precios
está apagada, la ficha de empresa muestra lo que puede y dice honestamente qué
falta y por qué.

**Se guarda el bruto.** El coste de almacenar el XBRL original es despreciable
comparado con el de volver a descargar cuatro años de filings porque el mapeo de
un campo estaba mal. Y es la única forma de auditar un número raro.

---

## 3. Fuentes por país

### 🇺🇸 Estados Unidos

#### SEC EDGAR

```
SOURCE:                    SEC EDGAR
COUNTRY:                   Estados Unidos
DATA TYPE:                 Estados financieros, filings, iniciados, metadatos
OFFICIAL / THIRD PARTY:    Oficial (regulador federal)
URL:                       https://www.sec.gov/search-filings
API:                       https://data.sec.gov  —  submissions, companyconcept,
                           companyfacts, frames. Full-text search aparte.
API KEY:                   No
FREE:                      Sí                                      PROVISIONAL
COMMERCIAL USE:            Sin restricción localizada               PROVISIONAL
STORAGE:                   Sin restricción localizada               PROVISIONAL
REDISTRIBUTION:            Sin restricción localizada               PROVISIONAL
RATE LIMIT:                10 req/s agregadas por IP. User-agent
                           declarado obligatorio. Prohibidos
                           botnets y crawlers indiscriminados.      PROVISIONAL
HISTORICAL DATA:           XBRL desde ~2009. Filings desde 1993/1996.
UPDATE FREQUENCY:          Continua (filings). Insider Transactions
                           Data Sets: trimestral.
LICENSE:                   No localizada como tal. 17 U.S.C. §105
                           excluye del copyright las obras del
                           gobierno federal de EE. UU., pero los
                           filings los redacta la empresa, no la SEC. NO LOCALIZADO
TERMS:                     https://www.sec.gov/about/webmaster-frequently-asked-questions
                           https://www.sec.gov/search-filings/edgar-search-assistance/accessing-edgar-data
RELIABILITY:               Muy alta. Es la referencia del sector.
IMPLEMENTATION DIFFICULTY: Media. El XBRL es prolijo y las etiquetas
                           varían entre empresas; hace falta un mapeo
                           por concepto con alternativas.
RECOMMENDATION:            ⭐ Tier 1. La fuente ancla del producto.
```

**Qué se saca, campo a campo.** `companyfacts` devuelve todos los conceptos XBRL
declarados por una empresa con su valor, periodo, unidad y —esto es lo que
importa— la `accn` del filing y su `filed` (fecha de presentación). Eso cubre:

| Bloque | Conceptos US-GAAP habituales |
|---|---|
| Cuenta de resultados | `Revenues` / `RevenueFromContractWithCustomerExcludingAssessedTax`, `GrossProfit`, `OperatingIncomeLoss`, `NetIncomeLoss`, `EarningsPerShareBasic` / `Diluted` |
| Balance | `CashAndCashEquivalentsAtCarryingValue`, `Assets`, `Liabilities`, `StockholdersEquity`, `LongTermDebtNoncurrent` + `DebtCurrent` |
| Flujo de caja | `NetCashProvidedByUsedInOperatingActivities`, `PaymentsToAcquirePropertyPlantAndEquipment` |
| Acciones | `CommonStockSharesOutstanding`, `WeightedAverageNumberOfDilutedSharesOutstanding`, y `dei:EntityCommonStockSharesOutstanding` en la portada |

*FCF no viene: se calcula* (`OCF − capex`). Es exactamente la clase de métrica que
el §17 pide no comprar.

**El detalle que hace que esto funcione y que casi nadie aprovecha:** cada hecho
XBRL trae su fecha de presentación. Eso significa que EDGAR permite construir una
base **point-in-time de verdad** —saber qué se sabía y cuándo— en lugar de la
reconstrucción con retraso fijo que hacen los agregadores. Es una ventaja
competitiva real y es gratis.

**Formularios y qué aporta cada uno:**

| Formulario | Quién | Qué da |
|---|---|---|
| 10-K / 10-Q | Emisor nacional | Estados financieros anuales/trimestrales, XBRL |
| 8-K | Emisor nacional | Hechos relevantes, con *items* codificados (2.02 resultados, 5.02 ceses…) |
| 20-F / 6-K | Emisor extranjero (ADR) | Anual / eventual. **20-F es anual, no trimestral**: las empresas extranjeras cotizadas en EE. UU. no tienen granularidad trimestral garantizada |
| 3 / 4 / 5 | Iniciados (Sección 16) | Alta, cambios y anuales de participación de directivos y >10% |
| SC 13D / 13G | Accionistas >5% | Participaciones significativas |
| DEF 14A | Emisor | Retribución, gobierno, propuestas |

Los **Insider Transactions Data Sets** ya vienen aplanados desde el XML de los
Forms 3/4/5, con actualización trimestral; para reciente hay que ir a los propios
formularios.
[readme](https://www.sec.gov/files/insider_transactions_readme.pdf)

**Identificadores.** `company_tickers.json` da CIK ↔ ticker ↔ exchange y es el
punto de entrada. **ISIN no lo publica la SEC**: no hay camino gratuito y limpio
de CIK a ISIN en EE. UU. (el CUSIP es un producto licenciado). El modelo canónico
debe tratar ISIN como opcional, no como clave. Ver
[`arquitectura.md`](arquitectura.md#identificadores).

**Riesgo principal:** la volatilidad de las etiquetas XBRL. Dos empresas del mismo
sector pueden declarar ingresos con conceptos distintos, y la misma empresa puede
cambiarlo entre ejercicios. Se resuelve con una tabla de conceptos con
alternativas ordenadas y una alarma cuando ninguna casa —que es justo el tipo de
fallo silencioso que ya mordió a este repositorio una vez (ver
[`FUENTES.md`](../FUENTES.md#el-contrato)).

#### FINRA — short interest

```
SOURCE:                    FINRA Equity Short Interest
COUNTRY:                   Estados Unidos
DATA TYPE:                 Posiciones cortas agregadas
OFFICIAL / THIRD PARTY:    Oficial (SRO supervisada por la SEC)
URL:                       https://www.finra.org/finra-data/browse-catalog/equity-short-interest
API:                       Descarga documentada (CSV/JSON y ficheros con |)
API KEY:                   No localizado                            NO LOCALIZADO
FREE:                      Sí, «free for the broader investing public»  PROVISIONAL
COMMERCIAL USE:            No localizado                            NO LOCALIZADO
STORAGE / REDISTRIBUTION:  No localizado                            NO LOCALIZADO
RATE LIMIT:                No localizado                            NO LOCALIZADO
HISTORICAL DATA:           5 años en la rejilla interactiva; archivo histórico
                           descargable por separado
UPDATE FREQUENCY:          Bimensual (Regla 4560, dos veces al mes)
TERMS:                     https://www.finra.org/finra-data/browse-catalog/equity-short-interest
RELIABILITY:               Alta. Es el dato regulatorio, no una estimación.
IMPLEMENTATION DIFFICULTY: Baja.
RECOMMENDATION:            Tier 2 — cubre el hueco de cortos en EE. UU., pero
                           los términos de FINRA Data no están localizados y
                           hay que leerlos.
```

---

### 🇪🇸 España

#### CNMV

```
SOURCE:                    CNMV
COUNTRY:                   España
DATA TYPE:                 Información periódica, hechos relevantes, cortos,
                           participaciones significativas, autocartera,
                           notificaciones de directivos, gobierno corporativo
OFFICIAL / THIRD PARTY:    Oficial (regulador)
URL:                       https://www.cnmv.es
API:                       Parcial. Ficheros ZIP con XML para información
                           privilegiada y otra información relevante, con marca
                           de tiempo y esquema. Consultas web para el resto.
                           Datasets también en https://datos.gob.es
API KEY:                   No
FREE:                      Sí                                       PROVISIONAL
COMMERCIAL USE:            Ley 37/2007 de reutilización de la información del
                           sector público contempla **expresamente** la
                           reutilización con fines comerciales y manda fomentar
                           licencias abiertas con mínimas restricciones.
                           Directiva (UE) 2019/1024 en la misma línea.  PROVISIONAL
STORAGE:                   Previsible sí, por lo anterior             NO LOCALIZADO
REDISTRIBUTION:            Previsible sí, con atribución              NO LOCALIZADO
RATE LIMIT:                No publicado                               NO LOCALIZADO
HISTORICAL DATA:           Registros oficiales con profundidad larga, variable
                           por tipo de registro
UPDATE FREQUENCY:          Continua para hechos relevantes. Semestral/anual
                           para información periódica. Diaria para cortos.
LICENSE:                   Nota legal de la CNMV: https://cnmv.es/portal/utilidades/notalegal.aspx
                                                                      NO LOCALIZADO
TERMS:                     https://www.cnmv.es/portal/quees/proteccion-datos-otros
RELIABILITY:               Alta.
IMPLEMENTATION DIFFICULTY: **Alta.** Es el conector más caro de los tres
                           reguladores utilizables.
RECOMMENDATION:            Tier 2. Imprescindible para España, pero hay que
                           leer la nota legal antes de construir encima.
```

**Por qué es el conector caro.** La CNMV no tiene un `companyfacts`. Tiene
registros oficiales consultables, ficheros ZIP/XML para comunicaciones, y un
formato de información pública periódica (IPP) que llega como documento, no como
XBRL etiquetado campo a campo. Extraer una cuenta de resultados comparable entre
emisores españoles exige un pipeline de extracción sobre documentos, no un
mapeo de conceptos. Es donde más trabajo hay y donde más fácil es colar un error.

La consecuencia práctica está en [`mvp-data-plan.md`](mvp-data-plan.md): España
entra en V1 con **hechos relevantes, cortos, participaciones significativas y
notificaciones de directivos** —que son estructurados y baratos— y los estados
financieros llegan en una segunda pasada, apoyados en el Investor Relations de
cada emisor.

**Lo que se obtiene, por bloque del §3:**

| Pedido | Dónde está | Formato | Dificultad |
|---|---|---|---|
| Emisores | Registros oficiales | Consulta web | Media |
| Información financiera anual / intermedia | IPP | Documento | **Alta** |
| Hechos relevantes | «Información privilegiada» y «Otra información relevante» (MAR partió el antiguo «hecho relevante» en dos) | ZIP + XML | Baja |
| Participaciones significativas | Consulta por emisor | Web | Media |
| Autocartera | Consulta por emisor | Web | Media |
| Posiciones cortas | [Consulta por NIF](https://www.cnmv.es/portal/consultas/busqueda?id=29) | Web / descarga | Baja |
| Gobierno corporativo | IAGC | Documento | Alta |
| Dividendos, ampliaciones, splits | Se comunican como información relevante | XML + texto | Media (hay que clasificar) |
| Administradores y directivos | [Notificaciones de directivos](https://www.cnmv.es/portal/Consultas/Notificacion-Directivos) (MAR art. 19) | Web | Media |

Nota sobre esa última fila: es el equivalente español del Form 4, y **existe**.
Lo que no se ha localizado es un mecanismo de descarga masiva; hoy es una consulta
por emisor. Hay una Circular en consulta pública que renueva los modelos de
notificación y deroga la Circular 2/2007, así que el formato puede cambiar.

#### BME

```
SOURCE:                    BME (Bolsas y Mercados Españoles, grupo SIX)
COUNTRY:                   España
DATA TYPE:                 Cotizaciones, índices, IBEX 35, composición,
                           corporate actions
OFFICIAL / THIRD PARTY:    Oficial (mercado)
URL:                       https://www.bolsasymercados.es/
FREE:                      Consulta web sí; uso más allá, no          PROVISIONAL
COMMERCIAL USE:            ❌ «uso interno exclusivamente». Cualquier otro uso
                           comercial o redistribución a terceros exige
                           autorización previa expresa de BME Market Data
                           (marketdata@grupobme.es)                    PROVISIONAL
STORAGE / REDISTRIBUTION:  ❌                                          PROVISIONAL
RECOMMENDATION:            ❌ **Tier 4 — NO APTA PARA PRODUCCIÓN COMERCIAL**
```

El IBEX 35 es producto de BME/SIX. No hay camino gratuito al benchmark español.

---

### 🇧🇷 Brasil

#### CVM — Portal de Dados Abertos

```
SOURCE:                    CVM (Comissão de Valores Mobiliários)
COUNTRY:                   Brasil
DATA TYPE:                 Estados financieros, formulario de referencia,
                           iniciados, hechos relevantes
OFFICIAL / THIRD PARTY:    Oficial (regulador)
URL:                       https://dados.cvm.gov.br/
API:                       Portal CKAN. Ficheros CSV/ZIP por dataset y ejercicio.
                           Integrado con el Portal Brasileiro de Dados Abertos.
API KEY:                   No
FREE:                      Sí                                         PROVISIONAL
COMMERCIAL USE:            Repositorio de datos públicos bajo la Lei de Acesso
                           à Informação y la Política de Dados Abertos del
                           Poder Executivo Federal, con «livre acesso a dados
                           públicos de forma não discriminatória»       PROVISIONAL
STORAGE:                   Previsible sí                               NO LOCALIZADO
REDISTRIBUTION:            ⚠️ **La licencia es por dataset, no global.** Los
                           términos dicen que el usuario debe comprobar «no
                           metadado de cada conjunto de dados as licenças sobre
                           condições adicionais», que además pueden cambiar.  PROVISIONAL
RATE LIMIT:                No publicado                                NO LOCALIZADO
HISTORICAL DATA:           DFP e ITR por ejercicio, profundidad larga
UPDATE FREQUENCY:          Semanal (DFP e ITR)
LICENSE:                   Por dataset                                 NO LOCALIZADO
TERMS:                     https://dados.cvm.gov.br/about
RELIABILITY:               Alta.
IMPLEMENTATION DIFFICULTY: Media-baja. CSV plano, pero con un esquema que hay
                           que aprender y nombres de cuenta en portugués.
RECOMMENDATION:            ⭐ Tier 1 con una salvedad: hay que comprobar la
                           licencia **dataset a dataset**, no una vez.
```

**Los datasets que importan:**

| Dataset | Qué es | Equivalente |
|---|---|---|
| `cia_aberta-doc-dfp` | Demonstrações Financeiras Padronizadas (anual) | 10-K |
| `cia_aberta-doc-itr` | Informações Trimestrais | 10-Q |
| `cia_aberta-doc-fre` | Formulário de Referência | 10-K + DEF 14A |
| `cia_aberta-doc-vlmo` | **Valores Mobiliários Negociados e Detidos** | **Form 4** |
| `cia_aberta-doc-fca` | Formulário Cadastral | metadatos de la compañía |

`vlmo` es el hallazgo del research en Brasil: la negociación de administradores y
personas vinculadas (Resolución CVM 44 art. 11, antes ICVM 358) está publicada en
abierto por el regulador, no por la bolsa. Brasil tiene insiders gratis y legales.

Base normativa de DFP/ITR: Resolución CVM nº 80/22, arts. 22 IV y 31. Y la CVM ha
publicado su Plan de Datos Abiertos 2026-2028, lo que sugiere continuidad.

#### B3

```
SOURCE:                    B3
COUNTRY:                   Brasil
DATA TYPE:                 Market data, índices, Ibovespa, empresas listadas
OFFICIAL / THIRD PARTY:    Oficial (mercado)
URL:                       https://www.b3.com.br
COMMERCIAL USE:            ❌ El usuario final no puede distribuir, redistribuir,
                           transferir, transmitir, retransmitir, licenciar,
                           sublicenciar, arrendar, vender, revender, recircular,
                           **reformatear ni publicar** market data.      PROVISIONAL
STORAGE / REDISTRIBUTION:  ❌ La licencia de distribuidor exige contrato firmado
                           con B3.                                       PROVISIONAL
NOTA:                      Política Comercial de Market Data **nueva desde el
                           01/01/2026**. Cualquier lectura anterior a esa fecha
                           está caducada.
TERMS:                     https://www.b3.com.br/pt_br/termos-de-uso-e-protecao-de-dados/termos-de-uso/
RECOMMENDATION:            ❌ **Tier 4 — NO APTA PARA PRODUCCIÓN COMERCIAL**
```

El §4 pedía investigar el Public Data Hub de B3 (FinancialData, OutstandingShares,
PositionOfShareholders, SummaryData). El hallazgo importante es de arquitectura,
no de endpoint: **casi todo lo que ese hub ofrece de fundamentales también lo
publica la CVM, y la CVM no lo prohíbe.** No hay razón de producto para depender
de B3. La separación *public data / licensed market data* que pedía el §4 se
resuelve por la vía más limpia posible: no tocar B3.

---

### 🇮🇳 India

India es el mercado que no sale.

#### SEBI

```
SOURCE:                    SEBI
COUNTRY:                   India
DATA TYPE:                 Filings (DRHP, RHP, SAST, buybacks, órdenes)
URL:                       https://www.sebi.gov.in/filings.html
API:                       ❌ **No se ha localizado ningún portal de datos
                           abiertos estructurado** equivalente a EDGAR o
                           dados.cvm.gov.br                              PROVISIONAL
RECOMMENDATION:            Tier 3 — útil para documentos, inútil para series
```

El regulador indio publica documentos, no datasets. Y el dato estructurado que
existe —divulgaciones PIT 2015 y SAST 2011, *shareholding patterns*, resultados—
se publica **en las webs de NSE y BSE**, cuyos términos son los que son. El
sistema de *system-driven disclosures*, alimentado por los depositarios NSDL y
CDSL, desemboca igualmente en las bolsas.

Es decir: en India, el dato del regulador se distribuye por un canal que prohíbe
recolectarlo automáticamente. Eso no es un obstáculo técnico que se resuelva con
un conector mejor; es una vía cerrada.

#### NSE y BSE

```
NSE  — https://www.nseindia.com/static/nse-terms-of-use
       ❌ Prohibida toda recolección sistemática o automatizada (scraping, data
       mining, data extraction, data harvesting) sin consentimiento escrito
       expreso. Market data comercial: vía NSE Data, a precio aprobado por su
       Consejo. Advierte de acciones legales.                            PROVISIONAL

BSE  — https://www.bseindia.com/static/about/website_policy.html
       ❌ «personal, non-commercial or educational purposes», con atribución
       completa. Productos comerciales de market data, de pago; distribución
       internacional vía Deutsche Börse desde 2013.                      PROVISIONAL
       Jurisdicción: leyes de India, tribunales de Bombay.

AMBAS: ❌ Tier 4 — NO APTAS PARA PRODUCCIÓN COMERCIAL
```

**Recomendación para India:** dejarla fuera de V1 y entrar más tarde por una de
estas tres puertas, en este orden de preferencia:

1. Una licencia comercial de un agregador que ya tenga cerrado el acuerdo con NSE
   (es lo que se compra cuando se compra EODHD o similar con cobertura india).
2. Investor Relations de las ~50 empresas del NIFTY, una a una. Legal, laborioso,
   sin cortos ni insiders.
3. Consentimiento escrito de NSE. Es lo que sus términos contemplan
   explícitamente; nadie ha comprobado si se concede ni a qué precio.

---

## 4. Fuentes globales

### Divisas — BCE ⭐

```
SOURCE:                    Banco Central Europeo — tipos de cambio de referencia
COUNTRY:                   Global (base EUR)
DATA TYPE:                 FX diario
OFFICIAL / THIRD PARTY:    Oficial (banco central)
URL:                       https://data.ecb.europa.eu/
API:                       SDMX RESTful + fichero eurofxref (CSV/XML)
API KEY:                   No
FREE:                      Sí                                          PROVISIONAL
COMMERCIAL USE:            ✅ «All publicly available ESCB statistics may be
                           reused **free of charge** on the condition that the
                           source is quoted» y no se modifiquen (metadatos
                           incluidos). Reutilización comercial libre.     PROVISIONAL
STORAGE:                   ✅                                           PROVISIONAL
REDISTRIBUTION:            ✅ con cita de la fuente y sin modificar       PROVISIONAL
RATE LIMIT:                No publicado                                 NO LOCALIZADO
HISTORICAL DATA:           Desde 1999 para las divisas principales
UPDATE FREQUENCY:          Diaria, ~16:00 CET en días hábiles TARGET. 29 divisas.
LICENSE:                   Condiciones del aviso legal del BCE
TERMS:                     https://www.ecb.europa.eu/services/using-our-site/disclaimer/html/index.en.html
RELIABILITY:               Máxima.
IMPLEMENTATION DIFFICULTY: Baja.
RECOMMENDATION:            ⭐ Tier 1. La base de toda la capa de divisas.
```

**BRL e INR están entre las 29 divisas**, así que EUR/USD, EUR/BRL y EUR/INR
salen directos, y USD/BRL y USD/INR por cruce a través del euro. Cubre el §8
entero con una sola fuente.

Dos cautelas que hay que codificar, no recordar:

- **Es un tipo de referencia, no un tipo de mercado.** Es una foto de las 16:00
  CET. Sirve para comparar rendimientos, no para valorar una operación.
- **El calendario es TARGET, no el de cada bolsa.** Un día hábil en Bombay puede
  no tener tipo publicado. La regla debe ser explícita —último tipo disponible,
  nunca interpolar hacia adelante— y estar probada.

El §8 pide poder explicar que una acción brasileña sube un 15 % en BRL y un 7 %
en EUR. Eso con el BCE se hace y se hace bien. Es, además, una de las pocas cosas
del producto que **no depende de la capa de precios de acciones**: el efecto
divisa sobre un rendimiento ya conocido se calcula con FX solo.

### Macro — Banco Mundial ⭐

```
SOURCE:                    Banco Mundial — World Development Indicators
DATA TYPE:                 PIB, crecimiento, inflación, paro, deuda, población,
                           comercio; y Pink Sheet de materias primas
URL:                       https://data.worldbank.org
API:                       https://api.worldbank.org/v2/ (REST, JSON/XML)
API KEY:                   No
FREE:                      Sí                                          PROVISIONAL
COMMERCIAL USE:            ✅ **CC BY 4.0** + términos adicionales: copiar,
                           modificar y distribuir para cualquier fin,
                           incluido comercial                            PROVISIONAL
STORAGE / REDISTRIBUTION:  ✅ con atribución                            PROVISIONAL
ATTRIBUTION:               Formato exigido: `The World Bank: Dataset name: Data
                           source`. Obligación de **propagar** la atribución a
                           sublicenciatarios.                            PROVISIONAL
⚠️ TRAMPA:                 Datasets de terceros dentro del catálogo pueden NO
                           ser redistribuibles. Hay que comprobar por dataset.
HISTORICAL DATA:           Desde 1960 en muchas series
UPDATE FREQUENCY:          Anual la mayoría; trimestral algunas; mensual el
                           Pink Sheet
TERMS:                     https://datacatalog.worldbank.org/public-licenses
                           https://www.worldbank.org/en/about/legal/terms-of-use-for-datasets
RECOMMENDATION:            ⭐ Tier 1 con atribución obligatoria.
```

Cubre los cuatro países con el mismo esquema, que es exactamente lo que necesita
un Macro Score comparable entre mercados. Y el **Pink Sheet** resuelve materias
primas (§15) con Brent, cobre LME y oro, en Excel y PDF, **mensual**.
[commodity markets](https://www.worldbank.org/en/research/commodity-markets)

Mensual no es diario. Para contexto sectorial sobra; para una serie diaria de
Brent no llega. Es una limitación real del MVP y así consta.

### Macro — FRED

```
SOURCE:                    FRED (Federal Reserve Bank of St. Louis)
API KEY:                   Sí, gratuita
FREE:                      Sí. FRED no cobra ni contabiliza consumo.     PROVISIONAL
COMMERCIAL USE:            ⚠️ **Depende de la serie.** Redistribuir comercialmente
                           series con copyright NO está permitido sin
                           autorización del titular del copyright.        PROVISIONAL
TERMS:                     https://fred.stlouisfed.org/docs/api/terms_of_use.html
                           https://fred.stlouisfed.org/legal
RECOMMENDATION:            Tier 2 — APPROVED_WITH_RESTRICTIONS.
```

**La trampa que el §7 pedía documentar, y es real:** FRED no es una fuente, es un
agregador. Las series propias de la Reserva Federal y de las agencias federales
(tipos, monetarios, empleo del BLS) no tienen el mismo régimen que las series
licenciadas de terceros (S&P/Case-Shiller, NAHB, ICE, Haver…). La obligación es
comprobar **la nota de fuente de cada serie**, una por una, antes de usarla.

Implicación de ingeniería: el conector de FRED debe llevar una **lista blanca de
`series_id` aprobados**, no permitir una serie arbitraria. Es el único diseño que
convierte esa regla en algo que se cumple solo.

### Macro — FMI ⚠️

```
SOURCE:                    Fondo Monetario Internacional
API:                       SDMX 3.0 — https://api.imf.org/external/sdmx/3.0
                           Datasets: IFS, WEO, FM, GFS, MFS, BOP
TERMS:                     https://www.imf.org/en/about/copyright-and-terms
COMMERCIAL USE:            ⚠️ **CONTRADICTORIO.** La regla general prohíbe el uso
                           comercial: descarga no sistemática, uso personal no
                           comercial, sin reventa ni redistribución.
                           Pero hay «special terms» para los datos estadísticos
                           publicados que permiten descargar, extraer, copiar,
                           crear obras derivadas, publicar y distribuir, con
                           atribución e integridad.
                           Y luego: «For any potential **commercial reuse** of
                           IMF Data, please email … to request permission».  PROVISIONAL
RECOMMENDATION:            ⚠️ **NEEDS_REVIEW.** No usar hasta resolverlo.
```

Este es exactamente el caso que el §MUY IMPORTANTE pedía no dar por bueno. Hay
tres cláusulas y no se sabe cuál manda. **Y no hace falta resolverlo para el
MVP**: todo lo que el §7 pide del FMI (PIB, inflación, deuda, tipos, reservas,
comercio) lo da el Banco Mundial bajo CC BY 4.0, que es una licencia limpia. Lo
único exclusivo del FMI son las **previsiones** del WEO, y un MVP no las necesita.

**Decisión: FMI fuera de V1.** Se pide permiso por correo en paralelo y se
incorpora si contestan bien. Cuesta un email y no bloquea nada.

### Noticias — GDELT ⭐

```
SOURCE:                    The GDELT Project
DATA TYPE:                 Noticias globales, eventos, menciones, tono, entidades
URL:                       https://gdeltproject.org
API:                       DOC 2.0 API, ficheros de eventos/menciones cada 15 min,
                           BigQuery, y espejo en AWS Open Data Registry
API KEY:                   No
FREE:                      Sí                                           PROVISIONAL
COMMERCIAL USE:            ✅ «unlimited and unrestricted use for any **academic,
                           commercial, or governmental** use of any kind
                           **without fee**»                               PROVISIONAL
STORAGE:                   ✅                                            PROVISIONAL
REDISTRIBUTION:            ✅ «You may **redistribute, rehost, republish, and
                           mirror** any of the GDELT datasets»             PROVISIONAL
ATTRIBUTION:               Citar «The GDELT Project» con enlace a gdeltproject.org
HISTORICAL DATA:           1979 en adelante según dataset
UPDATE FREQUENCY:          15 minutos
TERMS:                     https://gdeltproject.org/about.html
                           https://registry.opendata.aws/gdelt/
RECOMMENDATION:            ⭐ Tier 1. **La fuente más permisiva de todo el research.**
```

Con diferencia la licencia más generosa que ha aparecido. Da todo lo que pide el
§9: recuento de noticias, tendencia, tono, entidades, países.

Dos avisos honestos sobre la calidad, porque la licencia es excelente pero el dato
no es mágico:

- **La resolución por empresa es aproximada.** GDELT indexa entidades por nombre,
  no por ticker ni CIK. «Apple» aparece en artículos que no hablan de Apple Inc.,
  y una empresa española mediana puede no aparecer casi nunca. Hace falta una capa
  de desambiguación propia y hay que medir su precisión antes de enseñar el número.
- **El tono no es sentimiento financiero.** Es un promedio léxico sobre el
  artículo entero. Sirve como serie relativa —si el tono de una empresa cae frente
  a su propia media— no como afirmación absoluta.

Ambas cosas van en la ficha del producto, no en una nota al pie: el §31 dice que
son preferibles 100 métricas fiables a 10.000 dudosas, y una métrica de
sentimiento presentada sin sus límites es de las dudosas.

### Noticias — RSS e Investor Relations

Sin ficha única: cada medio tiene sus términos. Las reglas que valen para todos y
que van al conector, no al criterio de quien lo use:

- Se guardan **titular, fuente, fecha, URL y metadatos**. Nunca el cuerpo del
  artículo.
- El resumen lo genera la IA a partir de *nuestros* metadatos y del dato
  estructurado, y siempre enlaza al original.
- Se respeta `robots.txt` y la cadencia que pida el feed.
- Los feeds de **reguladores** (CNMV, CVM, SEC) son categoría aparte y la mejor
  de todas: son la fuente primaria, no un medio.

Para Investor Relations, el §10 pide un sistema que permita incorporar una empresa
como fuente. El modelo está en
[`arquitectura.md`](arquitectura.md#investor-relations). La regla de licencia es
la misma en todos los casos: los documentos de IR son públicos pero **con
copyright del emisor**; se pueden descargar, procesar y citar, y no se pueden
republicar enteros.

---

## 5. Precios: el capítulo que no tiene final feliz

El §6 pedía investigar Yahoo Finance sin darla por válida. Resultado:

```
SOURCE:                    Yahoo Finance (vía yfinance)
COMMERCIAL USE:            ❌ «You must not redistribute information displayed on
                           or provided by Yahoo Finance». Prohibido reproducir,
                           modificar, alquilar, vender, distribuir, transmitir,
                           emitir, crear obra derivada o **explotar con fines
                           comerciales** sin permiso escrito.             PROVISIONAL
ACCESO AUTOMATIZADO:       ❌ Prohibido sin permiso escrito.               PROVISIONAL
LICENCIA CONCEDIDA:        Personal, no transferible, revocable, no exclusiva
TERMS:                     https://guce.yahoo.com/terms
                           https://legal.yahoo.com/us/en/yahoo/finance-guidelines/index.html
                           https://help.yahoo.com/kb/SLN2310.html
RECOMMENDATION:            ❌ **Tier 4 en producción. Tier 3 (C, solo desarrollo)
                           si se acepta el riesgo de que los términos tampoco
                           amparen el prototipado automatizado.**
```

> ### 🔑 La distinción que casi todo el mundo confunde
>
> **`yfinance` es software libre bajo Apache-2.0. Eso licencia el cliente, no el
> contenido.**
>
> La librería puede usarse comercialmente sin problema. Los datos que devuelve
> siguen siendo de Yahoo y de sus proveedores de mercado, bajo los términos de
> arriba. Que `pip install yfinance` no pida nada no dice absolutamente nada
> sobre si se pueden usar los datos en un producto de pago.
>
> Este proyecto ya tenía un adaptador de yfinance escrito y funcionando. Sigue en
> el repositorio, y a partir de ahora está marcado `DEVELOPMENT_ONLY` en el
> registro de fuentes, lo que significa que **el arranque en producción falla si
> alguien lo configura**. No por prudencia excesiva: porque era, literalmente, la
> fuente de precios del sistema anterior.

Las alternativas gratuitas dicen lo mismo:

| Fuente | Capa gratuita | Veredicto |
|---|---|---|
| **Alpha Vantage** | Atribución, **sin reventa**. Redistribución comercial y datos licenciados de bolsa exigen licencia aparte | ❌ producción |
| **Tiingo** | Prohíbe expresamente reventa y redistribución | ❌ producción |
| **Finnhub** | Licencia no comercial; en cuanto la app se monetiza hace falta plan de pago | ❌ producción |
| **EODHD free** | 20 llamadas/día, último año, solo EE. UU. Comercial → plan de pago | ❌ producción |
| **Marketstack free** | 100 peticiones/**mes**, 1 año de histórico | ❌ producción |
| **Stooq** | **Términos no localizables.** Cuota diaria baja («Exceeded the daily hits limit»). Fiabilidad dudosa | ❌ `NEEDS_REVIEW` → tratar como rechazada |

Y las bolsas, que sí publican ficheros históricos gratuitos (COTAHIST de B3,
*bhavcopy* de NSE), los publican bajo los términos que ya se han visto: accesibles
no es lo mismo que utilizables.

**Conclusión del capítulo:** no existe, para estos cuatro mercados, una fuente
gratuita de precios EOD con licencia clara para uso comercial. No es que no se
haya encontrado; es que el modelo de negocio de quien tiene el dato es
precisamente venderlo.

### Índices y benchmarks: el mismo muro

```
S&P Dow Jones Indices — «Redistribution or reproduction in whole or in part are
prohibited without written permission of S&P Dow Jones Indices LLC.» Niveles,
constituyentes y ponderaciones van por acuerdo de licencia de datos aparte, con
tarifas.                                                                PROVISIONAL
https://www.spglobal.com/spdji/en/disclaimers/
```

Por la misma lógica, IBEX 35 (BME/SIX), Ibovespa (B3), NIFTY 50 (NSE Indices) y
SENSEX (Asia Index / BSE) son productos licenciados. El §14 pedía calcular
rendimiento relativo y alfa contra el índice; **sin licencia de precios ni de
índices, no se puede**, y no hay atajo: un ETF que replique el índice sigue siendo
una cotización.

---

## 6. Calidad y riesgos

### Calidad, fuente por fuente

| Fuente | Cobertura | Latencia | Consistencia | Riesgo de calidad |
|---|---|---|---|---|
| SEC EDGAR | Total en EE. UU. | Minutos | Alta | Etiquetas XBRL heterogéneas entre emisores |
| CVM | Total en Brasil | Semanal | Alta | Esquema en portugués; reexpresiones |
| CNMV | Total en España | Días | Media | Documentos, no campos. Extracción frágil |
| FINRA | Total en EE. UU. | Bimensual | Alta | Baja frecuencia por diseño |
| BCE | 29 divisas | 1 día | Máxima | Calendario TARGET ≠ calendario de bolsa |
| Banco Mundial | 4 países | **Meses** | Alta | Revisiones retroactivas silenciosas |
| GDELT | Global | 15 min | Media | Desambiguación de entidad; falsos positivos |

Dos riesgos de calidad merecen tratamiento explícito en el motor de calidad
(§19, diseñado en [`arquitectura.md`](arquitectura.md#motor-de-calidad-de-datos)):

**Las revisiones retroactivas.** El Banco Mundial y los institutos nacionales
revisan series hacia atrás sin avisar. Si se guarda solo el último valor, la
historia del producto cambia sola y un análisis de hace tres meses ya no se puede
reproducir. La solución es guardar `(serie, fecha_dato, fecha_descarga, valor)` y
no `(serie, fecha_dato, valor)`.

**Las reexpresiones contables.** Una empresa reexpresa su ejercicio anterior y los
datos «históricos» dejan de ser los que se publicaron. Es el mismo problema con
otro nombre, y se resuelve igual: el filing manda, y cada hecho se ancla a la
`accn` y a la fecha de presentación que lo trajo.

### Riesgos del proyecto, ordenados por lo que duelen

| # | Riesgo | Probabilidad | Impacto | Mitigación |
|---|---|---|---|---|
| 1 | **Una licencia clave resulta ser peor de lo que dice este documento** | Media | **Alto** | Nada está verificado. Verificar la lista corta antes de cobrar. El registro de fuentes permite apagar una fuente sin tocar código |
| 2 | **Sin precios, el producto parece incompleto al usuario** | Alta | Medio | Decir qué falta y por qué, en la ficha. Es preferible un hueco explicado que un número de origen dudoso |
| 3 | La CNMV cambia el formato de sus ficheros | Media | Medio | Guardar el bruto; el conector se re-escribe sin re-descargar |
| 4 | B3 endurece su política el 01/01/2026 | **Ya ocurrido** | Bajo | No dependemos de B3 |
| 5 | El mapeo de conceptos XBRL falla en silencio | Alta | **Alto** | Contrato de datos: ninguna columna obligatoria entera a nulo. Ya implementado y con historia |
| 6 | GDELT confunde entidades y el sentimiento engaña | Alta | Medio | Medir la precisión antes de publicar la métrica; presentarla siempre relativa |
| 7 | India se queda fuera indefinidamente | Media | Medio | Es una decisión consciente, no un olvido |
| 8 | La IA rellena un hueco con una estimación | Media | **Alto** | El contexto es cerrado y las ausencias son explícitas: `null` no, `"no_disponible"` sí |

El riesgo 8 merece una nota. El §1 y el §27 son tajantes: la IA no inventa. La
forma de conseguirlo no es pedírselo en el prompt, es construir el contexto de
manera que la ausencia sea un dato. Está diseñado en
[`arquitectura.md`](arquitectura.md#el-analista-ia).

---

## 7. Recomendaciones

**Jerarquía de fuentes (§20), corregida por el research.** El §20 proponía para
Brasil `B3 → IR → otras` y para India `NSE → BSE → IR`. El research invierte
ambas:

| Dato | 🇺🇸 | 🇪🇸 | 🇧🇷 | 🇮🇳 |
|---|---|---|---|---|
| Estados financieros | SEC → IR | **CNMV → IR** → ❌BME | **CVM → IR** → ❌B3 | IR → ❌NSE/BSE |
| Iniciados | SEC Forms 3/4/5 | CNMV directivos | **CVM `vlmo`** | ❌ sin vía limpia |
| Cortos | FINRA | CNMV | ❌ | ❌ |
| Hechos relevantes | SEC 8-K | CNMV | CVM IPE | IR |
| Precios | ❌ licencia | ❌ licencia | ❌ licencia | ❌ licencia |

La regla general se mantiene y sale reforzada: **la fuente primaria manda sobre el
agregador.** Lo que cambia es quién es la fuente primaria. Para fundamentales
brasileños no es B3, es CVM.

**Arquitectura de fuentes por tier (§30):**

| Tier | Fuentes | Qué significa |
|---|---|---|
| **A — Core** | SEC EDGAR, CVM, BCE, Banco Mundial, GDELT | Oficiales, gratuitas, aptas para producción. Se construye encima |
| **B — Complementarias** | CNMV, FRED (lista blanca), FINRA, RSS de reguladores, IR | Gratuitas con restricciones asumibles o con trabajo extra |
| **C — Desarrollo** | yfinance, Stooq | Prototipar sí; dependencia de producción **jamás**. El registro lo impide |
| **D — Futuro** | Licencia EOD de pago, FMI (pendiente de permiso), NSE Data, S&P DJI | Cuando haya ingresos. Coste estimado en [`mvp-data-plan.md`](mvp-data-plan.md#coste-de-pasar-a-fuentes-profesionales) |

**Lo que hay que hacer, en orden:**

1. Verificar la lista corta de licencias contra la fuente primaria. Es media
   jornada de leer páginas web, y hasta que no esté hecha no se cobra.
2. Escribir el conector de SEC EDGAR. Es el que más producto entrega por línea.
3. Escribir el de CVM. Añade un país entero con el mismo esfuerzo.
4. BCE y Banco Mundial: baratos y desbloquean toda la capa macro y de divisas.
5. GDELT, con la capa de desambiguación medida.
6. La CNMV al final, porque es la cara y la que menos se parece a las demás.
7. Y en paralelo, escribir a Investor Relations de dos o tres emisores españoles
   para ver si dan sus estados financieros en formato estructurado. Cuesta un
   correo.

---

## 8. §33 — Criterio de éxito: las nueve respuestas

**La pregunta:** *¿Podemos construir una aplicación de análisis bursátil para
EE. UU., España, Brasil e India utilizando únicamente fuentes gratuitas y sin
pagar por market data durante el MVP?*

**Sí para el análisis fundamental en EE. UU., España y Brasil. No para precios,
valoración, indicadores técnicos ni benchmarks, en ningún mercado. India no entra.**

### 1. Qué podemos hacer

Estados financieros completos y con fecha real de publicación en EE. UU. y
Brasil, y con más trabajo en España. Crecimiento, márgenes, rentabilidad
(ROE/ROA/ROIC), estructura de balance, cobertura de intereses y flujo de caja,
todo calculado en casa. Actividad de iniciados en los tres mercados. Posiciones
cortas en EE. UU. y España. Hechos relevantes, participaciones significativas y
autocartera. Contexto macro de los cuatro países. Divisas y descomposición del
rendimiento por efecto divisa. Noticias con recuento, tendencia y tono. Un
Fundamental Score determinista y un analista IA que lo explica sin inventarlo.

### 2. Qué no podemos hacer

Enseñar un precio. Un gráfico de cotización. Capitalización bursátil. Ningún
múltiplo de valoración —PER, EV/EBITDA, P/B, P/S, FCF yield—. Ningún indicador
técnico. Ninguna comparación con índice, ni alfa, ni beta, ni drawdown. Ningún
Technical Score. Y nada de India.

Que quede claro por qué: **no es una limitación técnica, es una limitación de
licencia.** El código para calcular todo eso está escrito y probado en este mismo
repositorio.

### 3. Qué fuentes utilizar

Núcleo: **SEC EDGAR, CVM, BCE, Banco Mundial, GDELT.** Complemento: **CNMV,
FINRA, FRED con lista blanca, RSS de reguladores, Investor Relations.** Fuera:
todas las bolsas, Yahoo y los agregadores en capa gratuita. Tabla completa en
[`data-matrix.md`](data-matrix.md).

### 4. Qué datos almacenar

Todo lo que venga de fuentes Tier A y B, con el bruto original al lado del dato
normalizado, y con `source`, `source_url`, `retrieved_at`, `published_at`,
`data_date` y `confidence` en cada fila. De GDELT, solo metadatos: titular,
medio, fecha, URL, tono. Nunca el cuerpo de un artículo. Nada de fuentes Tier C
en la base de producción.

### 5. Qué datos calcular

Todos los ratios del §17 y todos los indicadores del §16 —cuando haya precios—,
más los cuatro scores del §18, el Insider Score y el efecto divisa. Regla del
§17 llevada a su conclusión: **no se compra ningún ratio que se pueda calcular.**
Y con las fuentes disponibles se pueden calcular todos los fundamentales.

### 6. Qué datos utilizará la IA

Solo el objeto de contexto del §27, construido desde la base de datos, con las
ausencias marcadas explícitamente. La IA no consulta fuentes, no navega y no
recuerda datos de su entrenamiento: interpreta lo que se le pasa. Si un bloque
falta, dice «No disponemos de este dato». Diseño completo en
[`arquitectura.md`](arquitectura.md#el-analista-ia).

### 7. Qué restricciones legales y técnicas existen

Legales: las de [`data-licensing.md`](data-licensing.md), y ninguna verificada
todavía. La más dura es que los precios están licenciados en los cuatro mercados.
Técnicas: 10 req/s en EDGAR, la CNMV sin API estructurada, el Banco Mundial con
latencia de meses, GDELT sin identificador de empresa fiable, y el FMI con unos
términos que se contradicen.

### 8. Qué fuentes sustituir si el proyecto crece

En cuanto haya ingresos: una **licencia EOD de pago** que sustituya al hueco de
precios —no a yfinance, que no debe llegar a producción— y que además abre India.
Después, si el volumen lo justifica: fundamentales de pago para España, que es
donde más caro sale el conector propio. Y si alguna vez hace falta enseñar el
IBEX o el Ibovespa, licencia de índices con BME/SIX o B3.

### 9. Cuánto costaría pasar a fuentes profesionales

Desglosado en
[`mvp-data-plan.md`](mvp-data-plan.md#coste-de-pasar-a-fuentes-profesionales).
El orden de magnitud: **de 0 € a unos 20–100 €/mes** se recupera la capa de
precios y con ella la valoración, la técnica y probablemente India. De ahí a
varios miles al mes está la redistribución en tiempo real y los índices, que es
otro producto y no hace falta.

El salto de 0 € a ~50 €/mes es, con diferencia, el euro mejor gastado del
proyecto: multiplica por dos las capas del producto.

---

## Fuentes candidatas identificadas pero NO investigadas

Se nombran aquí para que no se pierdan, **sin ninguna afirmación sobre ellas**.
Ninguna se ha buscado ni contrastada en esta fase:

- **GLEIF** — identificadores LEI. Resolvería parte del problema de identificadores.
- **OpenFIGI** (Bloomberg) — mapeo de identificadores.
- **EIA** (Dept. of Energy, EE. UU.) — energía y precios de crudo, API propia.
- **Banco Central do Brasil** — PTAX, el tipo de cambio oficial brasileño.
- **Reserve Bank of India** — tipos de referencia.
- **INE** (ES), **IBGE** (BR), **BLS**/**BEA** (US), **MOSPI** (IN) — macro nacional.
- **Eurostat** — macro europea armonizada.
- **ESMA FIRDS** — ISIN y LEI por instrumento; términos no localizados.
- **Deutsche Börse Public Dataset** — CC BY 4.0, pero Xetra, fuera de nuestros mercados.

---

## Cambios respecto a lo que este repositorio hacía antes

Este repositorio era un backtester de estrategia mixta. Lo que el research obliga
a cambiar:

| Antes | Ahora | Por qué |
|---|---|---|
| yfinance como fuente de precios de producción | `DEVELOPMENT_ONLY`, con fallo al arrancar | Sus términos no permiten uso comercial |
| EODHD como fuente de fundamentales | Solo con plan de pago; la capa gratuita no vale | Capa gratuita = no comercial |
| Sin registro de fuentes | `config/fuentes.yaml` aplicado en ejecución | Para que la licencia no dependa de la memoria |
| Motor de backtest, cartera y órdenes | Se retira a una etiqueta de git | Ya no es el producto |
| Benchmarks vía ETF (EUNL.DE, IS3N.DE) | Fuera | Una cotización de ETF es market data igual |

Lo que se conserva es justamente la espina dorsal de datos: interfaz de fuentes,
enrutador, contrato, almacén con vista a fecha, calendarios, indicadores y el
informe HTML. Unas 4.000 líneas ya probadas que encajan sin cambios en la
arquitectura de arriba.
