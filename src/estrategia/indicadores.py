"""Indicadores precalculados, una vez por valor.

La primera version calculaba medias, ATR y momentum dentro del bucle diario,
recorriendo el historico entero en cada consulta. Con 140 valores y seis anos de
sesiones eso es inviable, y ademas hace inutilizables el panel y el analisis de
sensibilidad, que corren el backtest decenas de veces.

Aqui cada serie se recorre una sola vez y se deja todo resuelto en vectores
alineados con las sesiones del valor. El bucle diario pasa a ser una lectura por
indice.

Esto no abre la puerta al sesgo de anticipacion: todos los indicadores son
ventanas hacia atras, asi que la posicion `i` de cada vector solo depende de
datos en posiciones `<= i`. El motor lee la posicion correspondiente a la fecha
de decision y nunca una posterior; el almacen sigue vigilando el corte y los
tests de sesgo lo comprueban recortando la serie y verificando que la decision
no cambia.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

import numpy as np
import pandas as pd

from .config import Config
from .constantes import MESES_POR_ANO


def media_movil_vector(valores: np.ndarray, ventana: int) -> np.ndarray:
    """Media simple movil, con NaN donde aun no hay ventana completa."""
    n = len(valores)
    salida = np.full(n, np.nan)
    if n < ventana or ventana <= 0:
        return salida
    acumulado = np.cumsum(np.insert(valores, 0, 0.0))
    salida[ventana - 1 :] = (acumulado[ventana:] - acumulado[:-ventana]) / ventana
    return salida


def atr_wilder_vector(
    maximos: np.ndarray, minimos: np.ndarray, cierres: np.ndarray, periodo: int
) -> np.ndarray:
    """ATR de Wilder en cada sesion.

    Se siembra con la media simple de los primeros `periodo` rangos verdaderos y
    a partir de ahi se suaviza, que es la definicion original de Wilder. Una
    media movil simple del rango da un numero parecido pero distinto, y como de
    esto dependen los dos stops, la definicion se fija y se comprueba.
    """
    n = len(cierres)
    salida = np.full(n, np.nan)
    if n < periodo + 1:
        return salida

    previo = cierres[:-1]
    rango = np.maximum(
        maximos[1:] - minimos[1:],
        np.maximum(np.abs(maximos[1:] - previo), np.abs(minimos[1:] - previo)),
    )
    atr = float(np.mean(rango[:periodo]))
    salida[periodo] = atr
    for i in range(periodo, len(rango)):
        atr = (atr * (periodo - 1) + float(rango[i])) / periodo
        salida[i + 1] = atr
    return salida


def momentum_vector(
    fechas: np.ndarray, cierres: np.ndarray, meses: int, excluir_meses: int
) -> np.ndarray:
    """Momentum 12-1 en cada sesion.

    Los dos extremos se resuelven "a la fecha": el ultimo cierre disponible en o
    antes del dia objetivo, para que un festivo no invalide el calculo.
    """
    n = len(fechas)
    salida = np.full(n, np.nan)
    if n == 0:
        return salida

    ordinales = np.array([f.toordinal() for f in fechas])
    obj_fin = np.array([_desplazar_meses(f, -excluir_meses).toordinal() for f in fechas])
    obj_ini = np.array([_desplazar_meses(f, -meses).toordinal() for f in fechas])

    # searchsorted 'right' - 1 da el ultimo indice con fecha <= objetivo.
    idx_fin = np.searchsorted(ordinales, obj_fin, side="right") - 1
    idx_ini = np.searchsorted(ordinales, obj_ini, side="right") - 1

    valido = (idx_ini >= 0) & (idx_fin >= 0) & (idx_ini < idx_fin)
    p_ini = np.where(valido, cierres[np.clip(idx_ini, 0, n - 1)], np.nan)
    p_fin = np.where(valido, cierres[np.clip(idx_fin, 0, n - 1)], np.nan)
    with np.errstate(divide="ignore", invalid="ignore"):
        salida = np.where(valido & (p_ini > 0), p_fin / p_ini - 1.0, np.nan)
    return salida


def _desplazar_meses(f: date, meses: int) -> date:
    import calendar

    total = f.year * MESES_POR_ANO + (f.month - 1) + meses
    ano, mes = divmod(total, MESES_POR_ANO)
    dia = min(f.day, calendar.monthrange(ano, mes + 1)[1])
    return date(ano, mes + 1, dia)


@dataclass(slots=True)
class SerieValor:
    """Serie de un valor con sus indicadores ya resueltos."""

    ticker: str
    fechas: np.ndarray
    ordinales: np.ndarray
    apertura: np.ndarray
    maximo: np.ndarray
    minimo: np.ndarray
    cierre: np.ndarray
    cierre_bruto: np.ndarray
    volumen: np.ndarray
    ma_corta: np.ndarray
    ma_larga: np.ndarray
    ma_regimen: np.ndarray
    atr: np.ndarray
    momentum: np.ndarray

    def posicion(self, fecha: date) -> int:
        """Indice de la ultima sesion en o antes de `fecha`; -1 si no hay."""
        return int(np.searchsorted(self.ordinales, fecha.toordinal(), side="right")) - 1

    def posicion_exacta(self, fecha: date) -> int:
        """Indice de esa sesion concreta, o -1 si el valor no cotizo ese dia."""
        i = self.posicion(fecha)
        if i < 0 or self.fechas[i] != fecha:
            return -1
        return i


def construir_series(precios: pd.DataFrame, cfg: Config) -> dict[str, SerieValor]:
    """Calcula los indicadores de todos los valores de una sola pasada."""
    tec = cfg.reglas.tecnico
    series: dict[str, SerieValor] = {}
    if precios.empty:
        return series

    for ticker, grupo in precios.groupby("ticker", sort=False):
        g = grupo.sort_values("fecha")
        fechas = g["fecha"].to_numpy()
        cierre = g["cierre"].to_numpy(dtype=float)
        maximo = g["maximo"].to_numpy(dtype=float)
        minimo = g["minimo"].to_numpy(dtype=float)

        series[str(ticker)] = SerieValor(
            ticker=str(ticker),
            fechas=fechas,
            ordinales=np.array([f.toordinal() for f in fechas]),
            apertura=g["apertura"].to_numpy(dtype=float),
            maximo=maximo,
            minimo=minimo,
            cierre=cierre,
            cierre_bruto=g["cierre_bruto"].to_numpy(dtype=float),
            volumen=g["volumen"].to_numpy(dtype=float),
            ma_corta=media_movil_vector(cierre, tec.media_corta),
            ma_larga=media_movil_vector(cierre, tec.media_larga),
            ma_regimen=media_movil_vector(cierre, tec.regimen_mercado_media),
            atr=atr_wilder_vector(maximo, minimo, cierre, tec.atr_periodo),
            momentum=momentum_vector(
                fechas, cierre, tec.momentum_meses, tec.momentum_excluir_meses
            ),
        )
    return series


@dataclass(slots=True)
class SerieFX:
    """Tipos de cambio de una divisa, indexados por dia natural."""

    divisa: str
    ordinales: np.ndarray
    tasas: np.ndarray

    def tasa_en(self, fecha: date) -> float | None:
        """Ultima tasa conocida en o antes de esa fecha."""
        i = int(np.searchsorted(self.ordinales, fecha.toordinal(), side="right")) - 1
        return None if i < 0 else float(self.tasas[i])


def construir_fx(fx: pd.DataFrame) -> dict[str, SerieFX]:
    series: dict[str, SerieFX] = {}
    if fx.empty:
        return series
    for divisa, grupo in fx.groupby("divisa", sort=False):
        g = grupo.sort_values("fecha")
        series[str(divisa)] = SerieFX(
            divisa=str(divisa),
            ordinales=np.array([f.toordinal() for f in g["fecha"]]),
            tasas=g["tasa"].to_numpy(dtype=float),
        )
    return series


# --------------------------------------------------------------------------
# El resto de indicadores del §16
# --------------------------------------------------------------------------
#
# Todos son funciones puras sobre OHLCV y todos son causales: la posicion `i` de
# cada vector solo depende de datos en posiciones `<= i`. Eso no es un detalle de
# estilo, es lo que permite leerlos por indice desde una vista con fecha de corte
# sin abrir la puerta al sesgo de anticipacion, y hay un test que lo comprueba
# recortando la serie y verificando que el prefijo no cambia.
#
# Ninguno de estos se puede alimentar hoy: no hay fuente de precios con licencia
# para uso comercial en los cuatro mercados (ver docs/data-licensing.md). Estan
# escritos y probados para que el dia que haya licencia la capa tecnica funcione,
# y para que la afirmacion "el codigo esta, lo que falta es el derecho a
# alimentarlo" sea cierta y no una forma de hablar.
#
# Donde hay dos definiciones en circulacion se elige una, se dice cual y se
# comprueba. Un RSI suavizado a lo Wilder y uno con media simple dan numeros
# parecidos y distintos, y "parecido" no sirve cuando de ahi sale una decision.


def _rma(valores: np.ndarray, periodo: int) -> np.ndarray:
    """Suavizado de Wilder: se siembra con la media simple y luego se arrastra.

    Es el mismo suavizado que usa `atr_wilder_vector`, extraido aqui porque el
    RSI necesita exactamente el mismo. Tenerlo en un solo sitio evita que los dos
    indicadores se separen si alguien retoca uno.
    """
    n = len(valores)
    salida = np.full(n, np.nan)
    if n < periodo or periodo <= 0:
        return salida
    salida[periodo - 1] = float(np.mean(valores[:periodo]))
    for i in range(periodo, n):
        salida[i] = (salida[i - 1] * (periodo - 1) + valores[i]) / periodo
    return salida


def ema_vector(valores: np.ndarray, periodo: int) -> np.ndarray:
    """Media exponencial, sembrada con la media simple de las primeras `periodo`.

    Sembrar con el primer valor en vez de con la media simple es mas comun en
    codigo de ejemplo y arrastra un sesgo que tarda varias ventanas en diluirse.
    Con esta siembra, el primer valor no nulo coincide con el de la media simple,
    que es lo que espera cualquiera que compare con un grafico.
    """
    n = len(valores)
    salida = np.full(n, np.nan)
    if n < periodo or periodo <= 0:
        return salida
    alfa = 2.0 / (periodo + 1.0)
    salida[periodo - 1] = float(np.mean(valores[:periodo]))
    for i in range(periodo, n):
        salida[i] = alfa * valores[i] + (1.0 - alfa) * salida[i - 1]
    return salida


def rsi_vector(cierres: np.ndarray, periodo: int = 14) -> np.ndarray:
    """RSI de Wilder, en 0-100.

    Dos casos extremos que hay que decidir a proposito, porque la formula se
    divide por la perdida media:

    - **Sin perdidas en la ventana**: RSI = 100. No es una convencion comoda, es
      el limite de la formula cuando la perdida media tiende a cero.
    - **Sin ganancias**: RSI = 0, por el mismo motivo.

    Dejar que salga un NaN o un 50 en esos casos seria peor: un valor que lleva
    catorce sesiones subiendo sin un solo dia rojo es justo el que interesa, y es
    el que desapareceria del ranking.
    """
    n = len(cierres)
    salida = np.full(n, np.nan)
    if n < periodo + 1 or periodo <= 0:
        return salida

    cambio = np.diff(cierres)
    ganancia = _rma(np.where(cambio > 0, cambio, 0.0), periodo)
    perdida = _rma(np.where(cambio < 0, -cambio, 0.0), periodo)

    # `diff` acorta en uno: la posicion j de `cambio` es la sesion j+1.
    for j in range(len(cambio)):
        g, p = ganancia[j], perdida[j]
        if np.isnan(g) or np.isnan(p):
            continue
        if p == 0.0:
            salida[j + 1] = 100.0 if g > 0.0 else 50.0
        elif g == 0.0:
            salida[j + 1] = 0.0
        else:
            salida[j + 1] = 100.0 - 100.0 / (1.0 + g / p)
    return salida


def macd_vector(
    cierres: np.ndarray, rapida: int = 12, lenta: int = 26, senal: int = 9
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """MACD, su linea de senal y el histograma.

    La linea de senal es la EMA del MACD, **no** la EMA del precio: se calcula
    sobre el tramo del MACD que ya tiene valor, y las posiciones anteriores
    quedan a NaN. Calcularla sobre el vector entero con los NaN dentro los
    propaga y deja la senal inutilizable justo cuando empieza a haber datos.
    """
    macd = ema_vector(cierres, rapida) - ema_vector(cierres, lenta)
    linea = np.full(len(cierres), np.nan)
    validos = np.flatnonzero(~np.isnan(macd))
    if len(validos):
        desde = validos[0]
        linea[desde:] = ema_vector(macd[desde:], senal)
    return macd, linea, macd - linea


def roc_vector(valores: np.ndarray, periodo: int) -> np.ndarray:
    """Tasa de cambio en tanto por uno sobre `periodo` sesiones."""
    n = len(valores)
    salida = np.full(n, np.nan)
    if n <= periodo or periodo <= 0:
        return salida
    previo = valores[:-periodo]
    with np.errstate(divide="ignore", invalid="ignore"):
        salida[periodo:] = np.where(previo > 0, valores[periodo:] / previo - 1.0, np.nan)
    return salida


def estocastico_vector(
    maximos: np.ndarray,
    minimos: np.ndarray,
    cierres: np.ndarray,
    periodo: int = 14,
    suavizado: int = 3,
) -> tuple[np.ndarray, np.ndarray]:
    """%K y %D del oscilador estocastico, en 0-100.

    Si en la ventana el maximo y el minimo coinciden —un valor que no se ha
    movido en `periodo` sesiones— el denominador es cero y el resultado es NaN,
    no 50. Un 50 diria "ni sobrecomprado ni sobrevendido", que es una afirmacion;
    NaN dice "no hay dato", que es la verdad.
    """
    n = len(cierres)
    k = np.full(n, np.nan)
    if n < periodo or periodo <= 0:
        return k, np.full(n, np.nan)

    for i in range(periodo - 1, n):
        alto = float(np.max(maximos[i - periodo + 1 : i + 1]))
        bajo = float(np.min(minimos[i - periodo + 1 : i + 1]))
        if alto > bajo:
            k[i] = 100.0 * (cierres[i] - bajo) / (alto - bajo)

    d = np.full(n, np.nan)
    validos = np.flatnonzero(~np.isnan(k))
    if len(validos):
        desde = validos[0]
        d[desde:] = media_movil_vector(k[desde:], suavizado)
    return k, d


def bollinger_vector(
    cierres: np.ndarray, ventana: int = 20, desviaciones: float = 2.0
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Banda central, superior, inferior y anchura relativa.

    La desviacion es poblacional (`ddof=0`), que es la definicion de Bollinger.
    Con la muestral las bandas salen algo mas anchas, y la diferencia importa
    justo en las ventanas cortas.

    La anchura va en tanto por uno sobre la banda central, para que se pueda
    comparar entre valores con precios de escalas distintas.
    """
    n = len(cierres)
    vacio = np.full(n, np.nan)
    if n < ventana or ventana <= 0:
        return vacio.copy(), vacio.copy(), vacio.copy(), vacio.copy()

    centro = media_movil_vector(cierres, ventana)
    sigma = np.full(n, np.nan)
    for i in range(ventana - 1, n):
        sigma[i] = float(np.std(cierres[i - ventana + 1 : i + 1]))

    superior = centro + desviaciones * sigma
    inferior = centro - desviaciones * sigma
    with np.errstate(divide="ignore", invalid="ignore"):
        anchura = np.where(centro > 0, (superior - inferior) / centro, np.nan)
    return centro, superior, inferior, anchura


def volatilidad_historica_vector(
    cierres: np.ndarray, ventana: int = 20, sesiones_ano: int = 252
) -> np.ndarray:
    """Volatilidad anualizada de los rendimientos logaritmicos.

    Logaritmicos y no simples: se suman entre periodos, que es lo que hace valida
    la anualizacion por raiz del numero de sesiones.
    """
    n = len(cierres)
    salida = np.full(n, np.nan)
    if n <= ventana or ventana <= 1:
        return salida

    with np.errstate(divide="ignore", invalid="ignore"):
        rend = np.diff(np.log(np.where(cierres > 0, cierres, np.nan)))
    factor = np.sqrt(sesiones_ano)
    for j in range(ventana - 1, len(rend)):
        trozo = rend[j - ventana + 1 : j + 1]
        if np.isnan(trozo).any():
            continue
        salida[j + 1] = float(np.std(trozo, ddof=1)) * factor
    return salida


def obv_vector(cierres: np.ndarray, volumenes: np.ndarray) -> np.ndarray:
    """On-Balance Volume acumulado, empezando en cero.

    El nivel absoluto no significa nada —depende de donde se empiece a contar—;
    lo que se lee es su pendiente y su divergencia con el precio. Por eso arranca
    en cero y no en el volumen de la primera sesion.
    """
    n = len(cierres)
    salida = np.zeros(n)
    if n == 0:
        return salida
    for i in range(1, n):
        if cierres[i] > cierres[i - 1]:
            salida[i] = salida[i - 1] + volumenes[i]
        elif cierres[i] < cierres[i - 1]:
            salida[i] = salida[i - 1] - volumenes[i]
        else:
            salida[i] = salida[i - 1]
    return salida


def volumen_relativo_vector(volumenes: np.ndarray, ventana: int = 20) -> np.ndarray:
    """Volumen de la sesion dividido por su media de las ultimas `ventana`.

    La media incluye la sesion en curso, asi que el indicador es causal: un 3,0
    quiere decir que hoy se ha negociado el triple de lo normal, sin mirar
    manana.
    """
    media = media_movil_vector(volumenes, ventana)
    with np.errstate(divide="ignore", invalid="ignore"):
        return np.where(media > 0, volumenes / media, np.nan)


def beta_vector(
    cierres: np.ndarray, referencia: np.ndarray, ventana: int = 60
) -> np.ndarray:
    """Beta movil contra una referencia, sobre rendimientos simples.

    Las dos series tienen que venir ya alineadas por sesion. Si la referencia no
    se mueve en la ventana, la beta no esta definida y sale NaN en vez de
    dividirse por cero.
    """
    n = len(cierres)
    salida = np.full(n, np.nan)
    if n <= ventana or ventana <= 1 or len(referencia) != n:
        return salida

    with np.errstate(divide="ignore", invalid="ignore"):
        ra = np.diff(cierres) / np.where(cierres[:-1] > 0, cierres[:-1], np.nan)
        rb = np.diff(referencia) / np.where(referencia[:-1] > 0, referencia[:-1], np.nan)

    for j in range(ventana - 1, len(ra)):
        a = ra[j - ventana + 1 : j + 1]
        b = rb[j - ventana + 1 : j + 1]
        if np.isnan(a).any() or np.isnan(b).any():
            continue
        var = float(np.var(b, ddof=1))
        if var > 0:
            salida[j + 1] = float(np.cov(a, b, ddof=1)[0, 1]) / var
    return salida


def rendimiento_relativo_vector(
    cierres: np.ndarray, referencia: np.ndarray, ventana: int
) -> np.ndarray:
    """Diferencia de rendimiento contra la referencia en la ventana.

    Es la resta de dos tasas de cambio, no el cociente de precios: `+0,11`
    significa once puntos porcentuales mejor que la referencia en ese periodo.
    """
    if len(referencia) != len(cierres):
        return np.full(len(cierres), np.nan)
    return roc_vector(cierres, ventana) - roc_vector(referencia, ventana)


def drawdown_vector(valores: np.ndarray) -> np.ndarray:
    """Caida desde el maximo alcanzado hasta cada sesion, en tanto por uno negativo.

    El maximo es el de la propia serie hasta esa sesion, asi que el indicador es
    causal: no es el drawdown "del periodo" calculado a toro pasado, sino el que
    se veia ese dia. El maximo drawdown hasta la fecha es `min()` de este vector.
    """
    n = len(valores)
    if n == 0:
        return np.zeros(0)
    pico = np.maximum.accumulate(valores)
    with np.errstate(divide="ignore", invalid="ignore"):
        return np.where(pico > 0, valores / pico - 1.0, np.nan)
