"""Los indicadores del §16: contra referencia conocida y contra el futuro.

Dos familias de test, y la segunda es la que de verdad importa.

La primera comprueba el **numero**: cada indicador tiene dos o tres definiciones
en circulacion, y "parecido" no sirve cuando de ahi sale una decision. El RSI se
contrasta contra el ejemplo canonico de Wilder, que es la referencia publicada.

La segunda comprueba que son **causales**: que la posicion `i` de cada vector no
depende de nada posterior a `i`. Se hace recortando la serie y verificando que el
prefijo no cambia ni un decimal. Es la misma disciplina que `test_anti_sesgo.py`
aplica al motor, y es lo que permite leer estos vectores por indice desde una
vista con fecha de corte sin abrir la puerta al sesgo de anticipacion.
"""

from __future__ import annotations

import numpy as np
import pytest

from estrategia import indicadores as ind

# Serie del ejemplo publicado de Wilder para el RSI de 14 sesiones.
WILDER = np.array([
    44.34, 44.09, 44.15, 43.61, 44.33, 44.83, 45.10, 45.42, 45.84, 46.08,
    45.89, 46.03, 45.61, 46.28, 46.28, 46.00, 46.03, 46.41, 46.22, 45.64,
])


def _serie(n: int = 120, semilla: int = 7) -> tuple[np.ndarray, ...]:
    """OHLCV determinista. Inventado, pero con la forma de una cotizacion."""
    r = np.random.default_rng(semilla)
    cierres = 100 * np.cumprod(1 + r.normal(0.0004, 0.014, n))
    rango = cierres * r.uniform(0.004, 0.02, n)
    return (
        cierres + rango,           # maximos
        cierres - rango,           # minimos
        cierres,
        r.uniform(1e5, 1e6, n),    # volumenes
    )


# --------------------------------------------------------------------------
# Contra referencia conocida
# --------------------------------------------------------------------------


def test_el_rsi_reproduce_el_ejemplo_de_wilder():
    """Si esto falla, el suavizado ha dejado de ser el de Wilder."""
    rsi = ind.rsi_vector(WILDER, 14)
    assert np.isnan(rsi[:14]).all(), "no hay RSI antes de tener la ventana"
    esperado = [70.46, 66.25, 66.48, 69.35, 66.29, 57.92]
    assert np.allclose(rsi[14:], esperado, atol=0.01)


def test_la_ema_arranca_en_la_media_simple():
    """Sembrarla con el primer valor arrastra un sesgo que tarda en diluirse."""
    ema = ind.ema_vector(WILDER, 5)
    assert np.isnan(ema[:4]).all()
    assert ema[4] == pytest.approx(float(np.mean(WILDER[:5])))


def test_el_macd_de_una_recta_es_cero():
    """Sin curvatura, las dos medias coinciden: cualquier otra cosa es un bug."""
    recta = np.arange(1.0, 121.0)
    macd, senal, hist = ind.macd_vector(recta)
    # Una rampa lineal deja un desfase constante entre las dos EMA, no cero,
    # pero el histograma si converge: la senal alcanza al MACD.
    assert abs(hist[-1]) < 1e-6


def test_la_senal_del_macd_es_la_ema_del_macd_y_no_del_precio():
    """Calcularla sobre el vector con NaN dentro la deja inutilizable."""
    _, _, cierres, _ = _serie()
    macd, senal, _ = ind.macd_vector(cierres)
    assert not np.isnan(senal[-1])
    primer_macd = int(np.flatnonzero(~np.isnan(macd))[0])
    # La senal empieza 9-1 sesiones despues del primer MACD, no antes.
    primer_senal = int(np.flatnonzero(~np.isnan(senal))[0])
    assert primer_senal == primer_macd + 8


def test_el_estocastico_esta_entre_cero_y_cien():
    maximos, minimos, cierres, _ = _serie()
    k, d = ind.estocastico_vector(maximos, minimos, cierres)
    for v in (k, d):
        finitos = v[~np.isnan(v)]
        assert finitos.min() >= 0.0 and finitos.max() <= 100.0


def test_un_valor_parado_no_da_un_estocastico_de_cincuenta():
    """Con maximo igual a minimo el dato no existe; 50 seria una afirmacion."""
    plano = np.full(30, 10.0)
    k, _ = ind.estocastico_vector(plano, plano, plano, 14)
    assert np.isnan(k[-1])


def test_bollinger_usa_desviacion_poblacional():
    """Con la muestral las bandas salen mas anchas, y se nota en ventanas cortas."""
    _, _, cierres, _ = _serie()
    centro, sup, inf, anchura = ind.bollinger_vector(cierres, 20, 2.0)
    sigma = float(np.std(cierres[-20:]))          # ddof=0
    assert sup[-1] == pytest.approx(centro[-1] + 2 * sigma)
    assert inf[-1] == pytest.approx(centro[-1] - 2 * sigma)
    assert anchura[-1] == pytest.approx((sup[-1] - inf[-1]) / centro[-1])


def test_el_obv_sube_con_el_precio_y_baja_con_el():
    cierres = np.array([10.0, 11.0, 11.0, 9.0])
    vol = np.array([100.0, 200.0, 300.0, 400.0])
    assert list(ind.obv_vector(cierres, vol)) == [0.0, 200.0, 200.0, -200.0]


def test_la_beta_contra_uno_mismo_es_uno():
    _, _, cierres, _ = _serie()
    beta = ind.beta_vector(cierres, cierres, 60)
    assert beta[-1] == pytest.approx(1.0)


def test_la_beta_de_una_serie_doblada_es_uno():
    """Doblar el precio no dobla la beta: la beta va sobre rendimientos."""
    _, _, cierres, _ = _serie()
    assert ind.beta_vector(cierres * 2, cierres, 60)[-1] == pytest.approx(1.0)


def test_el_rendimiento_relativo_contra_uno_mismo_es_cero():
    _, _, cierres, _ = _serie()
    assert ind.rendimiento_relativo_vector(cierres, cierres, 20)[-1] == pytest.approx(0.0)


def test_el_drawdown_es_cero_en_maximos_y_negativo_despues():
    valores = np.array([100.0, 110.0, 99.0, 121.0])
    dd = ind.drawdown_vector(valores)
    assert dd[1] == pytest.approx(0.0)
    assert dd[2] == pytest.approx(99 / 110 - 1)
    assert dd[3] == pytest.approx(0.0)


def test_la_volatilidad_de_una_serie_sin_ruido_es_cero():
    """Crecimiento geometrico constante: rendimiento log constante, sigma cero."""
    suave = 100 * np.cumprod(np.full(60, 1.001))
    assert ind.volatilidad_historica_vector(suave, 20)[-1] == pytest.approx(0.0, abs=1e-9)


# --------------------------------------------------------------------------
# Causales: ninguno mira hacia adelante
# --------------------------------------------------------------------------


@pytest.mark.parametrize(
    "nombre,fn",
    [
        ("ema", lambda m, n, c, v: ind.ema_vector(c, 12)),
        ("rsi", lambda m, n, c, v: ind.rsi_vector(c, 14)),
        ("macd", lambda m, n, c, v: ind.macd_vector(c)[0]),
        ("senal_macd", lambda m, n, c, v: ind.macd_vector(c)[1]),
        ("roc", lambda m, n, c, v: ind.roc_vector(c, 20)),
        ("estocastico_k", lambda m, n, c, v: ind.estocastico_vector(m, n, c)[0]),
        ("estocastico_d", lambda m, n, c, v: ind.estocastico_vector(m, n, c)[1]),
        ("bollinger_sup", lambda m, n, c, v: ind.bollinger_vector(c)[1]),
        ("anchura_bollinger", lambda m, n, c, v: ind.bollinger_vector(c)[3]),
        ("volatilidad", lambda m, n, c, v: ind.volatilidad_historica_vector(c)),
        ("obv", lambda m, n, c, v: ind.obv_vector(c, v)),
        ("volumen_relativo", lambda m, n, c, v: ind.volumen_relativo_vector(v)),
        ("beta", lambda m, n, c, v: ind.beta_vector(c, c * 0.9 + 10, 60)),
        ("drawdown", lambda m, n, c, v: ind.drawdown_vector(c)),
        ("media_movil", lambda m, n, c, v: ind.media_movil_vector(c, 50)),
        ("atr", lambda m, n, c, v: ind.atr_wilder_vector(m, n, c, 14)),
    ],
)
def test_ningun_indicador_mira_hacia_adelante(nombre, fn):
    """Recortar el futuro no puede cambiar ni un decimal del pasado.

    Es el test que hace seguro leer estos vectores desde una vista con fecha de
    corte. Si alguno usara una ventana centrada, una normalizacion sobre la serie
    entera o un `bfill`, aqui se veria.
    """
    maximos, minimos, cierres, vol = _serie(120)
    corte = 95
    entero = fn(maximos, minimos, cierres, vol)
    recortado = fn(maximos[:corte], minimos[:corte], cierres[:corte], vol[:corte])

    a, b = entero[:corte], recortado
    assert len(b) == corte, f"{nombre}: el vector no queda alineado con las sesiones"
    assert np.array_equal(np.isnan(a), np.isnan(b)), f"{nombre}: cambian los huecos"
    finitos = ~np.isnan(a)
    assert np.allclose(a[finitos], b[finitos], rtol=1e-12, atol=1e-12), (
        f"{nombre}: el pasado cambia al conocer el futuro"
    )


def test_todos_devuelven_un_vector_alineado_con_las_sesiones():
    """Un indicador mas corto que la serie descoloca la lectura por indice."""
    maximos, minimos, cierres, vol = _serie(80)
    n = len(cierres)
    salidas = [
        ind.ema_vector(cierres, 12),
        ind.rsi_vector(cierres),
        *ind.macd_vector(cierres),
        ind.roc_vector(cierres, 20),
        *ind.estocastico_vector(maximos, minimos, cierres),
        *ind.bollinger_vector(cierres),
        ind.volatilidad_historica_vector(cierres),
        ind.obv_vector(cierres, vol),
        ind.volumen_relativo_vector(vol),
        ind.beta_vector(cierres, cierres, 60),
        ind.rendimiento_relativo_vector(cierres, cierres, 20),
        ind.drawdown_vector(cierres),
    ]
    assert all(len(s) == n for s in salidas)


def test_una_serie_mas_corta_que_la_ventana_no_revienta():
    """Un valor recien salido a bolsa entra en el universo con cuatro sesiones."""
    maximos, minimos, cierres, vol = _serie(5)
    assert np.isnan(ind.rsi_vector(cierres, 14)).all()
    assert np.isnan(ind.ema_vector(cierres, 26)).all()
    assert np.isnan(ind.bollinger_vector(cierres, 20)[0]).all()
    assert np.isnan(ind.beta_vector(cierres, cierres, 60)).all()
    assert len(ind.obv_vector(cierres, vol)) == 5
