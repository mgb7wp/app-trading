# Estrategia mixta (fundamental + técnica), multi-mercado

Implementación de la estrategia definida en [`ESTRATEGIA.md`](ESTRATEGIA.md). El
análisis fundamental decide **qué** empresas son candidatas, el técnico decide
**cuándo** entrar y salir, y la gestión del riesgo decide **cuánto** comprar,
sobre un universo de cinco mercados (España, EE. UU., Alemania, India y Brasil)
con el riesgo y la cartera medidos en euros.

`ESTRATEGIA.md` es la fuente de verdad: si el código y el documento no coinciden,
manda el documento. Los puntos donde el documento admite dos lecturas o no llega
están resueltos y explicados en [`SUPUESTOS.md`](SUPUESTOS.md).

> **Esto no es un consejo de inversión.** Los parámetros de `config/reglas.yaml`
> son un punto de partida razonable, no valores optimizados. Un backtest es una
> comprobación de que el código hace lo que dice, no una previsión.

## Instalación

```bash
pip install -e ".[panel,dev]"
```

Python 3.11 o superior.

## Uso

```bash
# 1. Descargar datos y dejarlos en caché
estrategia --proveedor yfinance datos --anos 8

# 2. Ver quién entra en el universo y por qué se cae el resto
estrategia --proveedor yfinance universo --detalle

# 3. Candidatas de la última revisión semanal
estrategia --proveedor yfinance senales

# 4. Backtest sobre el periodo de diseño
estrategia --proveedor yfinance backtest --periodo diseno

# 5. Backtest más análisis de sensibilidad
estrategia --proveedor yfinance validar

# 6. Panel interactivo
streamlit run panel/app.py
```

Todos los comandos aceptan `--proveedor {sintetico,yfinance}`. El informe se
guarda en `datos/resultados/`.

### Sin conexión: el proveedor sintético

`--proveedor sintetico` genera precios, fundamentales y divisas deterministas,
sin tocar la red. Es lo que usan los tests, y sirve para probar la app entera sin
descargar nada:

```bash
estrategia --proveedor sintetico datos --anos 7
estrategia --proveedor sintetico backtest
```

Los datos son inventados y están guionados para forzar los casos interesantes
(un hueco por debajo del stop, un mínimo que lo perfora y recupera, una empresa
que deja de pasar el filtro, un mercado con el régimen apagado). Cualquier
informe generado así va marcado como sintético en la cabecera y en el nombre del
fichero: una curva de capital inventada confundida con una real es un error
barato de evitar y caro de descubrir.

### La foto semanal

El documento pide guardar cada semana una copia de los fundamentales y del tipo
de cambio, para ir construyendo un histórico propio sin sesgo de anticipación.
El comando es idempotente por semana, así que está pensado para programarlo:

```bash
# crontab -e  (lunes a las 8:00)
0 8 * * 1 cd /ruta/al/repo && estrategia --proveedor yfinance foto
```

Cuanto antes empiece, antes habrá datos capturados de verdad en lugar de
reconstruidos.

## Configuración

Todos los parámetros de estrategia viven en `config/`; el código no contiene
valores sueltos.

| Fichero | Qué contiene |
|---|---|
| `reglas.yaml` | Los parámetros de la estrategia. Copia del bloque de `ESTRATEGIA.md` más las claves añadidas en la v0.3, cada una marcada y justificada. |
| `universo.yaml` | Los tickers por mercado. **Lista de partida sin verificar**: revísala la primera vez que descargues datos reales. |
| `impuestos_transaccion.yaml` | Impuesto de transacción por país, con su lado, su vigencia y las listas anuales. **Sin verificar contra la fuente oficial.** |
| `implementacion.yaml` | Tablas técnicas: calendario de cada mercado, ETF de las referencias, mapeo de sectores y pares de divisas. |

Que los parámetros estén en config no es cosmético: es lo que permite que el
análisis de sensibilidad mueva cada uno y vuelva a correr el backtest. Hay tests
que lo comprueban cambiando un valor y verificando que el comportamiento cambia,
que es más fiable que buscar números en el código.

## Arquitectura

```
src/estrategia/
  tipos.py         Estructuras y enumeraciones compartidas. No importa nada del paquete.
  config.py        Carga y valida los cuatro YAML. Único sitio que lee configuración.
  indicadores.py   Medias, ATR de Wilder y momentum, precalculados por valor.
  calendario.py    Sesiones por mercado y corte semanal. Único sitio que habla con exchange_calendars.
  sectores.py      Traduce los sectores del proveedor a las categorías del documento.
  datos/           Proveedores (yfinance y sintético), almacén y vista a fecha.
  universo.py      Liquidez y exclusión de sectores, evaluadas a fecha.
  fundamental.py   Mínimos, trampas de signo, percentiles y puntuación 0-100.
  tecnico.py       Señal técnica y régimen de mercado.
  seleccion.py     Ranking global combinando fundamental y momentum.
  riesgo.py        Número de acciones. Funciones puras.
  salidas.py       Stops y salidas semanales. Funciones puras.
  costes.py        Comisión, deslizamiento e impuestos.
  cartera.py       Estado de la cartera. Contenedor puro, no decide nada.
  ordenes.py       Reparte los huecos libres entre las candidatas.
  backtest.py      El bucle diario. Único módulo con estado mutable entre días.
  metricas.py      CAGR, drawdown, Sharpe, desgloses.
  validacion.py    División diseño/validación y sensibilidad.
  informe.py       Métricas, desgloses y avisos.
  cli.py           Comandos.
panel/app.py       Panel de Streamlit. Solo lee y pinta.
```

Las capas se respetan de arriba abajo y hay un test que lo comprueba recorriendo
los `import`. Sin esa disciplina aparece el ciclo típico de un proyecto así:
`cartera` necesita `riesgo`, que necesita `selección`, que necesita `cartera`.

### Las tres piezas que concentran el riesgo

**Anticipación.** Ningún módulo recibe series completas: recibe una vista
construida con una fecha de corte, que no devuelve nada posterior. El sesgo deja
de ser una regla que recordar y pasa a ser algo que habría que romper a
propósito. La vista además anota la fecha más alta que ha leído, de modo que los
tests afirman no solo que el resultado es correcto, sino que para calcularlo no
se miró ni un día más allá.

**Divisas.** Medias, momentum y ATR se calculan **siempre** sobre el precio en
divisa local; la conversión a euros se aplica solo al valorar la cartera y al
dimensionar el riesgo. Hay un test que dobla el tipo de cambio y comprueba que
los indicadores técnicos no se mueven.

**Calendarios.** No hay calendario global: los festivos no coinciden. Cada
mercado decide con su última sesión anterior al corte semanal y ejecuta en su
primera apertura posterior.

## Tests

```bash
pytest
```

Los de `test_anti_sesgo.py` son los que exige el documento y son la condición de
entrada: si uno falla, los resultados de un backtest no valen nada por buenos que
parezcan. Comprueban que un fundamental sin publicar es invisible, que India usa
su propio retraso de publicación, que truncar el futuro no cambia la decisión,
que la orden se ejecuta en la apertura siguiente, que los indicadores no dependen
de la divisa y que el stop de hoy no se calcula con el cierre de hoy.

## Lo que hay que saber antes de creerse un resultado

Estas no son notas al pie: son las razones por las que un backtest de esta app
dice menos de lo que parece. El informe las repite en cada ejecución.

- **El histórico fundamental es corto.** yfinance da unos cuatro ejercicios. Como
  el crecimiento de ventas a tres años necesita **cuatro** ejercicios publicados,
  ninguna empresa pasa el filtro hasta que se publica el cuarto: del orden de
  tres años y medio desde el inicio de los datos. Ese tramo entra en la
  rentabilidad anualizada como si la estrategia hubiera preferido liquidez, y no
  es eso. Para medir el motor sobre todo el histórico, `fundamental.activo: false`.
- **Los datos fundamentales son reconstruidos, no capturados.** Vienen
  reexpresados a día de hoy, y las reexpresiones no son neutras. El informe
  publica el porcentaje; en la v1 es prácticamente el 100%. El comando `foto`
  existe para ir cambiando eso.
- **Falta lo que dejó de cotizar**, así que hay sesgo de supervivencia, más
  fuerte en emergentes.
- **Los dividendos se reinvierten brutos**; un inversor en euros paga retención
  en origen en EE. UU., India y Brasil.
- **Manda `peso_maximo`, no `riesgo.por_operacion`.** Como el precio de entrada
  se cancela en la fórmula del tamaño, el peso implícito es
  `riesgo × precio / (2 × ATR)`, que supera el tope del 15% siempre que el ATR
  sea menor que un 3,3% del precio: la mayoría de las grandes compañías. El
  riesgo real por operación acaba en un 0,4-0,6% en vez del 1% nominal, y por eso
  el informe distingue riesgo teórico de riesgo efectivo. Si la sensibilidad de
  `riesgo.por_operacion` sale plana, no es robustez: es que el parámetro no
  estaba actuando.
- **La repatriación de capital no está modelada.** La rentabilidad en euros
  supone que convertir y sacar el dinero fue siempre posible al cambio de
  mercado, lo que no ha sido cierto históricamente en algunos emergentes.
- **Es probable que no se alcancen los mínimos de `validacion`** (100 operaciones
  en total, 15 por mercado) con un histórico fundamental tan corto. El informe
  avisa en vez de disimularlo.

## Estado

Todo lo que pide la versión 1 del documento está implementado y probado contra
el proveedor sintético: configuración, universo, filtros fundamental y técnico,
selección, stops por ATR, tamaño de posición, motor de backtest, costes e
impuestos por país, métricas y desgloses, validación con sensibilidad, informe,
CLI y panel.

**No se ha podido ejecutar contra datos reales**: el entorno donde se desarrolló
no tiene salida a Yahoo Finance. El camino de yfinance está escrito y las partes
que se pueden comprobar sin red tienen tests, pero la primera ejecución con
`--proveedor yfinance` en tu máquina es la que dirá si los tickers, los sectores
y los campos de los estados financieros salen como se espera. Es lo primero que
conviene hacer, y lo primero que hay que revisar si algo no cuadra.

Fuera de la versión 1, como dice el documento: entrada por RSI, salida por
tiempo, métricas para bancos y aseguradoras, fiscalidad de plusvalías, cobertura
de divisa y alertas.
