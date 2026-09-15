# Plan de datos del MVP

Qué se construye en V1, con qué fuentes, qué se deja fuera y qué cuesta encender
lo que falta.

> Las afirmaciones de licencia de las que depende este plan están todas
> `PROVISIONAL`. Ver [`data-licensing.md`](data-licensing.md#verificación-obligatoria-antes-de-cobrar).

---

## La decisión de producto

El research dejó una pregunta sobre la mesa: los fundamentales son gratis y
legales; los precios no lo son en ningún mercado. Hay dos maneras de responder a
eso.

**La primera es esperar.** Guardar el proyecto hasta poder pagar una licencia de
precios y lanzar entonces el producto completo, con su gráfico, sus múltiplos y
sus indicadores técnicos. Es la opción que se le ocurre a cualquiera.

**La segunda es lanzar lo que sí se puede**, que resulta ser once de las catorce
capas del producto, y encender las tres restantes cuando haya con qué.

Este plan toma la segunda, por tres razones:

1. **Lo que se puede hacer gratis es justamente lo que peor cubre la competencia.**
   Los agregadores gratuitos van todos sobrados de precios y gráficos, y cortos de
   *filings*, iniciados y posiciones cortas. El hueco del mercado está donde están
   las fuentes libres, no donde están las de pago.
2. **El coste de encender la capa de precios es de decenas de euros al mes**, no
   de miles, porque el producto no necesita redistribuir la serie. Esperar a
   tener ese dinero no es esperar mucho.
3. **Un producto en producción enseña cosas que un plan no enseña.** Sobre todo
   sobre la calidad real de los datos de la CNMV y sobre si la desambiguación de
   GDELT funciona.

**La condición que hace honesta esta decisión** es no fingir que las tres capas
que faltan no existen. La ficha de empresa dice qué falta y por qué, con estas
palabras o parecidas: *«Valoración y análisis técnico no disponibles: requieren
una licencia de datos de mercado que este servicio todavía no tiene.»* Es
preferible a un hueco sin explicar, y mucho preferible a rellenarlo con un
número de origen dudoso.

---

## 1. Qué fuentes utilizamos en V1

| Fuente | Qué aporta | Estado | Prioridad de construcción |
|---|---|---|---|
| **SEC EDGAR** | Estados financieros, iniciados, hechos relevantes, metadatos 🇺🇸 | `APPROVED_WITH_RESTRICTIONS` | **1.ª** |
| **CVM** | Estados financieros, iniciados, hechos relevantes 🇧🇷 | `APPROVED_WITH_RESTRICTIONS` | **2.ª** |
| **BCE** | Tipos de cambio de referencia | `APPROVED_WITH_RESTRICTIONS` | **3.ª** |
| **Banco Mundial** | Macro de los 4 países + materias primas mensuales | `APPROVED_WITH_RESTRICTIONS` | **4.ª** |
| **GDELT** | Noticias, recuento, tendencia, tono | `APPROVED_WITH_RESTRICTIONS` | **5.ª** |
| **FRED** | Macro de EE. UU. (lista blanca de series) | `APPROVED_WITH_RESTRICTIONS` | 6.ª |
| **FINRA** | Posiciones cortas 🇺🇸 | `NEEDS_REVIEW` → bloqueado hasta verificar | 7.ª |
| **CNMV** | Hechos relevantes, cortos, directivos, participaciones 🇪🇸 | `APPROVED_WITH_RESTRICTIONS` | 8.ª |
| **Investor Relations** | Estados financieros 🇪🇸 donde la CNMV no llegue | `APPROVED_WITH_RESTRICTIONS` | V1.1 |

**El orden no es caprichoso.** EDGAR primero porque entrega más producto por línea
de código que ninguna otra. CVM segunda porque añade un país entero con un
esfuerzo parecido. BCE y Banco Mundial en tercer y cuarto lugar porque son baratos
y desbloquean dos capas completas. CNMV la última de las de V1 porque es la que
más cuesta y la que menos se parece a las demás.

**Fuera de V1 y por qué:**

| Fuente | Motivo |
|---|---|
| Yahoo / yfinance | `DEVELOPMENT_ONLY`. Licencia personal no comercial |
| B3, BME, NSE, BSE | `REJECTED`. Market data licenciado |
| Alpha Vantage, Tiingo, Finnhub, EODHD free, Marketstack | `REJECTED`. Capa gratuita no comercial |
| Stooq | `REJECTED` por no tener términos localizables |
| FMI | `NEEDS_REVIEW`. Términos contradictorios, y el Banco Mundial cubre lo mismo |
| Índices (S&P DJI, IBEX, Ibovespa, NIFTY, SENSEX) | `REJECTED`. Todos licenciados |

---

## 2. Qué datos obtenemos de cada una

### SEC EDGAR 🇺🇸

Vía `data.sec.gov`: `submissions`, `companyfacts`, `companyconcept`, `frames`.

| Bloque | Qué sale | De dónde |
|---|---|---|
| Identidad | Nombre, CIK, ticker, exchange, SIC, domicilio fiscal | `company_tickers.json` + `submissions` |
| Resultados | Ingresos, margen bruto, resultado operativo, resultado neto, BPA básico y diluido | `companyfacts` US-GAAP |
| Balance | Caja, activo total, pasivo total, deuda corriente y no corriente, patrimonio neto | `companyfacts` |
| Flujo de caja | Flujo operativo, capex | `companyfacts` |
| Acciones | En circulación y media ponderada diluida | `companyfacts` + `dei` |
| Iniciados | Alta, compras, ventas, ejercicios de opciones y participación resultante | Forms 3/4/5 + Insider Transactions Data Sets |
| Hechos | Eventos codificados por *item* (2.02 resultados, 5.02 ceses…) | 8-K |
| Fechas reales | Fecha de presentación de cada hecho | `accn` + `filed` |

**Esa última fila es la que más vale y casi nadie usa.** Cada hecho XBRL trae la
fecha en que se presentó. Eso permite construir una base **point-in-time de
verdad** —saber qué se sabía y cuándo— en lugar de la reconstrucción con retraso
fijo que hacen los agregadores. Este repositorio ya tiene la infraestructura para
aprovecharlo: el almacén con vista a fecha de corte y los tests que comprueban que
ninguna decisión mira un día más allá.

Cobertura: emisores nacionales con 10-K/10-Q. Los extranjeros con ADR presentan
**20-F anual**, no trimestral: la granularidad trimestral no está garantizada y
eso hay que reflejarlo en la ficha, no promediarlo.

### CVM 🇧🇷

Ficheros CSV/ZIP por dataset y ejercicio, en `dados.cvm.gov.br`.

| Dataset | Qué da |
|---|---|
| `cia_aberta-doc-dfp` | Estados financieros anuales (equivalente al 10-K) |
| `cia_aberta-doc-itr` | Trimestrales (equivalente al 10-Q) |
| `cia_aberta-doc-fre` | Formulário de Referência: gobierno, retribución, riesgos, capital |
| `cia_aberta-doc-vlmo` | **Valores Mobiliários Negociados e Detidos** — el Form 4 brasileño |
| `cia_aberta-doc-fca` | Formulário Cadastral: metadatos de la compañía |

`vlmo` es el hallazgo que salva a Brasil: la negociación de administradores y
personas vinculadas la publica **el regulador**, no la bolsa. Brasil tiene
iniciados gratis y legales, igual que EE. UU.

### BCE 🌍

Tipos de cambio de referencia del euro, diarios, ~16:00 CET, 29 divisas. **BRL e
INR incluidos.** EUR/USD, EUR/BRL y EUR/INR directos; USD/BRL y USD/INR por cruce,
marcados como derivados nuestros y no como dato publicado por el BCE.

### Banco Mundial 🌍

PIB y crecimiento, inflación, paro, deuda, población y comercio para los cuatro
países, con el mismo esquema —que es lo que permite un Macro Score comparable
entre mercados—. Más el **Pink Sheet** mensual con Brent, cobre LME y oro.

### GDELT 🌍

Recuento de noticias, tendencia, tono medio, entidades y países. Se guarda
**titular, medio, fecha, URL, tono**. Nunca el cuerpo del artículo: no es una
política, es que la columna no existe en el esquema.

### FRED 🇺🇸

Solo series de una lista blanca, cada una con su titular anotado. Tipos de la Fed,
curva del Tesoro, IPC, paro, agregados monetarios. Ninguna serie de tercero sin
verificar por separado.

### CNMV 🇪🇸

En V1, solo lo que llega estructurado y barato:

- Información privilegiada y otra información relevante (ZIP + XML con marca de
  tiempo). MAR partió el antiguo «hecho relevante» en esas dos categorías.
- Posiciones cortas por emisor.
- Participaciones significativas y autocartera.
- Notificaciones de directivos y personas vinculadas (MAR art. 19) — el
  equivalente español del Form 4.

**Los estados financieros españoles no entran en V1.** La CNMV no tiene un
`companyfacts`: la información pública periódica llega como documento, no como
campos etiquetados, y extraer una cuenta de resultados comparable entre emisores
exige un pipeline de extracción sobre documentos. Eso es V1.1, apoyado en el
Investor Relations de cada emisor.

Consecuencia honesta: **en V1, una empresa española tiene ficha de gobierno,
flujos y noticias, pero no de fundamentales.** Se dice en la ficha.

---

## 3. Qué datos todavía NO podemos obtener

| Dato | Por qué | Se arregla con |
|---|---|---|
| **Precios OHLCV** | Licenciados en los cuatro mercados | Licencia EOD de pago |
| **Volumen** | Va en el mismo paquete | Idem |
| **Capitalización bursátil** | Necesita precio | Idem |
| **Todos los múltiplos**: PER, PER adelantado, P/S, P/B, EV/EBITDA, EV/Sales, FCF yield | Necesitan precio | Idem |
| **Todos los indicadores técnicos**: SMA, EMA, RSI, MACD, ROC, estocástico, Bollinger, ATR, OBV, volatilidad histórica | Necesitan OHLCV | Idem |
| **Rendimiento relativo, alfa, beta, drawdown** | Necesitan precio y benchmark | Licencia de precios + de índices |
| **Índices** (S&P 500, IBEX, Ibovespa, NIFTY, SENSEX) | Productos licenciados | Licencia de índices, miles €/mes |
| **India entera** | NSE y BSE prohíben la recolección; SEBI no publica en abierto | La licencia de precios cubre buena parte |
| **Estados financieros españoles** | La CNMV publica documentos, no campos | Trabajo propio, ~2 semanas (V1.1) |
| **Cortos en Brasil e India** | Sin vía localizada | — |
| **Materias primas diarias** | El Pink Sheet es mensual | Investigar EIA y otras |
| **Sentimiento minorista** | Sin fuente con licencia clara | — |

Los cuatro primeros y el de India **son el mismo problema**, y una sola licencia
los cierra todos. Eso es lo que hace que la hoja de ruta sea corta.

---

## 4. Qué datos calculamos nosotros

La regla del §17 llevada hasta el final: **no se compra ningún ratio que se pueda
calcular**. Con las fuentes de V1 se pueden calcular todos los fundamentales.

### Disponibles en V1 (solo necesitan estados financieros)

| Familia | Métricas |
|---|---|
| **Crecimiento** | Ingresos, BPA, EBITDA y FCF — interanual y CAGR a 3 y 5 años |
| **Rentabilidad** | Margen bruto, operativo y neto; ROE, ROA, ROIC |
| **Balance** | Deuda/Patrimonio, Deuda neta/EBITDA, ratio corriente, cobertura de intereses |
| **Flujo de caja** | Flujo operativo, FCF (= OCF − capex), margen FCF, conversión de caja |
| **Calidad** | Estabilidad del margen, consistencia del crecimiento, devengos vs caja |
| **Iniciados** | **Insider Score**: compras − ventas en ventana móvil, normalizado |
| **Divisa** | Descomposición del rendimiento: local vs EUR |

### Bloqueados hasta que haya precios

Valoración entera, técnico entero, relativo entero. El código para calcularlo está
escrito y probado en este repositorio; lo que falta es el derecho a alimentarlo.

### Ratios que NO se deben intentar calcular

El §17 pedía documentar esto explícitamente, y es tan importante como la lista de
los que sí:

| Ratio | Por qué no |
|---|---|
| **EV/EBITDA y cualquier EV** | EV necesita capitalización, que necesita precio. **Sin precio no hay EV.** Este repositorio ya tuvo el fallo de calcular puntuaciones con EV nulo y no enterarse: media puntuación fundamental dejó de funcionar en silencio (ver [`FUENTES.md`](../FUENTES.md#el-contrato)) |
| **ROE de bancos y aseguradoras** | La estructura de balance no es comparable. Un ROE de banco junto a uno industrial en la misma tabla es un error de método, no de dato |
| **Deuda neta/EBITDA con EBITDA ≤ 0** | El ratio cambia de signo y deja de significar nada. La regla correcta es suspender el filtro, no invertirlo |
| **ROE con patrimonio neto negativo** | Igual: matemáticamente sale un número, y ese número es basura |
| **PER adelantado** | Necesita estimaciones de consenso, que son un producto de pago. **No hay forma gratuita y legal de tenerlas** |
| **Crecimiento a 3 años con menos de 4 ejercicios** | Necesita cuatro cierres publicados. Con menos, el dato no existe: no se extrapola |

Las cuatro primeras son «trampas de signo» y ya están implementadas y probadas en
`src/estrategia/fundamental.py`. Son el tipo de error que no rompe nada, no avisa
y envenena un ranking entero.

---

## 5. Qué datos utilizará la IA

**Solo el objeto de contexto del §27**, construido desde la base de datos. La IA no
consulta fuentes, no navega y no recuerda datos de su entrenamiento.

```json
{
  "company":           { …identidad y metadatos },
  "price":             { "disponible": false, "motivo": "licencia_no_disponible" },
  "technical":         { "disponible": false, "motivo": "requiere_precios" },
  "fundamentals":      { …calculados por nosotros, con fecha de cada dato },
  "valuation":         { "disponible": false, "motivo": "requiere_precios" },
  "news":              { …titulares, recuento, tendencia, tono },
  "insiders":          { …operaciones y score },
  "corporate_actions": { …dividendos, splits, ampliaciones },
  "macro":             { …país y sector },
  "benchmark":         { "disponible": false, "motivo": "requiere_indices" },
  "scores":            { …con su composición y sus pesos }
}
```

**La ausencia es un dato, no un `null`.** Es la diferencia entre un modelo que
dice «no disponemos de este dato» y uno que rellena el hueco porque el hueco no
le dijo nada. Un `null` es ambiguo —¿falta, es cero, no aplica?—; un
`{"disponible": false, "motivo": "..."}` no lo es.

El diseño completo, con las reglas del prompt y cómo se verifica que se cumplen,
está en [`arquitectura.md`](arquitectura.md#el-analista-ia).

---

## 6. Qué queda fuera del MVP

**Por licencia:** precios, volumen, valoración, técnico, benchmarks, índices e
India. Y el FMI hasta que se aclaren sus términos.

**Por alcance, aunque las fuentes lo permitirían:**

- Estados financieros españoles (V1.1).
- Comparación con competidores. Necesita clasificación sectorial fiable en cuatro
  mercados con taxonomías distintas (SIC en EE. UU., CNAE en España, CNAE-BR en
  Brasil). Es un proyecto propio.
- Alertas y notificaciones.
- Carteras y seguimiento de posiciones. **El motor existe** —backtest, riesgo,
  órdenes, salidas, ya escrito y probado, bajo la etiqueta `motor-trading-v1`—
  pero hoy no es el producto, y su fuente de precios no puede usarse.
- API pública. V1 es interfaz web.
- Tiempo real. El §24 ya lo decía: no hace falta.

---

## Coste de pasar a fuentes profesionales

La respuesta a la pregunta 9 del §33.

### El salto que importa

| Nivel | Qué desbloquea | Coste aproximado |
|---|---|---|
| **0 €** (V1) | 11 de 14 capas. Fundamentales, iniciados, cortos, hechos, macro, divisas, noticias. EE. UU. y Brasil completos, España parcial | **0 €/mes** |
| **~20–100 €/mes** | **Precios EOD con uso comercial derivado.** Enciende valoración, técnico y relativo. Y normalmente **India**, porque los agregadores ya tienen cerrado el acuerdo con NSE | **el euro mejor gastado del proyecto** |
| ~500–2.000 €/mes | Fundamentales normalizados de pago, estimaciones de consenso, tiempo real diferido | Cuando el conector propio de España salga más caro que comprarlo |
| Miles €/mes + contrato | Redistribución de market data, índices licenciados, tiempo real | Otro producto. Probablemente nunca |

### Por qué la segunda fila es tan barata

Porque el producto **no redistribuye la serie de precios**. Muestra scores,
métricas derivadas y análisis. Eso encaja en una licencia de *uso derivado sin
redistribución*, que es el plan estándar de los agregadores de gama baja, no un
contrato con cada bolsa.

Y conviene decir lo que esa distinción **no** hace: no convierte una fuente
gratuita no comercial en utilizable. Yahoo sigue fuera, porque su licencia es
personal, y una licencia personal no se arregla usando el dato solo por dentro.
Lo que la distinción cambia es **el precio de la licencia que sí hay que
comprar** — uno o dos órdenes de magnitud.

### El orden de las compras

1. **Licencia EOD.** EODHD es la candidata natural: plan de pago con uso
   comercial, cobertura de los cuatro mercados, y **este repositorio ya tiene el
   adaptador escrito y probado contra respuestas grabadas**. El camino más corto
   de 0 € al producto completo es literalmente cambiar un estado en
   `config/fuentes.yaml` y poner una clave.
2. **Nada más, durante bastante tiempo.** Los fundamentales de pago solo compensan
   cuando el mantenimiento del conector de la CNMV empiece a doler.
3. **Índices, casi nunca.** Si un usuario necesita comparar con el IBEX, el coste
   de licenciarlo es desproporcionado frente al valor que añade. Hay
   alternativas: comparar contra la mediana del propio universo cubierto, que es
   un dato **nuestro** y no le debe nada a nadie.

Esa última idea merece quedarse: **un benchmark construido con nuestros propios
datos no tiene problema de licencia.** «Esta empresa está en el percentil 80 de
crecimiento de las 500 que cubrimos» responde a la misma pregunta del usuario que
«bate al índice en 11 puntos», sin pagar a S&P.

---

## Verificación de este plan

Antes de considerar el MVP listo para cobrar:

- [ ] Las siete líneas de la [verificación obligatoria](data-licensing.md#verificación-obligatoria-antes-de-cobrar), en `VERIFICADO`.
- [ ] `config/fuentes.yaml` carga, valida y **hace fallar el arranque** con una fuente `DEVELOPMENT_ONLY` en producción, con un test que lo demuestra.
- [ ] Ninguna fuente `REJECTED` o `NEEDS_REVIEW` instanciable.
- [ ] Toda fila de datos con `source`, `source_url`, `retrieved_at`, `published_at`, `data_date` y `confidence`.
- [ ] Atribución del BCE, del Banco Mundial (con su formato exacto) y de GDELT visible en el frontal.
- [ ] La ficha de empresa dice qué capas faltan y por qué, sin eufemismos.
- [ ] El contexto de la IA marca las ausencias explícitamente, y hay un test que comprueba que un bloque ausente produce «No disponemos de este dato».
- [ ] Ninguna columna `cuerpo` ni equivalente en la tabla de noticias.
