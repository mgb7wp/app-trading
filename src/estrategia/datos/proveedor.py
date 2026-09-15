"""Interfaz de los proveedores de datos.

Precios y fundamentales se piden por separado a proposito. El documento ya
contempla cambiar de proveedor fundamental (`ampliacion_futura: eodhd`) sin
tocar el de precios, y ademas tienen longitudes de historico, cadencias y modos
de fallar muy distintos: una sola interfaz para ambos obligaria a inventar la
mitad que un proveedor no ofrece.

Columnas que todo proveedor de precios debe devolver, en divisa local:

- `cierre`, `apertura`, `maximo`, `minimo`: OHLC **ajustado** por dividendos y
  splits. Los cuatro, no solo el cierre: calcular el ATR con maximos y minimos
  en bruto y las medias con el cierre ajustado convierte cada dividendo en un
  hueco fantasma y deja el ATR sin sentido.
- `cierre_bruto`, `volumen`: sin ajustar. El volumen negociado se mide con
  precio bruto x volumen bruto, porque el volumen no se ajusta por dividendos y
  mezclarlo con el precio ajustado subestima la liquidez historica.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import date

import pandas as pd

COLUMNAS_PRECIOS = [
    "fecha",
    "ticker",
    "apertura",
    "maximo",
    "minimo",
    "cierre",
    "cierre_bruto",
    "volumen",
]

COLUMNAS_FUNDAMENTALES = [
    "ticker",
    "fin_periodo",
    "periodo",
    "fecha_publicacion",
    "origen_fecha_publicacion",
    "origen_pit",
    "fecha_descarga",
    "roe",
    "margen_operativo",
    "ventas",
    "flujo_caja_libre",
    "deuda_neta",
    "ebitda",
    "ebit",
    "ev",
    "patrimonio_neto",
]


class ProveedorPrecios(ABC):
    """Da series OHLCV en divisa local."""

    @abstractmethod
    def precios(self, tickers: list[str], inicio: date, fin: date) -> pd.DataFrame:
        """OHLCV por ticker y fecha, con las columnas de `COLUMNAS_PRECIOS`."""

    @abstractmethod
    def fx(self, divisas: list[str], inicio: date, fin: date) -> pd.DataFrame:
        """Tipos de cambio diarios `EUR -> divisa`.

        Se guardan siempre en un solo sentido y se invierten al leer, para que
        no haya dos convenios circulando por el codigo.
        """

    @abstractmethod
    def sectores(self, tickers: list[str]) -> dict[str, str | None]:
        """Sector que el proveedor asigna a cada ticker, sin traducir."""


class ProveedorFundamentales(ABC):
    """Da estados financieros con su fecha de publicacion."""

    @abstractmethod
    def fundamentales(self, tickers: list[str], inicio: date, fin: date) -> pd.DataFrame:
        """Fundamentales por ticker y periodo, segun `COLUMNAS_FUNDAMENTALES`.

        `fecha_publicacion` es obligatoria. Si el proveedor no la ofrece, quien
        implemente esto debe estimarla a partir del cierre del periodo mas el
        retraso de `datos.retraso_por_mercado`, y decirlo en
        `origen_fecha_publicacion`.
        """


class Proveedor(ProveedorPrecios, ProveedorFundamentales, ABC):
    """Un proveedor que cubre ambas cosas."""

    nombre: str = "abstracto"
