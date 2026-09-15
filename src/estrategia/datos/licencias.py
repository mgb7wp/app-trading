"""Registro de fuentes que manda: el estado de licencia se aplica al arrancar.

El §22 del encargo pedia una tabla `data_sources` con el estado de cada fuente,
y decia por que: «no quiero que el proyecto dependa accidentalmente de una fuente
con problemas de licencia». Una tabla que solo se consulta cuando alguien se
acuerda no consigue eso. Esta si, porque la lee el registro de fuentes antes de
construir nada:

    APPROVED                     se usa en produccion
    APPROVED_WITH_RESTRICTIONS   se usa, con sus condiciones anotadas
    DEVELOPMENT_ONLY             funciona en local; en produccion, error al arrancar
    REJECTED / NEEDS_REVIEW      no se instancia nunca

Dos decisiones de diseno que conviene explicar, porque las dos van en contra de
lo comodo y las dos son a proposito.

**El entorno por defecto es produccion.** Si el defecto fuera `desarrollo`,
olvidarse de poner la variable en el despliegue dejaria correr una fuente con
problemas de licencia en produccion, en silencio, que es el fallo caro. Con este
defecto, olvidarse de ponerla en local da un error ruidoso que se arregla en diez
segundos. Se elige el error barato.

**Una fuente sin ficha no se instancia.** No hay estado por defecto ni lista de
excepciones: dar de alta un adaptador obliga a escribir su ficha en
`config/fuentes.yaml`, con su licencia y su enlace. Es la unica forma de que el
documento y el codigo no se separen con el tiempo.

El razonamiento de cada estado, con el enlace a los terminos oficiales, esta en
`docs/data-licensing.md`. Y hoy **ninguna ficha esta verificada contra su fuente
primaria** salvo la del proveedor sintetico, que son datos que inventamos
nosotros: lo demas esta marcado `PROVISIONAL`, que significa que el enlace esta
localizado pero nadie ha leido el texto.
"""

from __future__ import annotations

import os
from datetime import date
from functools import lru_cache
from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel, ConfigDict, Field

from ..errores import ErrorConfiguracion

RAIZ = Path(__file__).resolve().parents[3]
RUTA_POR_DEFECTO = RAIZ / "config" / "fuentes.yaml"

Estado = Literal[
    "APPROVED",
    "APPROVED_WITH_RESTRICTIONS",
    "DEVELOPMENT_ONLY",
    "REJECTED",
    "NEEDS_REVIEW",
]
Verificacion = Literal["VERIFICADO", "PROVISIONAL", "NO_LOCALIZADO"]
Entorno = Literal["produccion", "desarrollo"]


class _Base(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class EntornoCfg(_Base):
    """Como se decide si estamos en produccion, y que estados valen en cada caso."""

    variable: str
    por_defecto: Entorno
    estados_aptos_en_produccion: tuple[Estado, ...]
    estados_aptos_en_desarrollo: tuple[Estado, ...]

    def aptos(self, entorno: Entorno) -> tuple[Estado, ...]:
        return (
            self.estados_aptos_en_produccion
            if entorno == "produccion"
            else self.estados_aptos_en_desarrollo
        )


class Ficha(_Base):
    """La ficha del §22 para una fuente."""

    id: str
    name: str
    country: str
    data_type: tuple[str, ...]
    source_url: str | None = None
    api_url: str | None = None
    access_method: str
    requires_api_key: bool | str
    free: bool
    commercial_use: str | bool | None = None
    storage_allowed: str | bool | None = None
    redistribution_allowed: str | bool | None = None
    attribution_required: str | bool | None = None
    rate_limit: str | None = None
    update_frequency: str
    historical_depth: str
    license: str | None = None
    terms_url: str | None = None
    status: Estado
    tier: int = Field(ge=1, le=4)
    priority: int
    verification: Verificacion
    last_verified: date | None = None
    adaptador: str | None = None
    notes: str = ""

    @property
    def verificada(self) -> bool:
        return self.verification == "VERIFICADO" and self.last_verified is not None

    def apta_en(self, entorno: Entorno, cfg_entorno: EntornoCfg) -> bool:
        return self.status in cfg_entorno.aptos(entorno)

    def restricciones(self) -> list[str]:
        """Condiciones que hay que respetar al usar esta fuente.

        El informe y la ficha de empresa las leen para avisar solos, que es lo
        unico que evita que una obligacion de atribucion se quede en un `notes`
        que nadie mira.
        """
        avisos: list[str] = []
        if _es_si(self.attribution_required):
            avisos.append(f"atribucion obligatoria a {self.name}")
        if self.redistribution_allowed in ("por_dataset", "por_serie"):
            avisos.append(
                f"la licencia de {self.name} va {self.redistribution_allowed.replace('_', ' ')}: "
                "hay que comprobarla en cada ingesta"
            )
        if _es_no(self.redistribution_allowed):
            avisos.append(f"{self.name} no permite redistribuir los datos")
        if not self.verificada:
            avisos.append(
                f"la licencia de {self.name} esta {self.verification} y sin verificar "
                "contra la fuente primaria"
            )
        return avisos


class Registro(_Base):
    """El contenido de `config/fuentes.yaml`, validado."""

    version: int
    entorno: EntornoCfg
    fuentes: tuple[Ficha, ...]

    @property
    def por_adaptador(self) -> dict[str, Ficha]:
        return {f.adaptador: f for f in self.fuentes if f.adaptador}

    @property
    def por_id(self) -> dict[str, Ficha]:
        return {f.id: f for f in self.fuentes}

    def entorno_actual(self) -> Entorno:
        """Produccion salvo que se diga explicitamente lo contrario."""
        bruto = os.environ.get(self.entorno.variable, "").strip().lower()
        if not bruto:
            return self.entorno.por_defecto
        if bruto not in ("produccion", "desarrollo"):
            raise ErrorConfiguracion(
                f"{self.entorno.variable}={bruto!r} no es un entorno valido. "
                "Usa 'produccion' o 'desarrollo'."
            )
        return bruto  # type: ignore[return-value]

    def ficha_de(self, adaptador: str) -> Ficha:
        try:
            return self.por_adaptador[adaptador]
        except KeyError as exc:
            raise ErrorConfiguracion(
                f"la fuente '{adaptador}' no tiene ficha en config/fuentes.yaml.\n"
                "Ninguna fuente se instancia sin declarar su licencia: anade su "
                "ficha con el esquema del §22 y su enlace a los terminos oficiales. "
                "Ver docs/data-licensing.md."
            ) from exc

    def exigir_apta(self, adaptador: str, entorno: Entorno | None = None) -> Ficha:
        """Comprueba que la fuente se puede usar, o explica por que no.

        Es lo que convierte `docs/data-licensing.md` en algo que el codigo
        obedece. Se llama desde `registro.crear()`, que es por donde pasa toda
        construccion de una fuente.
        """
        ficha = self.ficha_de(adaptador)
        donde = entorno or self.entorno_actual()
        if ficha.apta_en(donde, self.entorno):
            return ficha
        raise ErrorConfiguracion(_motivo(ficha, donde, self.entorno))

    def pendientes_de_verificar(self) -> list[Ficha]:
        """Fuentes aptas cuya licencia nadie ha comprobado todavia.

        Son las que hay que resolver antes de cobrarle a un cliente. La lista
        corta esta en docs/data-licensing.md.
        """
        return [
            f
            for f in self.fuentes
            if f.status in ("APPROVED", "APPROVED_WITH_RESTRICTIONS") and not f.verificada
        ]


# --------------------------------------------------------------------------


def _es_si(valor: str | bool | None) -> bool:
    return valor is True or (isinstance(valor, str) and valor.lower() in ("si", "true"))


def _es_no(valor: str | bool | None) -> bool:
    return valor is False or (isinstance(valor, str) and valor.lower() in ("no", "false"))


def _motivo(ficha: Ficha, entorno: Entorno, cfg: EntornoCfg) -> str:
    """El mensaje que ve quien intenta usar una fuente que no puede."""
    cabecera = (
        f"la fuente '{ficha.adaptador}' esta en estado {ficha.status} y no se "
        f"puede usar en entorno '{entorno}'."
    )
    detalle = {
        "DEVELOPMENT_ONLY": (
            "Sus terminos no permiten usarla en un producto comercial. Sirve para "
            "desarrollo y para los tests, y por eso no se ha borrado.\n"
            f"Para trabajar en local: {cfg.variable}=desarrollo"
        ),
        "REJECTED": (
            "Sus terminos la excluyen de cualquier uso en este producto. No se "
            "instancia en ningun entorno."
        ),
        "NEEDS_REVIEW": (
            "Su licencia no esta resuelta. No se instancia hasta que alguien lea "
            "los terminos oficiales y actualice su ficha."
        ),
    }.get(ficha.status, "")
    enlace = f"\nTerminos: {ficha.terms_url}" if ficha.terms_url else ""
    nota = f"\nMotivo: {' '.join(ficha.notes.split())}" if ficha.notes else ""
    return f"{cabecera}\n{detalle}{nota}{enlace}\nVer docs/data-licensing.md."


@lru_cache(maxsize=4)
def _cargar_cacheado(ruta: str) -> Registro:
    p = Path(ruta)
    if not p.is_file():
        raise ErrorConfiguracion(f"no existe el registro de fuentes: {p}")
    with p.open(encoding="utf-8") as fh:
        contenido = yaml.safe_load(fh)
    if not isinstance(contenido, dict):
        raise ErrorConfiguracion(f"{p} no contiene un mapa YAML en la raiz")
    reg = Registro.model_validate(contenido)

    ids = [f.id for f in reg.fuentes]
    if len(set(ids)) != len(ids):
        repes = sorted({i for i in ids if ids.count(i) > 1})
        raise ErrorConfiguracion(f"ids repetidos en {p}: {repes}")

    adaptadores = [f.adaptador for f in reg.fuentes if f.adaptador]
    if len(set(adaptadores)) != len(adaptadores):
        repes = sorted({a for a in adaptadores if adaptadores.count(a) > 1})
        raise ErrorConfiguracion(f"adaptadores repetidos en {p}: {repes}")
    return reg


def cargar(ruta: Path | str | None = None) -> Registro:
    """Carga y valida `config/fuentes.yaml`."""
    return _cargar_cacheado(str(Path(ruta) if ruta is not None else RUTA_POR_DEFECTO))


def limpiar_cache() -> None:
    """Olvida el registro cargado. Para los tests que escriben su propio YAML."""
    _cargar_cacheado.cache_clear()
