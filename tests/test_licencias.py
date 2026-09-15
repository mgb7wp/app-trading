"""El registro de fuentes manda: la licencia se aplica al arrancar, no se recuerda.

El §22 del encargo pedia una tabla de fuentes con su estado y decia por que: «no
quiero que el proyecto dependa accidentalmente de una fuente con problemas de
licencia». Estos tests son lo que convierte esa intencion en una garantia.

El que importa es `test_una_fuente_de_solo_desarrollo_no_arranca_en_produccion`.
Si alguien lo pone verde relajando la comprobacion en vez de arreglando la causa,
el registro vuelve a ser documentacion.
"""

from __future__ import annotations

import textwrap

import pytest

from estrategia.datos import licencias, registro
from estrategia.errores import ErrorConfiguracion

# --------------------------------------------------------------------------
# El registro real
# --------------------------------------------------------------------------


def test_el_registro_carga_y_valida():
    reg = licencias.cargar()
    assert reg.version == 1
    assert len(reg.fuentes) >= 15


def test_todo_adaptador_registrado_tiene_ficha():
    """Dar de alta un adaptador obliga a declarar su licencia.

    Sin esto, anadir una fuente nueva y olvidarse de su ficha la dejaria
    funcionando sin que nadie hubiera mirado sus terminos, que es exactamente el
    accidente que el §22 quiere evitar.
    """
    reg = licencias.cargar()
    sin_ficha = [n for n in registro.disponibles() if n not in reg.por_adaptador]
    assert not sin_ficha, f"adaptadores sin ficha en config/fuentes.yaml: {sin_ficha}"


def test_toda_ficha_tiene_enlace_a_sus_terminos():
    """«No quiero afirmaciones del tipo "es gratis" sin comprobar la fuente oficial.»

    Se exceptua el proveedor sintetico, cuyos datos inventamos nosotros, y las
    fichas que declaran expresamente no haber localizado terminos: ahi la
    ausencia del enlace es el hallazgo, no un descuido.
    """
    reg = licencias.cargar()
    sin_enlace = [
        f.id
        for f in reg.fuentes
        if f.terms_url is None
        and f.id not in ("sintetico", "investor_relations")
        and f.verification != "NO_LOCALIZADO"
    ]
    assert not sin_enlace, f"fichas sin enlace a terminos oficiales: {sin_enlace}"


def test_las_bolsas_estan_rechazadas():
    """B3, BME, NSE y BSE prohiben el uso comercial de su market data."""
    reg = licencias.cargar().por_id
    for id_ in ("b3", "bme", "nse", "bse", "sp_dj_indices"):
        assert reg[id_].status == "REJECTED", id_


def test_yahoo_es_solo_de_desarrollo():
    """Era la fuente de precios del sistema anterior. No puede llegar a produccion."""
    ficha = licencias.cargar().por_id["yfinance"]
    assert ficha.status == "DEVELOPMENT_ONLY"
    assert ficha.tier == 4


def test_ninguna_fuente_de_produccion_esta_verificada_todavia():
    """El estado honesto del proyecto, afirmado por un test.

    Este test **debe** fallar el dia que se verifiquen las licencias contra la
    fuente primaria, y ese fallo es la senal de que hay que quitarlo. Mientras
    este verde, el proyecto no puede cobrarle a nadie.
    """
    pendientes = licencias.cargar().pendientes_de_verificar()
    assert pendientes, (
        "si esto falla, alguien ha verificado licencias: actualiza "
        "docs/data-licensing.md y borra este test"
    )
    assert all(f.last_verified is None for f in pendientes)


# --------------------------------------------------------------------------
# La comprobacion en ejecucion
# --------------------------------------------------------------------------


def test_una_fuente_de_solo_desarrollo_no_arranca_en_produccion(cfg, monkeypatch):
    """La garantia central: DEVELOPMENT_ONLY + produccion = error al arrancar.

    Si este test se pone rojo, el registro de fuentes ha dejado de mandar y hay
    que arreglar la causa, no el test.
    """
    monkeypatch.setenv("LALONJA_ENTORNO", "produccion")
    with pytest.raises(ErrorConfiguracion) as exc:
        registro.crear("yfinance", cfg)

    mensaje = str(exc.value)
    assert "DEVELOPMENT_ONLY" in mensaje
    # El mensaje tiene que servir para algo: decir que hacer y donde mirar.
    assert "LALONJA_ENTORNO=desarrollo" in mensaje
    assert "data-licensing.md" in mensaje


def test_la_misma_fuente_si_arranca_en_desarrollo(cfg, monkeypatch):
    monkeypatch.setenv("LALONJA_ENTORNO", "desarrollo")
    fuente = registro.crear("yfinance", cfg)
    assert fuente.nombre == "yfinance"


def test_el_sintetico_vale_en_los_dos_entornos(cfg, monkeypatch):
    """Son datos que generamos nosotros: no hay terminos de nadie que incumplir."""
    for entorno in ("produccion", "desarrollo"):
        monkeypatch.setenv("LALONJA_ENTORNO", entorno)
        assert registro.crear("sintetico", cfg).nombre == "sintetico"


def test_el_entorno_por_defecto_es_produccion(monkeypatch):
    """Olvidarse de la variable tiene que fallar hacia el lado barato.

    Si el defecto fuera 'desarrollo', olvidarla en el despliegue dejaria correr
    una fuente con problemas de licencia en silencio. Asi, olvidarla en local da
    un error que se arregla en diez segundos.
    """
    monkeypatch.delenv("LALONJA_ENTORNO", raising=False)
    assert licencias.cargar().entorno_actual() == "produccion"


def test_un_entorno_mal_escrito_no_se_interpreta_como_desarrollo(monkeypatch):
    """`LALONJA_ENTORNO=prod` no puede caer en el lado permisivo por descuido."""
    monkeypatch.setenv("LALONJA_ENTORNO", "prod")
    with pytest.raises(ErrorConfiguracion, match="no es un entorno valido"):
        licencias.cargar().entorno_actual()


def test_una_fuente_sin_ficha_no_se_instancia(cfg, monkeypatch):
    """Estar registrada como adaptador no basta: hace falta declarar su licencia."""
    monkeypatch.setitem(registro._FUENTES, "fuente_fantasma", lambda c: None)
    with pytest.raises(ErrorConfiguracion, match="no tiene ficha"):
        registro.crear("fuente_fantasma", cfg)


# --------------------------------------------------------------------------
# Las restricciones salen impresas
# --------------------------------------------------------------------------


def test_las_restricciones_llegan_al_informe(cfg):
    """Una obligacion de atribucion que vive en un YAML no se cumple sola."""
    from estrategia.datos.enrutador import Enrutador

    avisos = Enrutador(cfg.con_fuente_unica("yfinance")).restricciones()
    assert any("no permite redistribuir" in a for a in avisos)
    assert any("sin verificar" in a for a in avisos)


def test_una_fuente_con_atribucion_obligatoria_lo_dice():
    ficha = licencias.cargar().por_id["world_bank"]
    avisos = ficha.restricciones()
    assert any("atribucion obligatoria" in a for a in avisos)


def test_una_licencia_por_dataset_pide_comprobarla_en_cada_ingesta():
    """CVM dice que la licencia va en el metadato de cada dataset y puede cambiar."""
    avisos = licencias.cargar().por_id["cvm_dados_abertos"].restricciones()
    assert any("por dataset" in a for a in avisos)


# --------------------------------------------------------------------------
# Validacion del fichero
# --------------------------------------------------------------------------


def _escribir(tmp_path, cuerpo: str):
    ruta = tmp_path / "fuentes.yaml"
    ruta.write_text(textwrap.dedent(cuerpo), encoding="utf-8")
    licencias.limpiar_cache()
    return ruta


_CABECERA = """\
    version: 1
    entorno:
      variable: LALONJA_ENTORNO
      por_defecto: produccion
      estados_aptos_en_produccion: [APPROVED]
      estados_aptos_en_desarrollo: [APPROVED, DEVELOPMENT_ONLY]
    fuentes:
"""

_FICHA = """\
      - id: {id}
        name: Una fuente
        country: global
        data_type: [precios]
        access_method: rest_json
        requires_api_key: false
        free: true
        update_frequency: diaria
        historical_depth: larga
        status: APPROVED
        tier: 1
        priority: 1
        verification: PROVISIONAL
        adaptador: {adaptador}
"""


def test_un_estado_inventado_no_carga(tmp_path):
    ruta = _escribir(
        tmp_path,
        _CABECERA + _FICHA.format(id="x", adaptador="x").replace("APPROVED", "CASI_APROBADA"),
    )
    with pytest.raises(Exception):
        licencias.cargar(ruta)
    licencias.limpiar_cache()


def test_dos_fichas_con_el_mismo_id_no_cargan(tmp_path):
    ruta = _escribir(
        tmp_path,
        _CABECERA
        + _FICHA.format(id="x", adaptador="a")
        + _FICHA.format(id="x", adaptador="b"),
    )
    with pytest.raises(ErrorConfiguracion, match="ids repetidos"):
        licencias.cargar(ruta)
    licencias.limpiar_cache()


def test_dos_fichas_para_el_mismo_adaptador_no_cargan(tmp_path):
    """Dos fichas con estados distintos para un adaptador serian ambiguas."""
    ruta = _escribir(
        tmp_path,
        _CABECERA
        + _FICHA.format(id="a", adaptador="x")
        + _FICHA.format(id="b", adaptador="x"),
    )
    with pytest.raises(ErrorConfiguracion, match="adaptadores repetidos"):
        licencias.cargar(ruta)
    licencias.limpiar_cache()


def test_una_clave_desconocida_no_pasa(tmp_path):
    """Una errata en el nombre de un campo no puede quedarse callada."""
    ruta = _escribir(
        tmp_path,
        _CABECERA + _FICHA.format(id="x", adaptador="x") + "        comercial_use: si\n",
    )
    with pytest.raises(Exception):
        licencias.cargar(ruta)
    licencias.limpiar_cache()
