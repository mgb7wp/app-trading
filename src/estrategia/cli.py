"""Interfaz de linea de comandos.

Se apoya en `argparse` de la biblioteca estandar a proposito: es una dependencia
menos, y lo que hace falta aqui son siete subcomandos y un par de opciones.

El comando `foto` merece una nota. El documento pide guardar cada semana una
copia de los fundamentales y del tipo de cambio "desde el primer dia", para ir
construyendo un historico propio sin sesgo de anticipacion. Una app de escritorio
no tiene forma de hacerlo sola, asi que el comando esta pensado para programarlo
(cron en Linux o macOS, Programador de tareas en Windows) y es idempotente por
semana: ejecutarlo dos veces el mismo lunes no duplica nada.
"""

from __future__ import annotations

import argparse
import sys
from datetime import date, timedelta
from pathlib import Path

from . import backtest as backtest_mod
from . import config as config_mod
from . import informe as informe_mod
from . import metricas as metricas_mod
from . import universo as universo_mod
from . import validacion as validacion_mod
from .datos.almacen import Instantanea
from .errores import ErrorEstrategia
from .sectores import MapaSectores

RAIZ = config_mod.RAIZ
DIR_DATOS = RAIZ / "datos"
DIR_CACHE = DIR_DATOS / "cache"
DIR_FOTOS = DIR_DATOS / "fotos"
DIR_RESULTADOS = DIR_DATOS / "resultados"
RUTA_CONSULTAS = DIR_DATOS / "consultas_validacion.json"


def _proveedor(nombre: str, cfg):
    if nombre == "sintetico":
        from .datos.sintetico import ProveedorSintetico

        return ProveedorSintetico(cfg)
    from .datos.yfinance_proveedor import ProveedorYFinance

    return ProveedorYFinance(cfg)


def _descargar(cfg, nombre_proveedor: str, inicio: date, fin: date) -> Instantanea:
    prov = _proveedor(nombre_proveedor, cfg)
    tickers = cfg.universo.tickers()
    indices = list(cfg.reglas.tecnico.indices_regimen.values())
    referencias = [r.ticker for r in cfg.implementacion.referencias.values()]
    divisas = sorted(
        {m.divisa for m in cfg.reglas.universo.mercados}
        | {r.divisa for r in cfg.implementacion.referencias.values()}
    )

    print(f"Descargando precios de {len(tickers)} valores + indices y referencias...")
    precios = prov.precios(tickers + indices + referencias, inicio, fin)
    print(f"Descargando fundamentales de {len(tickers)} valores...")
    fundamentales = prov.fundamentales(tickers, inicio, fin)
    print("Descargando tipos de cambio...")
    fx = prov.fx(divisas, inicio, fin)
    print("Leyendo sectores...")
    sectores = prov.sectores(tickers)

    return Instantanea(
        precios=precios, fundamentales=fundamentales, fx=fx, sectores=sectores,
        fecha_descarga=date.today(), origen=prov.nombre,
    )


def _cargar_instantanea(args, cfg) -> Instantanea:
    directorio = DIR_CACHE / args.proveedor
    if not (directorio / "precios.parquet").is_file():
        print(
            f"No hay datos en cache para '{args.proveedor}'. "
            f"Ejecuta primero: estrategia datos --proveedor {args.proveedor}",
            file=sys.stderr,
        )
        raise SystemExit(2)
    return Instantanea.cargar(directorio)


# --------------------------------------------------------------------------
# Comandos
# --------------------------------------------------------------------------


def cmd_datos(args, cfg) -> None:
    fin = date.today()
    inicio = fin - timedelta(days=int(args.anos * 365.25))
    inst = _descargar(cfg, args.proveedor, inicio, fin)
    destino = DIR_CACHE / args.proveedor
    inst.guardar(destino)
    print(
        f"Guardado en {destino}: {len(inst.precios)} filas de precios, "
        f"{len(inst.fundamentales)} de fundamentales, {len(inst.fx)} de divisas."
    )


def cmd_foto(args, cfg) -> None:
    """Foto semanal de fundamentales y divisas.

    Idempotente por semana ISO: dos ejecuciones el mismo lunes no duplican nada.
    """
    hoy = date.today()
    ano, semana, _ = hoy.isocalendar()
    destino = DIR_FOTOS / f"{ano}-S{semana:02d}"
    if destino.is_dir() and not args.forzar:
        print(f"Ya existe la foto de la semana {ano}-S{semana:02d} en {destino}.")
        return

    inicio = hoy - timedelta(days=int(args.anos * 365.25))
    inst = _descargar(cfg, args.proveedor, inicio, hoy)
    inst.guardar(destino)
    print(f"Foto de {ano}-S{semana:02d} guardada en {destino}.")


def cmd_universo(args, cfg) -> None:
    inst = _cargar_instantanea(args, cfg).preparar(cfg)
    fecha = args.fecha or inst.rango_precios[1]
    vista = inst.vista(fecha)
    mapa = MapaSectores(cfg)
    resultado = universo_mod.evaluar(fecha, vista, cfg, mapa)

    elegibles = [e for e in resultado.values() if e.elegible]
    print(f"Universo a {fecha}: {len(elegibles)} elegibles de {len(resultado)}.\n")
    for mercado_id in cfg.reglas.mercados_por_id:
        delm = [e for e in resultado.values() if e.mercado == mercado_id]
        ok = [e for e in delm if e.elegible]
        print(f"  {mercado_id}: {len(ok)}/{len(delm)} elegibles")
        if args.detalle:
            for e in sorted(delm, key=lambda x: x.ticker):
                estado = "OK " if e.elegible else f"NO ({e.motivo})"
                print(f"      {e.ticker:16s} {estado:32s} vol {e.volumen_medio_base:,.0f}")
    if mapa.sin_mapear:
        print(f"\nSectores sin mapear: {mapa.sin_mapear}")


def cmd_senales(args, cfg) -> None:
    """Candidatas de la ultima revision semanal disponible."""
    inst = _cargar_instantanea(args, cfg).preparar(cfg)
    fin = args.fecha or inst.rango_precios[1]
    # Se corre un backtest corto que termina en la fecha pedida y se leen los
    # eventos de la ultima semana: asi las senales salen del mismo codigo que
    # las produce en el backtest, y no de un camino paralelo que puede divergir.
    inicio = fin - timedelta(days=int(3 * 365.25))
    r = backtest_mod.ejecutar(inst, cfg, max(inicio, inst.rango_precios[0]), fin)
    ev = r.eventos_df
    if ev.empty:
        print("No hay eventos en el periodo.")
        return
    ordenes = ev[ev["tipo"] == "orden"]
    if ordenes.empty:
        print("La ultima revision no genero ordenes.")
    else:
        ultima = ordenes["fecha"].max()
        print(f"Ordenes de la revision del {ultima}:\n")
        print(ordenes[ordenes["fecha"] == ultima].to_string(index=False))

    rech = ev[(ev["tipo"] == "rechazo") & (ev["fecha"] == ev["fecha"].max())]
    if not rech.empty and args.detalle:
        print("\nRechazos de esa fecha:\n")
        print(rech.to_string(index=False))


def cmd_backtest(args, cfg) -> None:
    inst = _cargar_instantanea(args, cfg)
    division = validacion_mod.dividir(inst, cfg)

    if args.periodo == "validacion":
        registro = validacion_mod.RegistroConsultas(RUTA_CONSULTAS)
        n = registro.anotar("backtest --periodo validacion")
        print(
            f"AVISO: has abierto el periodo de validacion. Van {n} consultas.\n"
            f"Cada una lo acerca a ser un periodo de diseno mas.\n"
        )
        inicio, fin = division.validacion
    elif args.periodo == "diseno":
        inicio, fin = division.diseno
    else:
        inicio, fin = division.inicio, division.fin

    print(f"Backtest de {inicio} a {fin} (periodo: {args.periodo})...")
    r = backtest_mod.ejecutar(inst, cfg, inicio, fin)

    consultas = validacion_mod.RegistroConsultas(RUTA_CONSULTAS).n
    inf = informe_mod.construir(r, cfg, inst, consultas_validacion=consultas)
    texto = informe_mod.a_markdown(inf)
    print("\n" + texto)
    _guardar_informe(inf, texto, args)


def cmd_validar(args, cfg) -> None:
    inst = _cargar_instantanea(args, cfg)
    division = validacion_mod.dividir(inst, cfg)
    inicio, fin = division.diseno
    print(f"Periodo de diseno: {inicio} a {fin}")
    print(f"Periodo de validacion (sin tocar): {division.corte} a {division.fin}\n")

    r = backtest_mod.ejecutar(inst, cfg, inicio, fin)
    base = metricas_mod.resumir(r.curva, r.operaciones_df, cfg)
    print(
        f"Base: anualizada {base.rentabilidad_anualizada:+.2%}, "
        f"Sharpe {base.sharpe:.2f}, {base.n_operaciones} operaciones."
    )
    print("\nAnalisis de sensibilidad (puede tardar varios minutos)...")
    sens = validacion_mod.sensibilidad(inst, cfg, inicio, fin, base)

    consultas = validacion_mod.RegistroConsultas(RUTA_CONSULTAS).n
    inf = informe_mod.construir(
        r, cfg, inst, sensibilidad=sens, consultas_validacion=consultas
    )
    texto = informe_mod.a_markdown(inf)
    print("\n" + texto)
    _guardar_informe(inf, texto, args)


def cmd_informe(args, cfg) -> None:
    cmd_backtest(args, cfg)


def _guardar_informe(inf, texto: str, args) -> None:
    DIR_RESULTADOS.mkdir(parents=True, exist_ok=True)
    marca = "sintetico_" if inf.sintetico else ""
    ruta = DIR_RESULTADOS / f"informe_{marca}{date.today().isoformat()}.md"
    ruta.write_text(texto, encoding="utf-8")
    inf.curva.to_parquet(DIR_RESULTADOS / f"curva_{args.proveedor}.parquet", index=False)
    if not inf.operaciones.empty:
        inf.operaciones.to_parquet(
            DIR_RESULTADOS / f"operaciones_{args.proveedor}.parquet", index=False
        )
    if not inf.eventos.empty:
        inf.eventos.to_parquet(
            DIR_RESULTADOS / f"eventos_{args.proveedor}.parquet", index=False
        )
    if inf.sensibilidad is not None and not inf.sensibilidad.empty:
        inf.sensibilidad.to_parquet(
            DIR_RESULTADOS / f"sensibilidad_{args.proveedor}.parquet", index=False
        )
    print(f"\nInforme guardado en {ruta}")


# --------------------------------------------------------------------------
# Entrada
# --------------------------------------------------------------------------


def _fecha(texto: str) -> date:
    return date.fromisoformat(texto)


def construir_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="estrategia",
        description="Estrategia mixta (fundamental + tecnica) multi-mercado.",
    )
    p.add_argument(
        "--config", type=Path, default=None,
        help="directorio de configuracion (por defecto config/)",
    )
    p.add_argument(
        "--proveedor", choices=["sintetico", "yfinance"], default="sintetico",
        help="de donde salen los datos. 'sintetico' no necesita red y es el "
             "que se usa en los tests; 'yfinance' descarga datos reales.",
    )
    sub = p.add_subparsers(dest="comando", required=True)

    d = sub.add_parser("datos", help="descarga y cachea datos")
    d.add_argument("--anos", type=float, default=8.0, help="anos de historico")
    d.set_defaults(func=cmd_datos)

    f = sub.add_parser("foto", help="foto semanal de fundamentales y divisas")
    f.add_argument("--anos", type=float, default=8.0)
    f.add_argument("--forzar", action="store_true", help="rehacer la foto de esta semana")
    f.set_defaults(func=cmd_foto)

    u = sub.add_parser("universo", help="quien entra en el universo y por que no")
    u.add_argument("--fecha", type=_fecha, default=None)
    u.add_argument("--detalle", action="store_true")
    u.set_defaults(func=cmd_universo)

    s = sub.add_parser("senales", help="candidatas de la ultima revision")
    s.add_argument("--fecha", type=_fecha, default=None)
    s.add_argument("--detalle", action="store_true")
    s.set_defaults(func=cmd_senales)

    b = sub.add_parser("backtest", help="corre el backtest")
    b.add_argument(
        "--periodo", choices=["diseno", "validacion", "todo"], default="diseno",
        help="'validacion' abre el periodo reservado y anota la consulta",
    )
    b.set_defaults(func=cmd_backtest)

    v = sub.add_parser("validar", help="backtest de diseno mas analisis de sensibilidad")
    v.set_defaults(func=cmd_validar)

    i = sub.add_parser("informe", help="alias de backtest, guarda el informe")
    i.add_argument("--periodo", choices=["diseno", "validacion", "todo"], default="todo")
    i.set_defaults(func=cmd_informe)

    return p


def main(argv: list[str] | None = None) -> int:
    args = construir_parser().parse_args(argv)
    try:
        cfg = config_mod.cargar(args.config)
        args.func(args, cfg)
    except ErrorEstrategia as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("\nInterrumpido.", file=sys.stderr)
        return 130
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
