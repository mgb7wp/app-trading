# Licencias de las fuentes de datos

El documento que decide qué puede entrar en un producto de pago y qué no.

---

> ## ⚠️ Léase esto antes que nada
>
> **Ninguna licencia de este documento se ha verificado contra su texto oficial.**
>
> El entorno donde se hizo el research tiene el egreso de red bloqueado por
> política. Comprobado en el momento de escribir esto:
>
> ```
> $ curl -sS https://www.sec.gov/os/webmaster-faq
> curl: (56) CONNECT tunnel failed, response 403
> ```
>
> Lo mismo con `cnmv.es`, `ecb.europa.eu`, `b3.com.br`, `gdeltproject.org` y el
> resto. La búsqueda web sí funciona, y con ella se ha podido **localizar** cada
> término de uso y formarse un hallazgo, pero **no leerlo**.
>
> Por eso cada afirmación de este documento lleva una marca:
>
> | Marca | Significa |
> |---|---|
> | `VERIFICADO` | Alguien ha abierto el enlace y leído la cláusula, con fecha. **Hoy no hay ninguna.** |
> | `PROVISIONAL` | Hallazgo por búsqueda. El enlace oficial está localizado; el texto no se ha leído. |
> | `NO LOCALIZADO` | No se ha encontrado el texto que responde a la pregunta. |
>
> Un `PROVISIONAL` favorable **no es permiso para usar la fuente en producción**.
> Es una hipótesis con un enlace donde comprobarla.
>
> ### Y un caso concreto de por qué esto no es exceso de celo
>
> Durante el research, una búsqueda sobre el copyright de la SEC devolvió un
> texto rotundo que prohibía «strictly» la redistribución de datos de EDGAR. Al
> mirar de dónde salía, resultó venir de los *filings* de una empresa llamada
> **EDGAR Online Inc.** — no de ninguna política de la SEC. Un documento escrito
> sin comprobar la procedencia habría descartado la fuente más importante del
> proyecto por confundir a una empresa con el regulador.
>
> La regla del §32 —documentación oficial sobre cualquier tercero— no es una
> preferencia metodológica. Es lo que separa este documento de una alucinación
> bien maquetada.

---

## Verificación obligatoria antes de cobrar

Esta es la lista corta. Hasta que estas siete líneas estén en `VERIFICADO`, el
producto no debe tener clientes de pago.

| # | Qué verificar | Dónde | Qué pasa si sale mal |
|---|---|---|---|
| 1 | **Que la SEC no restringe la reutilización comercial de EDGAR** | [webmaster FAQ](https://www.sec.gov/about/webmaster-frequently-asked-questions) · [accessing EDGAR data](https://www.sec.gov/search-filings/edgar-search-assistance/accessing-edgar-data) | Se cae el mercado principal. **Es el riesgo mayor del proyecto** |
| 2 | **La nota legal de la CNMV**, no solo la Ley 37/2007 | [notalegal.aspx](https://cnmv.es/portal/utilidades/notalegal.aspx) | Se cae España |
| 3 | **La licencia de cada dataset de CVM**, uno a uno | metadatos en [dados.cvm.gov.br](https://dados.cvm.gov.br/about) | Se cae Brasil, entero o por partes |
| 4 | **El aviso legal del BCE**, texto literal de la condición de cita | [disclaimer](https://www.ecb.europa.eu/services/using-our-site/disclaimer/html/index.en.html) | Se cae la capa de divisas |
| 5 | **Los términos del Banco Mundial** y el formato exacto de atribución | [public licenses](https://datacatalog.worldbank.org/public-licenses) · [terms](https://www.worldbank.org/en/about/legal/terms-of-use-for-datasets) | Se cae la capa macro |
| 6 | **Los términos de GDELT**, literales | [about](https://gdeltproject.org/about.html) | Se cae la capa de noticias |
| 7 | **Los términos de FINRA Data** | [equity short interest](https://www.finra.org/finra-data/browse-catalog/equity-short-interest) | Se cae el short interest de EE. UU. |

Son siete páginas web. Media jornada de trabajo. Y es lo único que separa este
documento de ser una opinión informada.

**Además, y sin urgencia de bloqueo:** resolver la contradicción de los términos
del FMI (§ [FMI](#fmi)), y decidir si Stooq se descarta definitivamente por no
tener términos localizables.

---

## Tabla resumen

Todo el research en una pantalla. El detalle, en las fichas de abajo.

| Fuente | País | Gratis | Uso comercial | Almacenar | Redistribuir | Atribución | Tier | Estado registro |
|---|---|:-:|:-:|:-:|:-:|:-:|:-:|---|
| **SEC EDGAR** | 🇺🇸 | ✅ | ✅¹ | ✅¹ | ✅¹ | no | 1 | `APPROVED_WITH_RESTRICTIONS` |
| **FINRA** | 🇺🇸 | ✅ | ❓ | ❓ | ❓ | ❓ | 2 | `NEEDS_REVIEW` |
| **CNMV** | 🇪🇸 | ✅ | ✅² | ❓ | ❓ | probable | 2 | `APPROVED_WITH_RESTRICTIONS` |
| **CVM** | 🇧🇷 | ✅ | ✅³ | ✅³ | ⚠️³ | ❓ | 1 | `APPROVED_WITH_RESTRICTIONS` |
| **SEBI** | 🇮🇳 | ✅ | ❓ | ❓ | ❓ | ❓ | 3 | `NEEDS_REVIEW` |
| **BCE** | 🌍 | ✅ | ✅ | ✅ | ✅ | **sí** | 1 | `APPROVED_WITH_RESTRICTIONS` |
| **Banco Mundial** | 🌍 | ✅ | ✅ | ✅ | ✅ | **sí, con formato** | 1 | `APPROVED_WITH_RESTRICTIONS` |
| **GDELT** | 🌍 | ✅ | ✅ | ✅ | ✅ | **sí** | 1 | `APPROVED_WITH_RESTRICTIONS` |
| **FRED** | 🇺🇸 | ✅ | ⚠️ por serie | ✅ | ❌ series de terceros | por serie | 2 | `APPROVED_WITH_RESTRICTIONS` |
| **FMI** | 🌍 | ✅ | ⚠️ contradictorio | ❓ | ❓ | sí | — | `NEEDS_REVIEW` |
| **B3** | 🇧🇷 | ✅ver | ❌ | ❌ | ❌ | — | 4 | `REJECTED` |
| **BME** | 🇪🇸 | ✅ver | ❌ | ❌ | ❌ | — | 4 | `REJECTED` |
| **NSE** | 🇮🇳 | ✅ver | ❌ | ❌ | ❌ | — | 4 | `REJECTED` |
| **BSE** | 🇮🇳 | ✅ver | ❌ | ❌ | ❌ | — | 4 | `REJECTED` |
| **Yahoo Finance** | 🌍 | ✅ver | ❌ | ❌ | ❌ | — | 4 | `DEVELOPMENT_ONLY` |
| **Alpha Vantage** | 🌍 | ✅ | ❌ free | ❓ | ❌ | sí | 4 | `REJECTED` |
| **Tiingo** | 🌍 | ✅ | ❌ free | ❓ | ❌ | ❓ | 4 | `REJECTED` |
| **Finnhub** | 🌍 | ✅ | ❌ free | ❓ | ❌ | ❓ | 4 | `REJECTED` |
| **EODHD** | 🌍 | ✅ | ❌ free / ✅ pago | ❓ | ❌ | ❓ | 4→D | `DEVELOPMENT_ONLY` |
| **Marketstack** | 🌍 | ✅ | ❌ free | ❓ | ❌ | ❓ | 4 | `REJECTED` |
| **Stooq** | 🌍 | ✅ | ❓ | ❓ | ❓ | ❓ | 4 | `REJECTED` |
| **S&P DJ Indices** | 🇺🇸 | ❌ | ❌ | ❌ | ❌ | — | 4 | `REJECTED` |

`✅ver` = se puede consultar en la web; no se puede usar más allá de eso.

¹ Ninguna restricción localizada, no una autorización leída. Es el punto 1 de la
verificación obligatoria.
² Por la Ley 37/2007 y la Directiva (UE) 2019/1024. Falta la nota legal propia.
³ **Por dataset, no global.** Los términos del portal remiten al metadato de cada
conjunto.

---

# Fichas

## SEC EDGAR

| | |
|---|---|
| **Términos** | https://www.sec.gov/about/webmaster-frequently-asked-questions |
| | https://www.sec.gov/search-filings/edgar-search-assistance/accessing-edgar-data |
| | https://www.sec.gov/about/developer-resources |
| **Estado** | `PROVISIONAL` |

**Licencia.** No hay documento de licencia como tal. `NO LOCALIZADO`

**Uso comercial.** No se ha localizado ninguna restricción. La SEC describe EDGAR
como documentos públicos que cualquiera puede consultar y descargar gratis.
`PROVISIONAL`

**Almacenamiento.** Sin restricción localizada. `PROVISIONAL`

**Redistribución.** Sin restricción localizada. `PROVISIONAL`

**Atribución.** No exigida explícitamente. `NO LOCALIZADO`

**Restricciones técnicas** (estas sí están localizadas y son concretas):

- **10 peticiones por segundo**, agregadas por IP, independientemente de cuántas
  máquinas se usen.
- **User-agent declarado obligatorio**, con nombre y correo de contacto reales.
- Prohibidos botnets y *crawling* indiscriminado.
- La SEC pide *scripting* eficiente, descargar solo lo necesario y moderar la
  carga, y **se reserva el derecho de limitar la tasa de peticiones** para
  preservar el acceso equitativo.

**Histórico vs tiempo real.** No se han localizado condiciones distintas.
`NO LOCALIZADO`

**Riesgo: 🟡 medio** — no por lo que dicen los términos, sino por lo que no se ha
leído. Es la fuente de la que más depende el producto, así que una sorpresa aquí
sería la peor posible.

**Contexto jurídico, que NO es una conclusión.** 17 U.S.C. §105 excluye del
copyright las obras del gobierno federal de EE. UU. Pero los filings de EDGAR no
los escribe la SEC: los escribe cada empresa, y la excepción del §105 no se les
aplica directamente. Ese matiz es real y no se resuelve con una búsqueda web. Lo
que sí se observa es que el ecosistema entero de proveedores redistribuye filings
de EDGAR sin contrato con la SEC, lo cual es un indicio fuerte, no una prueba.

> Hay una lectura conservadora que además es buena ingeniería: **el producto no
> necesita redistribuir filings.** Necesita leerlos, extraer cifras, calcular
> ratios y publicar sus propios números con enlace al documento original. Los
> hechos numéricos no son obra protegible, y enlazar al original no es
> redistribuirlo. Adoptando esa postura por diseño, el punto 1 de la verificación
> obligatoria deja de ser un riesgo existencial y pasa a ser una comprobación.

**Recomendación:** ⭐ **Tier 1.** `APPROVED_WITH_RESTRICTIONS` con dos condiciones
que van al código, no al criterio de nadie: limitador de 10 req/s y user-agent
obligatorio en el conector, no en la configuración.

---

## FINRA — Equity Short Interest

| | |
|---|---|
| **Términos** | https://www.finra.org/finra-data/browse-catalog/equity-short-interest |
| **Estado** | `PROVISIONAL` en lo gratuito, `NO LOCALIZADO` en todo lo demás |

**Gratis.** Sí. FINRA publica los informes de posiciones cortas que recibe de sus
miembros «free for the broader investing public». `PROVISIONAL`

**Uso comercial, almacenamiento, redistribución, atribución, límites.**
`NO LOCALIZADO` en los cinco. Existe un portal FINRA Data con sus propias
condiciones de uso que no se han localizado.

**Frecuencia.** Bimensual, por la Regla 4560. Las posiciones se reportan antes de
las 18:00 ET del segundo día hábil tras la fecha de liquidación designada.

**Histórico.** 5 años en la rejilla interactiva; el archivo histórico va por
descarga separada. Formatos CSV, JSON y ficheros de texto delimitados por `|`.

**Riesgo: 🟡 medio.** El dato es excelente —es regulatorio, no una estimación— y
tapa un hueco que no tapa nadie más. Pero es la única fuente de la lista corta
donde no se ha localizado **ninguna** condición de uso, y eso no se puede
confundir con que no las haya.

**Recomendación:** Tier 2, `NEEDS_REVIEW`. No entra en producción hasta leer sus
términos. Punto 7 de la verificación obligatoria.

---

## CNMV

| | |
|---|---|
| **Términos** | https://cnmv.es/portal/utilidades/notalegal.aspx |
| | https://www.cnmv.es/portal/quees/proteccion-datos-otros |
| **Marco legal** | Ley 37/2007 · Directiva (UE) 2019/1024 |
| **Estado** | `PROVISIONAL` |

**Uso comercial.** La Ley 37/2007 de reutilización de la información del sector
público **contempla expresamente la reutilización con fines comerciales** y manda
fomentar licencias abiertas con las mínimas restricciones posibles. La Directiva
(UE) 2019/1024 va en la misma dirección, y la CNMV declara cumplirla.
`PROVISIONAL`

**Almacenamiento y redistribución.** Previsiblemente permitidos por lo anterior.
`NO LOCALIZADO`

**Atribución.** Previsiblemente exigida —es lo habitual en reutilización de
información pública española—. `NO LOCALIZADO`

**El matiz que hace falta entender.** La ley marco dice qué debe hacer el sector
público; **no sustituye a las condiciones concretas que publique cada organismo**.
Un organismo puede publicar una licencia específica más restrictiva de lo que
sugiere el marco general, o simplemente no publicar ninguna y dejarlo ambiguo.
Por eso la nota legal de la CNMV es el punto 2 de la verificación obligatoria y
no se puede dar por supuesta desde la ley.

**Datasets también en `datos.gob.es`.** Los conjuntos publicados ahí llevan la
licencia del catálogo nacional, que suele ser más explícita que la web del propio
organismo. Puede ser el camino más rápido para resolver el punto 2.

**Riesgo: 🟡 medio.** El marco legal apunta claramente a favor. Lo que falta es la
confirmación del organismo.

**Recomendación:** Tier 2, `APPROVED_WITH_RESTRICTIONS`, con atribución a la CNMV
por defecto en todo lo que se publique a partir de sus datos. Poner la atribución
desde el principio cuesta cero y evita rehacer el frontal si resulta obligatoria.

---

## CVM — Portal de Dados Abertos

| | |
|---|---|
| **Términos** | https://dados.cvm.gov.br/about |
| **Marco legal** | Lei de Acesso à Informação · Política de Dados Abertos do Poder Executivo Federal |
| **Estado** | `PROVISIONAL` |

**Uso comercial.** El portal se describe como repositorio de datos públicos
generados o custodiados por la CVM, publicados para promover la transparencia y
permitir «livre acesso a dados públicos de forma não discriminatória». No se ha
localizado ninguna exclusión del uso comercial. `PROVISIONAL`

**Almacenamiento.** Previsiblemente permitido. `NO LOCALIZADO`

> ### ⚠️ **Redistribución: la licencia es por dataset, no global**
>
> Los términos del portal dicen que el usuario debe comprobar **«no metadado de
> cada conjunto de dados, as licenças sobre condições adicionais»**, y añaden que
> esas condiciones pueden ser actualizadas, corregidas o sustituidas **en
> cualquier momento**.
>
> Esto tiene dos consecuencias prácticas, y ninguna es teórica:
>
> 1. **No existe una respuesta única para «¿se puede usar CVM?».** Hay que
>    comprobar `cia_aberta-doc-dfp`, `-itr`, `-fre`, `-vlmo` y `-fca` por
>    separado. Es el punto 3 de la verificación obligatoria.
> 2. **La comprobación caduca.** El registro de fuentes lleva `last_verified` por
>    algo; para CVM, además, conviene releer los metadatos de cada dataset en cada
>    ingesta y avisar si cambian. Eso es una línea de código en el conector y
>    ahorra descubrir un cambio de licencia por la vía cara.

**Obligaciones del usuario localizadas.** Cumplir la legislación vigente, no
interferir en el funcionamiento normal del portal y no usarlo con fines ilícitos.
Son condiciones de comportamiento, no de licencia de contenido.

**Frecuencia.** Semanal para ITR y DFP. La CVM ha publicado su Plan de Datos
Abiertos 2026-2028, lo que indica continuidad institucional.

**Riesgo: 🟢 bajo-medio.** Es un portal de datos abiertos de un regulador federal
integrado con el Portal Brasileiro de Dados Abertos: el contexto es muy favorable.
El riesgo no es que prohíba, es que una condición particular de un dataset
concreto pase desapercibida.

**Recomendación:** ⭐ Tier 1, `APPROVED_WITH_RESTRICTIONS`, con la comprobación de
licencia por dataset automatizada dentro del conector.

---

## SEBI e India

| | |
|---|---|
| **SEBI** | https://www.sebi.gov.in/filings.html |
| **NSE** | https://www.nseindia.com/static/nse-terms-of-use · [data policy](https://www.nseindia.com/static/market-data/nse-data-policy) · [dotex](https://dotexdata.nseindia.com/TermsAndConditions/TermsofUse.pdf) |
| **BSE** | https://www.bseindia.com/static/about/website_policy.html · [market data products](https://www.bseindia.com/market_data_products.html) |
| **Estado** | `PROVISIONAL` |

**SEBI.** Publica documentos (DRHP, RHP, SAST, recompras, órdenes) pero **no se ha
localizado ningún portal de datos abiertos estructurado** equivalente a EDGAR o a
dados.cvm.gov.br. `PROVISIONAL`

**NSE.** Prohíbe expresamente toda recolección sistemática o automatizada
—*scraping*, *data mining*, *data extraction*, *data harvesting*— sin
consentimiento escrito expreso. El market data con fines comerciales debe
proveerlo NSE Data a un precio aprobado por su Consejo. Los términos advierten de
acciones legales por uso no autorizado. `PROVISIONAL`

**BSE.** Uso «personal, non-commercial or educational» con atribución completa.
Los productos comerciales de market data son de pago; la distribución
internacional va vía Deutsche Börse desde 2013. Jurisdicción: leyes de India,
tribunales de Bombay. `PROVISIONAL`

**El problema estructural de India, dicho claro.** Las divulgaciones de iniciados
(PIT 2015), las de participaciones significativas (SAST 2011), los patrones
accionariales y los resultados **son información regulatoriamente obligatoria**,
pero el regulador no las publica en abierto: las publican las bolsas. Y las
bolsas prohíben recolectarlas automáticamente.

Es decir: no es un obstáculo técnico que se resuelva con un conector mejor. El
único canal de distribución del dato público indio es un canal que prohíbe
consumirlo como lo necesitamos.

**Riesgo: 🔴 alto.** NSE menciona acciones legales de forma explícita, y la
jurisdicción es india.

**Recomendación:** ❌ **Tier 4 — NO APTA PARA PRODUCCIÓN COMERCIAL** para NSE y
BSE. SEBI queda en Tier 3 para documentos puntuales. **India fuera de V1.** Las
tres puertas de entrada posibles, en
[`data-sources.md`](data-sources.md#nse-y-bse).

---

## B3

| | |
|---|---|
| **Términos** | https://www.b3.com.br/pt_br/termos-de-uso-e-protecao-de-dados/termos-de-uso/ |
| | Política de Consumo de Market Data · Política Comercial de Market Data (PDF en b3.com.br) |
| **Estado** | `PROVISIONAL` |

**Uso comercial, almacenamiento y redistribución: ❌ los tres.** El usuario final
no puede distribuir, redistribuir, transferir, transmitir, retransmitir,
licenciar, sublicenciar, arrendar, vender, revender, recircular, **reformatear ni
publicar** market data. La condición de distribuidor o redistribuidor exige
contrato firmado con B3. `PROVISIONAL`

**Esa lista es deliberadamente larga.** «Reformatear» está ahí a propósito:
cierra el argumento de que transformar el dato lo convierte en otra cosa.

**⚠️ Vigencia.** Hay una Política Comercial de Market Data **nueva desde el
01/01/2026**. Cualquier análisis, artículo o respuesta de foro anterior a esa
fecha está caducado, incluido lo que diga la mitad de internet.

**Riesgo: 🔴 alto** si se usara. **🟢 nulo** como está, porque no se usa.

**Recomendación:** ❌ **Tier 4 — NO APTA PARA PRODUCCIÓN COMERCIAL.** `REJECTED`.

**Y no hace falta.** Es el hallazgo de arquitectura más limpio del research: casi
todo lo que el Public Data Hub de B3 ofrece de fundamentales lo publica también la
CVM, y la CVM no lo prohíbe. La separación *public data* / *licensed market data*
que pedía el §4 se resuelve por la vía más simple: **no tocar B3**.

---

## BME

| | |
|---|---|
| **Términos** | https://www.bolsasymercados.es/ |
| **Contacto de licencias** | marketdata@grupobme.es |
| **Estado** | `PROVISIONAL` |

La información de las webs de BME es de **uso interno exclusivamente**. Cualquier
otro uso comercial o redistribución a terceros exige **autorización previa y
expresa de BME Market Data**. BME pertenece al grupo SIX. `PROVISIONAL`

El IBEX 35 es producto de BME/SIX: no hay camino gratuito al benchmark español.

**Riesgo: 🔴 alto** si se usara. **Recomendación:** ❌ Tier 4. `REJECTED`.

---

## Yahoo Finance / yfinance

| | |
|---|---|
| **Términos** | https://guce.yahoo.com/terms |
| | https://legal.yahoo.com/us/en/yahoo/finance-guidelines/index.html |
| | https://help.yahoo.com/kb/SLN2310.html |
| **Estado** | `PROVISIONAL` |

**Redistribución: ❌.** «You must not redistribute information displayed on or
provided by Yahoo Finance.» `PROVISIONAL`

**Uso comercial: ❌.** Prohibido reproducir, modificar, alquilar, vender,
distribuir, transmitir, emitir, crear obra derivada o **explotar con fines
comerciales** sin permiso escrito. `PROVISIONAL`

**Acceso automatizado: ❌** sin permiso escrito. `PROVISIONAL`

**Licencia concedida:** personal, no transferible, revocable y no exclusiva.
`PROVISIONAL`

> ### 🔑 `yfinance` es Apache-2.0. Eso licencia el cliente, no el contenido.
>
> Es la confusión más extendida del sector y conviene dejarla resuelta.
>
> La librería `yfinance` es software libre y puede usarse comercialmente sin
> ningún problema. **Los datos que devuelve no son suyos.** Son de Yahoo y de sus
> proveedores de mercado, y se rigen por los términos de arriba.
>
> Que `pip install yfinance` no pida nada, no tenga clave y no muestre un aviso
> no dice absolutamente nada sobre el derecho a usar esos datos en un producto de
> pago.

> ### La otra confusión: «si el dato no sale, no hace falta licencia»
>
> Durante el research apareció esta idea, y es atractiva: si el precio es una
> entrada interna y lo que se publica es un score, ¿hace falta licencia?
>
> **Para Yahoo, no salva nada.** La licencia concedida es *personal y no
> comercial*. Usar esos datos dentro de un producto de pago incumple los
> términos aunque el dato no salga nunca del servidor. No hay lectura de
> «entrada interna» que convierta una licencia personal en una comercial.
>
> **Para el precio de la licencia, sí cambia mucho.** Una licencia de *uso
> derivado sin redistribución* cuesta decenas de euros al mes. Una de
> *redistribución* cuesta miles y exige contrato con cada bolsa. Que el producto
> no publique la serie OHLCV no elimina la necesidad de licenciar: la abarata uno
> o dos órdenes de magnitud. Eso es lo que hace viable el plan de
> [`mvp-data-plan.md`](mvp-data-plan.md).

**Riesgo: 🔴 alto.** Y no es abstracto: era la fuente de precios del sistema
anterior de este repositorio.

**Recomendación:** ❌ **Tier 4 en producción.** Estado en el registro:
`DEVELOPMENT_ONLY`, lo que significa que **el arranque en producción falla** si
alguien la configura. Se conserva para desarrollo y tests, con la reserva honesta
de que los términos tampoco amparan claramente el acceso automatizado durante el
prototipado.

---

## Agregadores gratuitos de precios

Todos coinciden en lo mismo: la capa gratuita es no comercial, y el uso comercial
está detrás del plan de pago. Ninguno es una excepción.

| Fuente | Capa gratuita | Términos |
|---|---|---|
| **Alpha Vantage** | Atribución obligatoria, **sin reventa**. Redistribución comercial y datos licenciados de bolsa exigen licencia aparte | alphavantage.co/terms_of_service |
| **Tiingo** | Prohíbe expresamente reventa y redistribución | tiingo.com/about/pricing |
| **Finnhub** | Licencia no comercial. En cuanto la app se monetiza o redistribuye datos, hace falta plan de pago | finnhub.io/terms-of-service |
| **EODHD** | 20 llamadas/día, último año, solo EE. UU. Comercial → plan de pago | eodhd.com/financial-apis/terms |
| **Marketstack** | 100 peticiones al **mes**, 1 año de histórico | marketstack.com/terms |
| **Stooq** | **Sin términos localizables.** Cuota diaria baja («Exceeded the daily hits limit») | — |

Todos `PROVISIONAL`. **Recomendación:** ❌ Tier 4 en capa gratuita, `REJECTED`.

**Stooq merece una mención aparte**, porque es la trampa más fácil de este
research: gratis, sin clave, con histórico de varios mercados y sin nadie que te
diga que no. Pero **no tener términos localizables no es lo mismo que no tener
restricciones**: es no saber. Y el §MUY IMPORTANTE del encargo dice exactamente
que no se asuma. `REJECTED` por ausencia de información, no por prohibición.

**EODHD, en cambio, es la candidata natural del Tier D.** Su plan de pago sí
contempla uso comercial, cubre los cuatro mercados incluida India, y este
repositorio **ya tiene el adaptador escrito y probado contra respuestas
grabadas**. Es el camino más corto desde 0 € hasta el producto completo.

---

## Banco Central Europeo

| | |
|---|---|
| **Términos** | https://www.ecb.europa.eu/services/using-our-site/disclaimer/html/index.en.html |
| **Datos** | https://data.ecb.europa.eu/ |
| **Estado** | `PROVISIONAL` |

**Uso comercial: ✅.** «All publicly available ESCB statistics may be reused **free
of charge** on the condition that the source is quoted.» La reutilización
comercial está permitida. `PROVISIONAL`

**Almacenamiento: ✅.** **Redistribución: ✅**, con dos condiciones: citar la fuente
y **no modificar los datos, metadatos incluidos**. `PROVISIONAL`

**Atribución: obligatoria.**

**Qué cubre.** Tipos de cambio de referencia del euro, ~16:00 CET cada día hábil
TARGET, 29 divisas. **BRL e INR están entre ellas**, así que EUR/USD, EUR/BRL y
EUR/INR salen directos y USD/BRL y USD/INR por cruce. Cubre el §8 entero.

**Dos cautelas técnicas**, que no son de licencia pero condicionan lo que se puede
afirmar con estos datos:

- Es un **tipo de referencia**, una foto de las 16:00 CET, no un tipo de mercado.
  Sirve para comparar rendimientos; no para valorar una operación.
- El calendario es **TARGET**, no el de cada bolsa. Un día hábil en Bombay puede
  no tener tipo publicado. La regla —último disponible, nunca interpolar hacia
  adelante— va codificada y con test, no en la cabeza de nadie.

**La condición de «no modificar» merece un párrafo.** Guardar el tipo tal cual y
citar al BCE es correcto. Calcular un cruce USD/BRL a partir de EUR/USD y EUR/BRL
produce **un dato nuestro**, y así debe etiquetarse: «calculado por La Lonja a
partir de tipos de referencia del BCE». Presentar un cruce derivado como si fuera
un tipo publicado por el BCE sí sería alterar el dato. La distinción es barata de
implementar —un campo `derivado: true`— y evita el único incumplimiento plausible
de esta licencia.

**Riesgo: 🟢 bajo.** **Recomendación:** ⭐ Tier 1, `APPROVED_WITH_RESTRICTIONS`
(la restricción es citar y no alterar).

---

## Banco Mundial

| | |
|---|---|
| **Términos** | https://datacatalog.worldbank.org/public-licenses |
| | https://data.worldbank.org/summary-terms-of-use |
| | https://www.worldbank.org/en/about/legal/terms-of-use-for-datasets |
| **Licencia** | **CC BY 4.0** + términos adicionales |
| **Estado** | `PROVISIONAL` |

**Uso comercial: ✅.** CC BY 4.0 permite copiar, modificar y distribuir **para
cualquier fin, incluido el comercial**. `PROVISIONAL`

**Almacenamiento y redistribución: ✅**, con atribución. `PROVISIONAL`

**Atribución: obligatoria y con formato.** `The World Bank: Dataset name: Data
source`. Y hay obligación de **propagar la atribución a sublicenciatarios**: quien
reciba los datos a través de nuestro producto debe seguir viendo de dónde salen.
Eso condiciona el diseño del frontal y de la API, no solo un pie de página.

> **⚠️ La trampa del catálogo.** El Banco Mundial aloja datasets de terceros
> dentro de su propio catálogo, y esos **pueden no ser redistribuibles**. La
> licencia CC BY 4.0 cubre lo que publica el Banco Mundial, no todo lo que hay en
> su web. Hay que comprobar por dataset, igual que en CVM y en FRED.

**Materias primas.** El **Pink Sheet** ([commodity
markets](https://www.worldbank.org/en/research/commodity-markets)) da Brent,
cobre LME y oro entre otros, en Excel y PDF, **mensual**, y hereda esta licencia.
Mensual no es diario: sobra para contexto sectorial y no llega para una serie de
Brent.

**Riesgo: 🟢 bajo.** CC BY 4.0 es una licencia conocida y sin sorpresas.

**Recomendación:** ⭐ Tier 1, `APPROVED_WITH_RESTRICTIONS` (atribución con formato
y propagación).

---

## FRED

| | |
|---|---|
| **Términos** | https://fred.stlouisfed.org/docs/api/terms_of_use.html |
| | https://fred.stlouisfed.org/legal |
| **Estado** | `PROVISIONAL` |

**Gratis: ✅.** FRED no cobra ni contabiliza el consumo. Clave de API gratuita.

**Uso comercial: ⚠️ depende de la serie.** **Redistribuir comercialmente series
con copyright NO está permitido** sin autorización del titular del copyright.
`PROVISIONAL`

> ### FRED no es una fuente: es un agregador
>
> Es la trampa que el §7 pedía documentar, y es completamente real.
>
> Las series propias de la Reserva Federal y de las agencias federales —tipos,
> agregados monetarios, empleo del BLS, cuentas nacionales del BEA— no están en el
> mismo régimen que las series licenciadas de terceros: S&P/Case-Shiller, NAHB,
> ICE, Haver y otras. Cada serie arrastra las obligaciones de **su titular**, y
> FRED lo indica en la nota de fuente de cada una.
>
> **Traducción a ingeniería:** el conector de FRED no debe aceptar un `series_id`
> arbitrario. Debe llevar una **lista blanca de series aprobadas**, cada una con
> su titular y su estado de verificación anotados en `config/fuentes.yaml`.
> Cualquier otro diseño convierte «hay que comprobar la serie» en «alguien se
> acordará», y nadie se acuerda.

**Riesgo: 🟡 medio**, y enteramente controlable con la lista blanca.

**Recomendación:** Tier 2, `APPROVED_WITH_RESTRICTIONS` con lista blanca
obligatoria.

---

## GDELT

| | |
|---|---|
| **Términos** | https://gdeltproject.org/about.html · https://registry.opendata.aws/gdelt/ |
| **Estado** | `PROVISIONAL` |

**Uso comercial: ✅.** «Unlimited and unrestricted use for any **academic,
commercial, or governmental** use of any kind **without fee**.» `PROVISIONAL`

**Almacenamiento: ✅.** **Redistribución: ✅.** «You may **redistribute, rehost,
republish, and mirror** any of the GDELT datasets.» `PROVISIONAL`

**Atribución: obligatoria** — citar «The GDELT Project» con enlace a
gdeltproject.org.

**Es la licencia más permisiva de todo el research**, con diferencia y sin
competencia cercana.

**Riesgo de licencia: 🟢 bajo. Riesgo de calidad: 🟡 medio**, y hay que decirlo con
la misma claridad:

- **La resolución por empresa es aproximada.** GDELT indexa entidades por nombre,
  no por ticker ni CIK. «Apple» aparece en artículos que no hablan de Apple Inc.,
  y una cotizada española mediana puede no aparecer casi nunca. Hace falta una
  capa de desambiguación propia, y hay que **medir su precisión antes de publicar
  el número**.
- **El tono no es sentimiento financiero.** Es un promedio léxico sobre el
  artículo completo. Sirve como serie relativa —el tono de una empresa contra su
  propia media— y no como afirmación absoluta sobre si una noticia es buena.

Ambas limitaciones van en la ficha del producto, no en una nota al pie. El §31
pide 100 métricas fiables antes que 10.000 dudosas, y una métrica de sentimiento
presentada sin sus límites es exactamente una de las dudosas.

**Recomendación:** ⭐ Tier 1, `APPROVED_WITH_RESTRICTIONS` (atribución).

---

## FMI

| | |
|---|---|
| **Términos** | https://www.imf.org/en/about/copyright-and-terms |
| **API** | https://api.imf.org/external/sdmx/3.0 (SDMX 3.0 — IFS, WEO, FM, GFS, MFS, BOP) |
| **Estado** | ⚠️ `NEEDS_REVIEW` |

Aquí hay tres cláusulas y no está claro cuál manda:

1. **Regla general:** descarga no sistemática, **uso personal no comercial**, sin
   derecho a revender, redistribuir, compilar ni crear obras derivadas.
2. **Términos especiales para datos estadísticos publicados**, que según los
   hallazgos **anulan expresamente** la prohibición general y permiten
   «download, extract, copy, create derivative works, publish, distribute and
   use», con atribución y respeto a la integridad del dato.
3. **Y luego:** «For any potential **commercial reuse** of IMF Data, please email
   … to request permission».

`PROVISIONAL` las tres.

La (2) y la (3) se contradicen de forma directa: o los términos especiales
permiten el uso comercial, o hace falta pedir permiso. No se puede resolver sin
leer el texto completo, y **este es precisamente el caso que el encargo pedía no
dar por bueno**.

**Y no hace falta resolverlo para el MVP.** Todo lo que el §7 pide del FMI —PIB,
inflación, deuda, tipos, reservas, comercio— lo da el Banco Mundial bajo CC BY
4.0, que es una licencia limpia y conocida. Lo único realmente exclusivo del FMI
son las **previsiones del WEO**, y un MVP no las necesita.

**Riesgo: 🟡 medio.** **Recomendación:** ⚠️ `NEEDS_REVIEW`. **Fuera de V1.** Se
manda el correo pidiendo permiso en paralelo —cuesta cinco minutos— y se
incorpora si contestan bien. No bloquea nada.

---

## Índices y benchmarks

| | |
|---|---|
| **S&P Dow Jones Indices** | https://www.spglobal.com/spdji/en/disclaimers/ |
| **Estado** | `PROVISIONAL` |

«Redistribution or reproduction in whole or in part are prohibited without written
permission of S&P Dow Jones Indices LLC.» Los datos de índice —niveles,
constituyentes y ponderaciones— van por un acuerdo de licencia de datos aparte,
con tarifas propias. S&P DJI cobra por licenciar sus índices a terceros.
`PROVISIONAL`

Por la misma lógica de negocio, y cada uno con sus propios términos:

| Índice | Titular |
|---|---|
| IBEX 35 | BME / SIX |
| Ibovespa | B3 |
| NIFTY 50 | NSE Indices |
| SENSEX | Asia Index / BSE |

**Riesgo: 🔴 alto** si se usaran. **Recomendación:** ❌ Tier 4, `REJECTED`.

**Consecuencia para el producto.** El §14 pedía rendimiento relativo y alfa contra
el índice. **Sin licencia de precios ni de índices, no se puede**, y no hay atajo:
usar un ETF que replique el índice sustituye un dato licenciado por otro dato
licenciado. Es la razón de que los benchmarks por ETF que tenía este repositorio
—EUNL.DE, IS3N.DE— salgan de la configuración.

---

## Investor Relations y RSS

Sin ficha única: cada emisor y cada medio tiene sus propios términos, y no tiene
sentido investigar doscientos por adelantado. Lo que sí se puede fijar son las
reglas que valen para todos, y que van **dentro del conector**, no en el criterio
de quien lo use:

**Investor Relations.** Los documentos son públicos y **tienen copyright del
emisor**. Se pueden descargar, procesar, extraer cifras y citar con enlace al
original. **No se pueden republicar enteros ni alojar copias públicas.** Los
hechos numéricos que contienen no son obra protegible; su redacción y su
maquetación sí.

**RSS de medios.** Se guardan **titular, medio, fecha, URL y metadatos**. Nunca el
cuerpo del artículo. El resumen lo genera nuestra IA a partir de nuestros
metadatos y del dato estructurado, y **siempre enlaza al original**. Se respeta
`robots.txt` y la cadencia que pida el feed.

**RSS de reguladores.** Categoría aparte y la mejor de todas: CNMV, CVM y SEC
publican sus propias comunicaciones y son fuente primaria, no medio. Heredan la
licencia de su organismo.

**Riesgo: 🟡 medio**, y concentrado en un solo punto: el día que a alguien le
parezca buena idea guardar el texto completo «para que la IA lo resuma mejor». La
regla tiene que estar en el esquema de la base de datos —que no exista una
columna `cuerpo`— y no en la documentación.

**Recomendación:** Tier 2, `APPROVED_WITH_RESTRICTIONS`, con la restricción
impuesta por el modelo de datos.

---

## Cómo se aplica todo esto en el código

Este documento no sirve de nada si hay que acordarse de él. Por eso su contenido
está en `config/fuentes.yaml` con el esquema del §22, y el enrutador —el único
punto por el que pasan todos los datos— lo obedece:

| Estado | Efecto en ejecución |
|---|---|
| `APPROVED` | Se usa en producción |
| `APPROVED_WITH_RESTRICTIONS` | Se usa, y sus condiciones se anotan en cada fila que produce |
| `DEVELOPMENT_ONLY` | Funciona en local. **En producción, el arranque falla** |
| `REJECTED` | No se instancia nunca |
| `NEEDS_REVIEW` | No se instancia nunca |

Con un test que lo demuestra: configurar una fuente `DEVELOPMENT_ONLY` en modo
producción tiene que hacer fallar el arranque, y si alguien rompe esa garantía,
el test se pone rojo.

Así, «no depender accidentalmente de una fuente con problemas de licencia» deja de
ser una intención y pasa a ser imposible por construcción. Y cuando la
verificación primaria cambie un estado en el YAML, el efecto es inmediato en todo
el sistema sin tocar una línea de código.

Cada fuente lleva además `last_verified`. Hoy, **todas están vacías**.
