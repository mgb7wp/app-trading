# Arquitectura

Los diseños que el research no necesitaba red para producir: modelo canónico
(§21), motor de puntuación (§18), motor de calidad de datos (§19), contexto del
analista IA (§27), requisitos del screener (§26) y la arquitectura de conectores
(§23).

Nada de esto está implementado todavía. El §29 pedía no empezar por los
conectores, y este documento es lo que hay que tener escrito antes de escribirlos.

---

## La cadena, y qué garantiza cada eslabón

```
FUENTES EXTERNAS   → registro de fuentes: si el estado no es apto, no se instancia
DATA INGESTION     → un conector por fuente, sustituible, sin lógica de producto
RAW DATA           → el original tal cual llegó, con su hash. Nunca se descarta
NORMALIZATION      → unidades, divisa, signo, periodo fiscal, identificadores
CANONICAL MODEL    → el mismo modelo para los cuatro mercados
DATABASE           → toda fila con procedencia y fechas
ANALYTICS ENGINE   → ratios e indicadores calculados en casa
SCORING ENGINE     → determinista, versionado, reproducible
AI ANALYST         → interpreta. No inventa
FRONTEND / API
```

Tres invariantes que se sostienen solas por construcción, no por disciplina:

**Una fuente no apta no arranca.** El estado de `config/fuentes.yaml` se comprueba
en el enrutador, que es el único punto por el que pasan todos los datos.

**Ningún dato entra sin procedencia.** El enrutador estampa `fuente` en cada fila
y aplica el contrato. Ya está implementado: `src/estrategia/datos/enrutador.py`.

**Ninguna decisión mira el futuro.** El almacén sirve vistas con fecha de corte y
anota la fecha máxima leída, de modo que un test puede afirmar no solo que el
resultado es correcto, sino que para calcularlo no se miró un día más allá.
También implementado: `src/estrategia/datos/almacen.py`.

---

## Modelo canónico de datos

§21. El mismo modelo para 🇺🇸🇪🇸🇧🇷🇮🇳, con las diferencias entre mercados
absorbidas en la normalización y no propagadas hacia arriba.

### Los campos que lleva absolutamente todo

Antes de las entidades, la parte que se repite en cada una de ellas. El §19 los
pide y no son opcionales:

```
Procedencia (en toda fila de dato)
 ├── source            id de la fuente en config/fuentes.yaml
 ├── source_url        el documento concreto, no la página de inicio
 ├── retrieved_at      cuándo lo descargamos nosotros
 ├── published_at      cuándo lo publicó la fuente
 ├── data_date         a qué fecha se refiere el dato
 ├── confidence        0-1, del motor de calidad
 └── raw_ref           hash del bruto que lo produjo
```

Tres fechas distintas, no una. Es lo que permite responder «¿qué sabíamos el 3 de
marzo?», que es una pregunta diferente de «¿qué pasó el 3 de marzo?». Y `raw_ref`
es lo que permite auditar un número raro sin volver a descargar nada.

### Company

```
Company
 ├── id                 uuid interno. Nunca el ticker
 ├── name
 ├── legal_name
 ├── country            us | es | br | in
 ├── exchange
 ├── currency_quote     divisa de cotización
 ├── currency_report    divisa de los estados financieros
 ├── sector             taxonomía propia
 ├── industry
 ├── identifiers        → Identifier[]
 ├── fiscal_year_end    mes de cierre
 ├── ir_url
 ├── status             activa | suspendida | deslistada
 ├── listed_from
 └── delisted_at
```

**`currency_quote` y `currency_report` son dos campos distintos a propósito.** Una
empresa puede cotizar en una divisa y reportar en otra, y confundirlas produce un
EV que está mal por un factor de varias unidades sin que nada falle. Este
repositorio ya tiene la comprobación en `fundamental.valor_empresa()` precisamente
por eso.

**`status`, `listed_from` y `delisted_at` están desde el principio** aunque en V1
no haya fuente de empresas deslistadas. Es la única forma de atacar el sesgo de
supervivencia más adelante sin migrar el esquema, y el coste hoy es tres columnas
vacías.

### Identifier

El §21 ponía `isin` y `cik` como campos de `Company`. El research dice que eso no
aguanta:

```
Identifier
 ├── company_id
 ├── scheme            ticker | cik | isin | lei | cnpj | nif | figi | scrip_code
 ├── value
 ├── exchange          cuando el identificador es por mercado
 ├── valid_from
 └── valid_to          null = vigente
```

Tres razones para separarlo en una tabla:

1. **Ningún identificador es universal.** CIK solo existe en EE. UU. CNPJ solo en
   Brasil. ISIN no lo publica la SEC y el CUSIP es un producto licenciado, así que
   **no hay camino gratuito y limpio de CIK a ISIN**. Un campo `isin` obligatorio
   sería un campo vacío para todo el mercado estadounidense.
2. **Una empresa puede tener varios del mismo tipo.** Cotizaciones en varios
   mercados, tickers distintos por bolsa.
3. **Los tickers cambian.** Con `valid_from` y `valid_to`, un ticker reutilizado
   por otra empresa deja de ser una bomba.

### Price

```
Price
 ├── company_id
 ├── date
 ├── open, high, low, close
 ├── adjusted_close
 ├── volume
 ├── currency
 └── adjustment_ref    → qué corporate actions se aplicaron
```

**Vacía en V1**, por licencia. La tabla existe y el modelo está cerrado para que
encenderla sea cargar datos, no migrar.

`adjustment_ref` no es decoración: sin saber qué ajustes se aplicaron, dos series
de la misma empresa de dos fechas de descarga distintas no son comparables y nadie
sabe por qué.

### FinancialStatement

```
FinancialStatement
 ├── company_id
 ├── period_type            anual | trimestral | semestral
 ├── fiscal_year
 ├── fiscal_period          FY | Q1..Q4 | H1 | H2
 ├── period_start, period_end
 ├── currency
 ├── unit_scale             1 | 1e3 | 1e6
 ├── is_restated            ← reexpresado respecto a lo publicado antes
 ├── is_consolidated
 ├── accounting_standard    us_gaap | ifrs | br_gaap
 │
 ├── revenue, gross_profit, operating_income, ebitda, net_income
 ├── eps_basic, eps_diluted
 ├── cash, total_assets, total_liabilities, equity
 ├── debt_short, debt_long, debt_total, net_debt
 ├── operating_cash_flow, capex, free_cash_flow
 ├── shares_outstanding, shares_diluted_weighted
 │
 ├── filing_id             → el documento que lo trajo
 └── (procedencia)
```

Cuatro decisiones que vienen de haberse quemado antes:

**`unit_scale` explícito.** Es la causa número uno de errores de mil veces. Si el
valor y su escala viajan juntos, el error deja de ser posible; si la escala se
infiere del contexto, aparece cuando una fuente cambia de criterio.

**`accounting_standard` explícito.** US-GAAP e IFRS no calculan lo mismo con el
mismo nombre. Comparar un ROIC entre estándares sin decirlo es un error de método
que ningún test de código detecta.

**`is_restated`.** Una empresa reexpresa un ejercicio y los datos «históricos»
dejan de ser los que se publicaron. Sin esta bandera, la historia del producto
cambia sola y un análisis de hace tres meses no se puede reproducir.

**`ebitda`, `net_debt` y `free_cash_flow` son campos calculados, no leídos.** Se
derivan con una fórmula versionada y se guardan con la versión de la fórmula. Es
la regla del §17 —no comprar lo que se puede calcular— aplicada también al
almacenamiento.

### Filing

```
Filing
 ├── company_id
 ├── form_type          10-K | 10-Q | 8-K | 20-F | 6-K | 3 | 4 | 5 | DFP | ITR
 │                      | FRE | VLMO | IPP | IAGC | info_privilegiada | …
 ├── filed_at           ← la fecha real de publicación
 ├── period_end
 ├── accession_number
 ├── url
 ├── items              códigos, cuando existen (8-K item 2.02, …)
 └── raw_ref
```

`filed_at` es lo que hace posible el point-in-time de verdad. EDGAR y CVM lo dan.
La CNMV lo da para comunicaciones. Es el campo que separa este producto de un
agregador que reconstruye con retraso fijo.

### InsiderTransaction

```
InsiderTransaction
 ├── company_id
 ├── insider_name, insider_role, is_director, is_officer, is_ten_percent_owner
 ├── transaction_date, reported_date
 ├── transaction_type   compra | venta | opcion | donacion | herencia | otro
 ├── shares, price, value, currency
 ├── shares_after
 ├── is_derivative
 ├── is_planned         ← plan preestablecido (10b5-1 y equivalentes)
 └── filing_id
```

**`is_planned` es el campo que decide si el Insider Score dice algo.** Una venta
ejecutada bajo un plan preestablecido meses antes no es una señal sobre la
empresa: es un calendario. Un score que las mezcla mide ruido. En EE. UU. el
Form 4 lo marca; en Brasil y España hay que ver qué llega y, si no llega, decirlo
en la ficha en vez de suponerlo.

### ShortInterest

```
ShortInterest
 ├── company_id
 ├── report_date, settlement_date
 ├── shares_short
 ├── shares_short_prior
 ├── pct_of_float          solo si float es fiable
 ├── days_to_cover         solo si hay volumen → no en V1
 └── holder                CNMV publica por titular; FINRA agrega
```

Dos cosas que no se pueden calcular en V1 y que el esquema deja claras:
`days_to_cover` necesita volumen —que está licenciado— y `pct_of_float` necesita
un *float* fiable, que no es lo mismo que las acciones en circulación.

España y EE. UU. no publican lo mismo: la CNMV da posiciones **por titular** por
encima de un umbral; FINRA da el **agregado**. No son comparables entre sí y el
modelo no debe fingir que sí.

### CorporateAction

```
CorporateAction
 ├── company_id
 ├── type              dividendo | dividendo_extra | split | contrasplit
 │                     | bonus | ampliacion | spinoff | fusion | adquisicion
 │                     | recompra
 ├── announcement_date, ex_date, record_date, payment_date, effective_date
 ├── ratio             para splits y bonus
 ├── amount, currency  para dividendos
 ├── confidence        ← casi siempre extraído de texto
 └── source
```

`confidence` está aquí y no en otras entidades porque estos datos casi siempre
salen de clasificar texto libre —un 8-K, un hecho relevante— y no de un campo
etiquetado. Es honesto marcar que un split detectado por texto es menos seguro que
un ingreso leído de XBRL.

### News

```
News
 ├── company_id        puede ser null: noticia sectorial o macro
 ├── title
 ├── source_name, url, published_at, language, country
 ├── tone              GDELT
 ├── event_type
 ├── relevance         ← confianza de la desambiguación de entidad
 └── (sin cuerpo)
```

> **No hay columna `body`, y esa ausencia es la política.** Una regla escrita en un
> documento se incumple el día que alguien piensa que la IA resumiría mejor con el
> texto completo. Una columna que no existe, no.

`relevance` es el campo que mantiene honesta la capa de noticias: GDELT indexa por
nombre, no por ticker, y hay que poder filtrar por confianza de la asociación.

### MacroSeries y FxRate

```
MacroSeries
 ├── series_id, source, country, indicator
 ├── data_date, value, unit
 ├── vintage_date      ← cuándo se descargó ESTE valor
 └── is_revision

FxRate
 ├── base, quote, date, rate
 ├── source            ecb
 └── is_derived        ← true en cruces calculados por nosotros
```

**`vintage_date` resuelve las revisiones retroactivas.** El Banco Mundial y los
institutos nacionales revisan series hacia atrás sin avisar. Guardando
`(serie, fecha_dato, fecha_descarga, valor)` en vez de `(serie, fecha_dato, valor)`,
un análisis de hace tres meses sigue siendo reproducible.

**`is_derived` cumple una condición de licencia del BCE.** Sus términos permiten
la reutilización si se cita la fuente y **no se modifican los datos**. Un cruce
USD/BRL calculado a partir de EUR/USD y EUR/BRL es un dato nuestro, y así hay que
etiquetarlo. Presentarlo como tipo publicado por el BCE sí sería alterar el dato.

### Score

```
Score
 ├── company_id, as_of_date
 ├── kind              fundamental | technical | sentiment | macro | overall
 ├── value             0-100
 ├── components        {factor: {valor, peso, percentil, disponible}}
 ├── engine_version    ← versión del motor que lo produjo
 └── missing_factors   [] ← qué faltó y por qué
```

`engine_version` y `missing_factors` son los dos campos que hacen auditable un
score. Sin el primero, un cambio en la fórmula reescribe el pasado en silencio.
Sin el segundo, un score al que le falta un factor es indistinguible de uno
completo.

---

## Motor de puntuación

§18. La regla que lo gobierna todo: **el score lo produce código determinista. La
IA explica, contextualiza, compara y resume, pero no lo inventa.**

### Cómo se puntúa un factor

Percentil dentro de una cohorte, no umbral absoluto. Un ROE del 12 % es distinto
en una utility que en una tecnológica, y un umbral fijo mide sector, no calidad.

La cohorte es **sector × mercado**, con una regla de repliegue cuando no hay
suficientes empresas: sector global → mercado → universo. Y con un mínimo por
debajo del cual el factor no se puntúa: con seis empresas, un percentil no es
una medida, es una anécdota.

Los percentiles se calculan con posiciones de Hazen, `(rango − 0,5) / n`, y no con
`(r−1)/(n−1)`. Esta última asigna 0 y 100 exactos a los extremos, lo que convierte
a la empresa peor y mejor de la muestra en valores de libro en vez de en los
extremos observados de una muestra pequeña. Ya está implementado en
`src/estrategia/fundamental.py`.

### Fundamental Score

| Factor | Peso | Métricas | V1 a 0 € |
|---|---|---|---|
| Growth | 20 % | Ingresos, BPA, EBITDA y FCF: interanual y CAGR 3a | ✅ |
| Profitability | 20 % | Margen bruto, operativo, neto; ROE, ROA, ROIC | ✅ |
| Balance Sheet | 15 % | D/E, deuda neta/EBITDA, ratio corriente, cobertura | ✅ |
| Cash Flow | 15 % | Margen FCF, conversión de caja, devengos vs caja | ✅ |
| **Valuation** | **20 %** | PER, P/S, P/B, EV/EBITDA, FCF yield | ❌ **requiere precio** |
| Quality | 10 % | Estabilidad del margen, consistencia, dilución | ✅ |

**Sin precios, el peso de Valuation se redistribuye proporcionalmente entre los
cinco restantes**, `missing_factors` lo recoge y la ficha lo enseña. No se
sustituye por un proxy: no hay ningún sustituto honesto de un múltiplo.

### Technical Score

Trend, Momentum, Relative Strength, Volatility, Volume. **Cero de cinco factores
disponibles a 0 €.**

> **No se publica un Technical Score parcial.** No es que le falte un factor: le
> faltan los cinco. Un «Technical Score» sin precio no es un score incompleto, es
> un número inventado. En V1 el bloque se marca `disponible: false` y se explica
> por qué.

### Sentiment Score

| Factor | Peso | Fuente | V1 |
|---|---|---|---|
| News sentiment | 40 % | Tono medio GDELT, relativo a la propia media de la empresa | ⚠️ |
| News volume | 25 % | Recuento contra la media de 90 días | ✅ |
| News momentum | 25 % | Derivada del recuento y del tono | ⚠️ |
| Retail sentiment | 10 % | — | ❌ sin fuente con licencia clara |

Los ⚠️ son honestos: el tono de GDELT es un promedio léxico sobre el artículo
entero, no sentimiento financiero, y la asociación empresa-artículo es
aproximada. El score se publica **siempre relativo a la propia historia de la
empresa**, nunca como afirmación absoluta, y con la precisión de la
desambiguación medida y visible.

### Macro Score

Rates, Inflation, GDP, Currency, Sector conditions. Cuatro de cinco disponibles;
*sector conditions* se limita a materias primas mensuales del Pink Sheet.

Es un score **de país y sector**, no de empresa, y se aplica a la empresa por su
domicilio y su sector. Que eso es una aproximación —una exportadora brasileña no
vive la macro brasileña como una eléctrica regulada— tiene que estar dicho.

### Overall

Media ponderada de los cuatro. En V1, con Technical fuera y Sentiment degradado,
los pesos se redistribuyen y la composición es visible en la ficha.

**Reglas que no se negocian:**

1. El score es reproducible: mismos datos y misma `engine_version` → mismo número.
2. Un cambio de fórmula sube `engine_version` y **no reescribe los scores
   pasados**.
3. `missing_factors` nunca va vacío por conveniencia.
4. La IA recibe el score y su composición. **Nunca se le pide que lo estime.**

---

## Motor de calidad de datos

§19. Lo que se comprueba, dónde y qué pasa cuando falla.

Se aplica en la normalización, antes de escribir en el modelo canónico. La
alternativa —comprobar al leer— llena la base de basura y la limpia a mano para
siempre.

| Comprobación | Detecta | Acción |
|---|---|---|
| **Columna obligatoria entera a nulo** | Mapeo roto | **Rechazar el lote** |
| Duplicados por clave natural | Ingesta doble | Rechazar el duplicado |
| Fechas fuera de rango o futuras | Error de parseo | Rechazar la fila |
| Salto de escala (×1.000 entre periodos) | Cambio de `unit_scale` | Rechazar y avisar |
| Cambio de divisa sin cambio declarado | Error de mapeo | Rechazar y avisar |
| Identidad contable (activo ≠ pasivo + patrimonio) | Parseo o consolidación | Marcar `confidence` bajo |
| Valor extremo (>5σ de la propia historia) | Outlier o error | Marcar, no rechazar |
| Dato más viejo que el umbral de su tipo | Fuente parada | Marcar como obsoleto |
| Signo imposible (ingresos < 0) | Error de parseo | Rechazar |
| Licencia del dataset cambiada desde la última ingesta | Cambio de términos | **Parar la ingesta y avisar** |

**La primera merece su párrafo, porque tiene una historia en este repositorio.** El
proveedor de yfinance devolvía la columna `ev` entera a nulo, con un comentario
que decía que se completaría más adelante y que nadie completó. Efecto: EV/EBIT
nunca se podía calcular, la valoración puntuaba cero para todas las empresas y
**la mitad del peso de la puntuación fundamental dejaba de hacer nada**. No se
caía nada. No salía ningún aviso. El ranking simplemente pasaba a decidirse solo
por calidad.

La lección no es «revisar mejor»: es que **una fuente puede cumplir la forma del
contrato y no su fondo**. Un hueco suelto es un dato que falta, cosa normal. Una
columna entera vacía es un mapeo roto. Ya está implementado en
`src/estrategia/datos/contrato.py`.

**La última también.** Los términos de CVM dicen que la licencia va en el metadato
de cada dataset y puede cambiar en cualquier momento. Comprobarlo en cada ingesta
cuesta una línea y evita descubrir un cambio de licencia por la vía cara.

### Cómo se calcula `confidence`

```
confidence = 1.0
  × 1.00 si fuente Tier A     × 0.90 Tier B      × 0.70 Tier C
  × 1.00 si dato etiquetado (XBRL, CSV estructurado)
  × 0.80 si extraído de tabla en documento
  × 0.60 si extraído de texto libre
  × 0.90 si is_restated
  × (penalización por antigüedad según el tipo de dato)
```

No es una probabilidad y no hay que fingir que lo es. Es una ordenación que
permite tres cosas concretas: filtrar en el screener, mostrarlo en la ficha, y
que el analista IA sepa de qué se puede fiar más.

---

## El analista IA

§27. El requisito es que la IA **no invente** precios, ratios, resultados,
crecimiento, noticias, fechas, datos macro ni información corporativa.

Pedírselo en el prompt no basta. Hay que construir el contexto de modo que
inventar sea difícil y se note.

### Cuatro reglas de construcción

**1. El contexto es cerrado.** La IA no consulta fuentes, no navega y no usa lo
que recuerde de su entrenamiento. Solo lee el objeto que se le pasa.

**2. La ausencia es un dato, no un `null`.**

```json
"valuation": {
  "disponible": false,
  "motivo": "requiere_precios",
  "explicacion": "No disponemos de licencia de datos de mercado."
}
```

Un `null` es ambiguo: ¿falta, es cero, no aplica? Un modelo que ve `"per": null`
puede razonablemente pensar que debe estimarlo. Un modelo que ve
`{"disponible": false, "motivo": "requiere_precios"}` no tiene ese hueco que
rellenar.

**3. Cada dato lleva su fecha y su procedencia.** Así la IA puede decir «según el
10-Q presentado el 2 de agosto» en vez de «actualmente», que es una palabra que no
significa nada en un documento generado.

**4. Los números vienen calculados.** La IA no multiplica, no divide y no calcula
percentiles. Recibe el ratio y el percentil ya hechos. Un LLM haciendo aritmética
sobre datos financieros es un error esperando su turno.

### El prompt, en lo esencial

```
Eres un analista financiero. Trabajas EXCLUSIVAMENTE con el contexto JSON
que se te proporciona.

NUNCA inventes ni estimes: precios, ratios, resultados, crecimiento,
noticias, fechas, datos macro o información corporativa.

Si un bloque tiene "disponible": false, di literalmente
"No disponemos de este dato" y explica el motivo que indica el contexto.
No lo sustituyas por una estimación, ni por conocimiento general, ni por
lo que sea habitual en el sector.

Cita siempre la fecha del dato que uses.
No des recomendaciones de compra o venta.
```

### Cómo se comprueba que se cumple

Esto es lo que convierte la regla en una garantía:

- **Tests con bloques ausentes.** Un contexto sin `valuation` debe producir «no
  disponemos» y nunca un PER. Un contexto sin `price` no puede producir una cifra
  de cotización.
- **Verificación numérica automática.** Se extraen los números de la respuesta y
  se comprueba que **todos** aparecen en el contexto. Un número que no está en el
  contexto es una alucinación, y es detectable sin juicio humano.
- **Tests con datos contradictorios.** El §27 dice que la IA debe poder encontrar
  contradicciones. Un contexto con crecimiento alto y flujo de caja negativo debe
  producir una observación sobre eso.

La verificación numérica es la más valiosa de las tres: es barata, es automática y
detecta exactamente el fallo que más importa.

---

## Requisitos del screener

§26. Qué datos hacen falta para responder a las consultas del ejemplo.

| Consulta del §26 | Necesita | V1 a 0 € |
|---|---|---|
| «USA, crecimiento >15 %, deuda baja y tendencia alcista» | Crecimiento ✅ · Deuda ✅ · **Tendencia ❌** | **Parcial** |
| «Españolas con ROIC elevado y valoración razonable» | ROIC ⚠️ (V1.1) · **Valoración ❌** | **No** |
| «Brasileñas con momentum positivo y fundamentales mejorando» | **Momentum ❌** · Mejora ✅ | **Parcial** |
| «Indias con crecimiento superior al mercado» | **India ❌** | **No** |

Dos de cuatro salen a medias y dos no salen. Merece decirlo así de claro.

**Lo que sí se puede ofrecer en V1** —y no es poco—:

```
Crecimiento de ingresos           > X %   (1a, 3a CAGR)
Crecimiento de BPA                > X %
Margen operativo                  > X %
ROE / ROA / ROIC                  > X %
Deuda neta / EBITDA               < X
Cobertura de intereses            > X
Margen de FCF                     > X %
Insider Score                     > X
Posición corta (US, ES)           < X %
Fundamental Score                 > X
Confianza del dato                > X      ← poco habitual y muy útil
Sector, país, tamaño por activos
```

Ese penúltimo filtro es de los que diferencian: poder pedir «solo empresas cuyos
datos tengan confianza alta» es una función que casi ningún screener ofrece, y
sale gratis de haber diseñado bien el motor de calidad.

**Requisitos técnicos**, que condicionan el esquema:

- **Los ratios se precalculan y se indexan.** Calcularlos al vuelo en una consulta
  multipaís no escala.
- **Una vista `metricas_actuales` por empresa**, materializada, con la última
  fecha de cada métrica.
- **Los percentiles se guardan junto al valor**, para poder filtrar por «top 20 %
  de su sector» sin recalcular la cohorte en cada consulta.
- **Todo filtro respeta `confidence`** y el screener declara cuántas empresas
  quedaron excluidas por falta de dato. Un screener que devuelve 12 empresas de un
  universo de 500 sin decir que 300 no tenían el dato está mintiendo por omisión.

---

## Conectores

§23. Uno por fuente, sustituible, sin lógica de producto.

```
/connectors
    /sec          EDGAR: submissions, companyfacts, forms 3/4/5, 8-K
    /cnmv         comunicaciones, cortos, directivos, participaciones
    /cvm          dfp, itr, fre, vlmo, fca
    /finra        equity short interest
    /fred         macro US, con lista blanca de series
    /ecb          tipos de cambio de referencia
    /worldbank    macro 4 países + pink sheet
    /gdelt        noticias y tono
    /investor_relations
```

Sin `/b3`, `/nse` ni `/bse`: están `REJECTED`. No existir es la forma más fiable
de no usarse.

**El contrato de todo conector:**

```python
class Conector(Protocol):
    nombre: str
    capacidades: Capacidades      # qué resuelve y qué no

    def descargar(self, peticion) -> Bruto: ...
    def normalizar(self, bruto: Bruto) -> list[FilaCanonica]: ...
```

Separar `descargar` de `normalizar` es lo que permite re-parsear cuatro años de
filings sin volver a descargarlos cuando se encuentra un error de mapeo. Y hace
que `normalizar` sea una función pura, que es la parte donde de verdad se cometen
los errores y la única que se puede probar sin red y sin claves.

**`capacidades` no es documentación**: la ficha de empresa la lee para saber de qué
avisar. Rellenarla con optimismo no mejora el sistema, hace que deje de avisar de
sus propios límites. Ya está implementado en `src/estrategia/datos/proveedor.py`.

### Frecuencia

§24. Nada en tiempo real en V1.

| Cadencia | Qué |
|---|---|
| **Diaria** | Tipos del BCE, GDELT, comprobación de nuevos filings |
| **Semanal** | CVM (publica semanalmente), recálculo de scores y percentiles |
| **Quincenal** | FINRA short interest |
| **Mensual** | Banco Mundial, Pink Sheet |
| **Por evento** | Filings, resultados, dividendos, corporate actions, iniciados |

«Por evento» significa: se detecta que hay un filing nuevo en la pasada diaria y se
procesa entonces, no que haya *webhooks*. Para una cadencia de revisión diaria no
hace falta más.

### Investor Relations

§10. El modelo que permite incorporar una empresa como fuente:

```
IRSource
 ├── company_id
 ├── ir_url
 ├── feed_url            RSS o Atom, si lo hay
 ├── scrape_allowed      ← leído de robots.txt, no supuesto
 ├── last_checked
 └── documents → IRDocument[]

IRDocument
 ├── company_id, ir_source_id
 ├── document_type   earnings_release | annual_report | quarterly_report
 │                   | presentation | guidance | announcement | shareholder_info
 ├── title, publication_date, source_url, language
 ├── local_ref       ← copia privada para procesar, nunca pública
 ├── extraction_status
 └── extracted_to    → filing_id / financial_statement_id
```

**La regla de licencia, en el esquema.** Los documentos de IR son públicos y
tienen copyright del emisor. Se pueden descargar, procesar, extraer cifras y citar
con enlace al original. No se pueden republicar enteros ni alojar copias
públicas. Por eso `local_ref` es privado por diseño y lo que se publica es
`source_url`.

`scrape_allowed` se lee de `robots.txt` en cada pasada y se guarda. No se supone,
y no se decide una vez.

---

## Qué se conserva de este repositorio

El §23 pedía conectores independientes sobre una espina dorsal común. Esa espina
ya existe, probada, y encaja sin cambios:

| Módulo | Qué aporta |
|---|---|
| `datos/proveedor.py` | Interfaz de fuente y declaración de capacidades |
| `datos/registro.py` | Nombre → constructor, con importación perezosa |
| `datos/enrutador.py` | **El único punto por el que pasan todos los datos.** Estampa procedencia y aplica el contrato |
| `datos/contrato.py` | Base del motor de calidad, con la regla de la columna entera a nulo |
| `datos/almacen.py` | Vista a fecha de corte y anotación de la fecha máxima leída |
| `calendario.py` | Sesiones por mercado, vectorizado. Ya cubre los cuatro |
| `indicadores.py` | Medias, ATR de Wilder, momentum. A ampliar con RSI, MACD, estocástico, Bollinger, OBV, beta y volatilidad histórica |
| `fundamental.py` | Percentiles de Hazen, trampas de signo, puntuación 0-100 |
| `metricas.py` | CAGR, drawdown, Sharpe |
| `informe_html.py` | Página autocontenida, sin JS ni CDN, paleta validada |
| `diagnostico.py` | Qué resuelve cada fuente y qué no, ticker a ticker |

Y lo que se retira a una etiqueta de git, porque ya no es el producto:
`backtest.py`, `ordenes.py`, `cartera.py`, `riesgo.py`, `salidas.py`,
`seleccion.py` y `validacion.py`. Están escritos y probados; el día que haya un
producto de carteras, ese motor existe.
