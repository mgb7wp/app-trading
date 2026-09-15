"""Registro de fuentes disponibles.

Antes habia un `if/else` en el CLI que conocia los nombres de las fuentes. Con
dos ya empieza a molestar y con cinco es insostenible, asi que aqui hay un mapa
de nombre a constructor: **anadir una fuente es registrarla**, y ni el CLI ni el
panel ni el motor tienen que enterarse.

Los constructores importan de forma perezosa a proposito. Importar yfinance
tarda casi un segundo, y el adaptador de una fuente que necesita una libreria que
no esta instalada no debe impedir arrancar la app entera para usar otra.

Y es tambien la puerta por la que se aplica el registro de licencias: `crear()`
comprueba en `config/fuentes.yaml` que la fuente se puede usar en este entorno
antes de construir nada. Estar registrada como adaptador no basta; hace falta
tener ficha y que su estado lo permita. Ver `licencias.py`.
"""

from __future__ import annotations

from typing import Callable, TYPE_CHECKING

from ..errores import ErrorConfiguracion
from . import licencias

if TYPE_CHECKING:  # pragma: no cover
    from ..config import Config
    from .proveedor import Fuente

_FUENTES: dict[str, Callable[["Config"], "Fuente"]] = {}


def registrar(nombre: str, constructor: Callable[["Config"], "Fuente"]) -> None:
    """Da de alta una fuente con su constructor."""
    _FUENTES[nombre] = constructor


def disponibles() -> list[str]:
    return sorted(_FUENTES)


def crear(nombre: str, cfg: "Config") -> "Fuente":
    """Construye una fuente por su nombre, si su licencia lo permite.

    El orden importa: primero se comprueba que la fuente existe, luego que su
    estado en `config/fuentes.yaml` la autoriza en este entorno, y solo entonces
    se construye. Asi una fuente que no se puede usar no llega ni a importar su
    adaptador, y el mensaje explica que hacer.
    """
    try:
        constructor = _FUENTES[nombre]
    except KeyError as exc:
        raise ErrorConfiguracion(
            f"fuente de datos desconocida: {nombre!r}. "
            f"Disponibles: {', '.join(disponibles())}"
        ) from exc
    licencias.cargar().exigir_apta(nombre)
    return constructor(cfg)


# -- Fuentes de serie --------------------------------------------------------


def _sintetico(cfg: "Config") -> "Fuente":
    from .sintetico import ProveedorSintetico

    return ProveedorSintetico(cfg)


def _yfinance(cfg: "Config") -> "Fuente":
    from .yfinance_proveedor import ProveedorYFinance

    return ProveedorYFinance(cfg)


def _eodhd(cfg: "Config") -> "Fuente":
    from .eodhd_proveedor import ProveedorEODHD

    return ProveedorEODHD(cfg)


registrar("sintetico", _sintetico)
registrar("yfinance", _yfinance)
registrar("eodhd", _eodhd)
