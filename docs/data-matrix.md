# Matriz dato × país

Qué fuente concreta resuelve cada dato en cada mercado, y dónde están los huecos.

> **Nada de esta matriz está verificado contra la fuente primaria.** Cada celda
> hereda el estado de verificación de su fuente en
> [`data-licensing.md`](data-licensing.md). Ver el
> [aviso completo](data-sources.md#️-estado-de-verificación-nada-está-verificado).

**Leyenda:**

| Símbolo | Significa |
|---|---|
| ✅ | Fuente disponible, gratuita y con licencia aparentemente apta para uso comercial |
| ⚠️ | Disponible, pero con restricción, trabajo extra o licencia sin resolver |
| ❌ | **No hay vía gratuita y legalmente utilizable.** Hueco real |
| 🔒 | El dato existe y es accesible, pero su licencia lo prohíbe en un producto comercial |

---

## La matriz

| Dato | 🇺🇸 EE. UU. | 🇪🇸 España | 🇧🇷 Brasil | 🇮🇳 India | Fuente recomendada |
|---|---|---|---|---|---|
| **Prices** (OHLC) | 🔒 | 🔒 | 🔒 | 🔒 | **Ninguna gratuita.** Licencia EOD de pago |
| **Volume** | 🔒 | 🔒 | 🔒 | 🔒 | Idem — va en el mismo paquete que el precio |
| **Fundamentals** (ratios) | ✅ calculados | ⚠️ calculados | ✅ calculados | ❌ | Cálculo propio sobre estados financieros |
| **Financial statements** | ✅ SEC EDGAR XBRL | ⚠️ CNMV IPP + IR | ✅ CVM DFP/ITR | ❌ | Regulador |
| **Insider trading** | ✅ SEC Forms 3/4/5 | ⚠️ CNMV directivos | ✅ CVM `vlmo` | 🔒 NSE/BSE | Regulador |
| **Short interest** | ✅ FINRA | ✅ CNMV | ❌ | ❌ | Regulador |
| **Dividends** | ⚠️ SEC 8-K + XBRL | ⚠️ CNMV inf. relevante | ⚠️ CVM IPE | ❌ | Regulador, clasificando el texto |
| **Splits** | ⚠️ SEC 8-K + `dei` | ⚠️ CNMV inf. relevante | ⚠️ CVM IPE | ❌ | Idem — **ver aviso abajo** |
| **Corporate actions** | ⚠️ SEC 8-K *items* | ⚠️ CNMV inf. relevante | ⚠️ CVM IPE | ❌ | Idem |
| **News** | ✅ GDELT + RSS | ✅ GDELT + RSS | ✅ GDELT + RSS | ✅ GDELT + RSS | GDELT |
| **Sentiment** | ⚠️ GDELT tone | ⚠️ GDELT tone | ⚠️ GDELT tone | ⚠️ GDELT tone | GDELT, con cautelas |
| **Macro** | ✅ FRED + BM | ✅ BCE + BM | ✅ BM | ✅ BM | Banco Mundial como base común |
| **FX** | ✅ BCE | ✅ BCE | ✅ BCE | ✅ BCE | **BCE, las cuatro divisas** |
| **Indices** | 🔒 S&P DJI | 🔒 BME/SIX | 🔒 B3 | 🔒 NSE/BSE | **Ninguna gratuita** |
| **Commodities** | ⚠️ BM Pink Sheet (mensual) | ⚠️ idem | ⚠️ idem | ⚠️ idem | Banco Mundial, mensual |

### Cómo leer las dos filas de arriba

Las filas *Prices* y *Volume* llevan 🔒 y no ❌ a propósito, y la diferencia
importa. El dato existe, es accesible y hasta se descarga con dos líneas de
Python. Lo que falta no es el dato: es el derecho a usarlo. Un ❌ se arregla
buscando mejor; un 🔒 se arregla firmando.

### El aviso de los splits

El §13 lo planteaba bien: si una acción pasa de 100 a 50 por un split 2:1, el
sistema no debe decir «ha caído un 50 %».

En V1 **ese riesgo no existe, porque no hay serie de precios**. Pero aparece el
minuto uno en que se encienda la capa de precios, y para entonces la detección de
splits tiene que estar ya construida y probada. Por eso las corporate actions
están en el MVP aunque su consumidor principal todavía no exista: es más barato
tenerlas listas que descubrir el problema con usuarios delante.

Y hay un segundo motivo, independiente de los precios: un split cambia el número
de acciones, y el número de acciones entra en el BPA y en cualquier magnitud por
acción. Las corporate actions hacen falta aunque nunca se dibuje un gráfico.

---

## El mismo cuadro, por capa de producto

Qué partes del producto se encienden con fuentes a 0 € y cuáles no:

| Capa | Depende de | 🇺🇸 | 🇪🇸 | 🇧🇷 | 🇮🇳 | V1 a 0 € |
|---|---|:-:|:-:|:-:|:-:|---|
| Identidad de empresa | Regulador | ✅ | ✅ | ✅ | ❌ | **Sí** |
| Estados financieros | Regulador | ✅ | ⚠️ | ✅ | ❌ | **Sí** (ES en 2.ª pasada) |
| Crecimiento | Estados financieros | ✅ | ⚠️ | ✅ | ❌ | **Sí** |
| Rentabilidad y márgenes | Estados financieros | ✅ | ⚠️ | ✅ | ❌ | **Sí** |
| Balance y solvencia | Estados financieros | ✅ | ⚠️ | ✅ | ❌ | **Sí** |
| Flujo de caja | Estados financieros | ✅ | ⚠️ | ✅ | ❌ | **Sí** |
| **Valoración** | **Precio** + estados | 🔒 | 🔒 | 🔒 | 🔒 | **No** |
| **Técnico** | **Precio** | 🔒 | 🔒 | 🔒 | 🔒 | **No** |
| **Benchmark y alfa** | **Precio** + índice | 🔒 | 🔒 | 🔒 | 🔒 | **No** |
| Iniciados | Regulador | ✅ | ⚠️ | ✅ | 🔒 | **Sí** |
| Posiciones cortas | Regulador | ✅ | ✅ | ❌ | ❌ | **Sí** (US y ES) |
| Hechos relevantes | Regulador | ✅ | ✅ | ✅ | ⚠️ | **Sí** |
| Noticias y tono | GDELT | ✅ | ✅ | ✅ | ✅ | **Sí** |
| Macro | BM / BCE / FRED | ✅ | ✅ | ✅ | ✅ | **Sí** |
| Divisa | BCE | ✅ | ✅ | ✅ | ✅ | **Sí** |

**Once capas de catorce se encienden a coste cero.** Las tres que no dependen
todas del mismo dato que falta.

---

## Los cuatro scores del §18 contra esta matriz

| Score | Factores que pide el §18 | Disponible a 0 € | Veredicto V1 |
|---|---|---|---|
| **Fundamental** | Growth, Profitability, Balance, Cash Flow, Valuation, Quality | 5 de 6 | ✅ **Se calcula**, sin el factor Valoración y diciéndolo |
| **Technical** | Trend, Momentum, Relative Strength, Volatility, Volume | 0 de 5 | ❌ **No se calcula.** No se enseña un score parcial |
| **Sentiment** | News sentiment, volume, momentum, retail | 3 de 4 | ⚠️ **Se calcula** sin *retail*, y con los límites de GDELT a la vista |
| **Macro** | Rates, Inflation, GDP, Currency, Sector | 4 de 5 | ✅ **Se calcula**; *sector conditions* limitado a materias primas mensuales |
| **Overall** | Combinación de los cuatro | — | ⚠️ Con pesos redistribuidos y **la composición visible en la ficha** |

La decisión de fondo es la misma en los cinco casos y viene del §31: cuando falta
un factor, se recalculan los pesos entre los que quedan, se dice cuáles son, y no
se rellena el hueco con un proxy. Un score que finge estar completo vale menos que
un score que declara de qué está hecho.

Con un matiz que no se puede diluir: **el Technical Score no se publica a 0 €.**
No es que pierda un factor; es que pierde los cinco. Un «Technical Score» sin
precio no es un score incompleto, es un número inventado.

---

## Los huecos, uno por uno

Ordenados por lo que cuesta taparlos.

| # | Hueco | Mercados | Se tapa con | Coste |
|---|---|---|---|---|
| 1 | **Precios y volumen** | los 4 | Licencia EOD comercial | ~20–100 €/mes |
| 2 | **Valoración, técnico, benchmark** | los 4 | Consecuencia directa de #1 | — |
| 3 | **India entera** | 🇮🇳 | La misma licencia de #1, o IR empresa a empresa | incluido / trabajo |
| 4 | **Estados financieros de España** | 🇪🇸 | Pipeline de extracción sobre IPP + IR | ~2 semanas de trabajo |
| 5 | Cortos en Brasil e India | 🇧🇷🇮🇳 | Sin vía localizada | — |
| 6 | Índices y benchmarks | los 4 | Licencia de índices | miles €/mes |
| 7 | Materias primas diarias | los 4 | Pink Sheet es mensual. EIA sin investigar | por investigar |
| 8 | Sentimiento minorista | los 4 | Sin fuente con licencia clara | — |

Los huecos 1, 2 y 3 son **el mismo hueco**. Una sola licencia los cierra los tres.
Esa es la observación que más condiciona la hoja de ruta del producto, y está
desarrollada en [`mvp-data-plan.md`](mvp-data-plan.md).

El hueco 4 es el único que se cierra con trabajo propio en vez de con dinero, y
por eso está planificado para V1.1.

---

## Fuentes citadas

| Fuente | Enlace | Tier | Estado |
|---|---|---|---|
| SEC EDGAR | https://www.sec.gov/search-filings/edgar-application-programming-interfaces | 1 | `PROVISIONAL` |
| FINRA Equity Short Interest | https://www.finra.org/finra-data/browse-catalog/equity-short-interest | 2 | `PROVISIONAL` |
| CNMV | https://www.cnmv.es | 2 | `PROVISIONAL` |
| CVM Dados Abertos | https://dados.cvm.gov.br | 1 | `PROVISIONAL` |
| BCE | https://data.ecb.europa.eu | 1 | `PROVISIONAL` |
| Banco Mundial | https://data.worldbank.org | 1 | `PROVISIONAL` |
| FRED | https://fred.stlouisfed.org | 2 | `PROVISIONAL` |
| GDELT | https://gdeltproject.org | 1 | `PROVISIONAL` |
| B3 | https://www.b3.com.br | 4 | `PROVISIONAL` |
| BME | https://www.bolsasymercados.es | 4 | `PROVISIONAL` |
| NSE | https://www.nseindia.com/static/nse-terms-of-use | 4 | `PROVISIONAL` |
| BSE | https://www.bseindia.com/static/about/website_policy.html | 4 | `PROVISIONAL` |
| Yahoo Finance | https://guce.yahoo.com/terms | 4 | `PROVISIONAL` |
| S&P Dow Jones Indices | https://www.spglobal.com/spdji/en/disclaimers/ | 4 | `PROVISIONAL` |
| FMI | https://www.imf.org/en/about/copyright-and-terms | — | `NEEDS_REVIEW` |
