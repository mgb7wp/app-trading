"""El sitio del research: que diga la verdad y que no pida nada a nadie.

Lo que se publica en el dominio es contenido propio, no datos de terceros, y
esa es la razon por la que se puede publicar hoy. Estos tests protegen las dos
propiedades de las que depende esa afirmacion: que la pagina sea autocontenida
y que el semaforo salga del mismo fichero que el codigo obedece al arrancar.
"""

from __future__ import annotations

import html
import re
from datetime import date

import pytest

from estrategia import sitio_research
from estrategia.datos import licencias


@pytest.fixture(scope="module")
def pagina() -> str:
    return sitio_research.generar(hoy=date(2026, 9, 15))


# --------------------------------------------------------------------------
# Autocontenida
# --------------------------------------------------------------------------


def test_la_pagina_no_pide_nada_a_nadie(pagina):
    """Sin JavaScript, sin CDN, sin fuentes web, sin imagenes remotas.

    Es la propiedad que hace que la pagina se abra igual desde un servidor, desde
    el disco o desde un correo, y la que evita filtrar visitas a terceros.
    """
    assert not re.search(r"<script[^>]+\bsrc=", pagina)
    assert not re.search(r'<link[^>]+href="https?://', pagina)
    assert "@import" not in pagina
    assert not re.search(r'<img[^>]+src="https?://', pagina)


def test_no_hay_javascript(pagina):
    assert "<script" not in pagina.lower()


def test_los_enlaces_externos_son_enlaces_no_recursos(pagina):
    """Enlazar a los terminos oficiales si; cargar algo de fuera no."""
    externos = re.findall(r'href="(https?://[^"]+)"', pagina)
    assert externos, "la pagina tiene que enlazar a los terminos oficiales"
    assert any("sec.gov" in u for u in externos)
    assert any("gdeltproject.org" in u for u in externos)


# --------------------------------------------------------------------------
# El contenido sale del registro, no de una copia a mano
# --------------------------------------------------------------------------


def test_todas_las_fuentes_del_registro_salen_en_la_pagina(pagina):
    """Si el semaforo se escribiera a mano, se separaria del codigo el primer dia."""
    for f in licencias.cargar().fuentes:
        # Escapado, porque los nombres llevan `&` (S&P Dow Jones Indices) y en la
        # pagina tienen que salir como entidad, no en crudo.
        assert html.escape(f.name, quote=True) in pagina, f"falta {f.id} en el sitio"


def test_el_estado_va_escrito_al_lado_del_color(pagina):
    """El par ambar/rojo queda en la banda 6-8 de separacion para daltonismo.

    Eso es legal solo con codificacion secundaria, asi que el estado tiene que
    aparecer como texto y no unicamente como color. Si alguien quita el texto
    para que quede mas limpio, este test se pone rojo.
    """
    for estado in ("APPROVED_WITH_RESTRICTIONS", "DEVELOPMENT_ONLY", "REJECTED", "NEEDS_REVIEW"):
        assert estado in pagina


def test_un_cambio_de_estado_se_refleja_en_la_pagina():
    """La prueba de que la pagina obedece al registro y no al reves."""
    reg = licencias.cargar()
    yahoo = reg.por_id["yfinance"]
    antes = sitio_research.generar(registro=reg)
    assert "Solo desarrollo" in antes

    aprobada = yahoo.model_copy(update={"status": "APPROVED"})
    reg2 = reg.model_copy(
        update={"fuentes": tuple(aprobada if f.id == "yfinance" else f for f in reg.fuentes)}
    )
    despues = sitio_research.generar(registro=reg2)
    assert "Se puede usar en producción" in despues


# --------------------------------------------------------------------------
# Honestidad
# --------------------------------------------------------------------------


def test_el_aviso_de_no_verificado_esta_arriba_del_todo(pagina):
    """Enterrar este aviso al final seria la forma educada de esconderlo."""
    aviso = pagina.index("Nada de esto está verificado")
    primera_fuente = pagina.index("El semáforo de fuentes")
    assert aviso < primera_fuente


def test_se_dice_cuantas_fuentes_faltan_por_verificar(pagina):
    n = len(licencias.cargar().pendientes_de_verificar())
    assert f"{n} fuentes" in pagina


def test_no_se_promete_lo_que_no_se_puede_dar(pagina):
    """Las tres capas que dependen de precios salen marcadas, no disimuladas."""
    for capa in ("Valoración", "Análisis técnico", "Benchmark y alfa"):
        assert capa in pagina
    assert "Requiere precios" in pagina


def test_lleva_el_descargo_legal(pagina):
    assert "no es asesoramiento de inversión" in pagina
    assert "no por un abogado" in pagina


# --------------------------------------------------------------------------
# Forma
# --------------------------------------------------------------------------


def test_tiene_titulo_idioma_y_viewport(pagina):
    assert pagina.startswith("<!doctype html>")
    assert '<html lang="es">' in pagina
    assert 'name="viewport"' in pagina
    assert "<title>" in pagina


def test_funciona_en_claro_y_en_oscuro(pagina):
    assert "prefers-color-scheme: dark" in pagina
    assert "color-scheme: light" in pagina


def test_se_escribe_donde_se_le_pide(tmp_path):
    destino = tmp_path / "publico" / "index.html"
    ruta = sitio_research.escribir(destino)
    assert ruta == destino and destino.is_file()
    assert destino.read_text(encoding="utf-8").startswith("<!doctype html>")
