"""El sitio del research: una pagina autocontenida, sin JavaScript y sin CDN.

Lo que se publica en lalonja-trading.com en esta fase es el research, no datos de
nadie: fuentes por pais, el semaforo de licencias, la matriz y lo que se puede
construir con lo que hay. Es contenido propio, asi que se puede publicar hoy sin
ningun riesgo de licencia, que es mas de lo que se puede decir de casi cualquier
otra pagina de analisis bursatil.

**El semaforo se genera desde `config/fuentes.yaml`.** No es una comodidad: es lo
que impide que la pagina y el codigo se separen. Si alguien cambia el estado de
una fuente, el sitio lo dice en la siguiente publicacion sin que nadie tenga que
acordarse de editar un HTML. Y al reves: una fuente que aparece en verde en la
pagina es una fuente que el enrutador deja usar de verdad.

Colores: tres estados, no cuatro. La pregunta que se hace el lector es ternaria
—se puede usar, todavia no, nunca— y un semaforo de cuatro tonos es justo la
paleta que falla con daltonismo. Los tres tonos pasaron el validador en claro y
en oscuro; el par ambar/rojo queda en la banda 6-8 de separacion CVD, que es
legal solo con codificacion secundaria, asi que **el estado va siempre escrito**
al lado del color, nunca solo en color.
"""

from __future__ import annotations

import html
from datetime import date
from pathlib import Path

from .datos import licencias
from .datos.licencias import Ficha, Registro

# --------------------------------------------------------------------------
# Paleta
# --------------------------------------------------------------------------

#: Estados del semaforo. Validados con el comprobador de paletas en los dos
#: modos: banda de luminosidad, suelo de croma, separacion CVD y contraste.
#: Claro  #2a78d6 / #8f7f0e / #c93a5c  sobre #fcfcfb
#: Oscuro #3987e5 / #a8940f / #e2586b  sobre #1a1a19
_SEMAFORO = {
    "APPROVED": ("apta", "Se puede usar en producción"),
    "APPROVED_WITH_RESTRICTIONS": ("apta", "Se usa, con sus condiciones anotadas"),
    "DEVELOPMENT_ONLY": ("pendiente", "Solo desarrollo. En producción no arranca"),
    "NEEDS_REVIEW": ("pendiente", "Licencia sin resolver. No se instancia"),
    "REJECTED": ("no", "Sus términos la excluyen. No se instancia nunca"),
}

_PAIS = {
    "us": "🇺🇸 EE. UU.",
    "es": "🇪🇸 España",
    "br": "🇧🇷 Brasil",
    "in": "🇮🇳 India",
    "global": "🌍 Global",
}


def _e(t: object) -> str:
    return html.escape(str(t), quote=True)


# --------------------------------------------------------------------------
# Contenido que no sale del registro
# --------------------------------------------------------------------------

#: La matriz del §29. Cada celda: (marca, texto). Las marcas son las mismas que
#: en docs/data-matrix.md, y significan lo mismo.
MATRIZ: tuple[tuple[str, tuple[tuple[str, str], ...]], ...] = (
    ("Precios (OHLC)", (("no", "licenciado"), ("no", "licenciado"), ("no", "licenciado"), ("no", "licenciado"))),
    ("Volumen", (("no", "licenciado"), ("no", "licenciado"), ("no", "licenciado"), ("no", "licenciado"))),
    ("Estados financieros", (("si", "SEC EDGAR"), ("mas", "CNMV + IR"), ("si", "CVM"), ("falta", "sin fuente"))),
    ("Ratios fundamentales", (("si", "calculados"), ("mas", "calculados"), ("si", "calculados"), ("falta", "sin fuente"))),
    ("Operaciones de iniciados", (("si", "Forms 3/4/5"), ("mas", "CNMV"), ("si", "CVM vlmo"), ("no", "solo NSE/BSE"))),
    ("Posiciones cortas", (("si", "FINRA"), ("si", "CNMV"), ("falta", "sin fuente"), ("falta", "sin fuente"))),
    ("Dividendos", (("mas", "SEC 8-K"), ("mas", "CNMV"), ("mas", "CVM IPE"), ("falta", "sin fuente"))),
    ("Splits", (("mas", "SEC 8-K"), ("mas", "CNMV"), ("mas", "CVM IPE"), ("falta", "sin fuente"))),
    ("Operaciones corporativas", (("mas", "SEC 8-K"), ("mas", "CNMV"), ("mas", "CVM IPE"), ("falta", "sin fuente"))),
    ("Noticias", (("si", "GDELT"), ("si", "GDELT"), ("si", "GDELT"), ("si", "GDELT"))),
    ("Sentimiento", (("mas", "GDELT tono"), ("mas", "GDELT tono"), ("mas", "GDELT tono"), ("mas", "GDELT tono"))),
    ("Macro", (("si", "FRED + BM"), ("si", "BCE + BM"), ("si", "Banco Mundial"), ("si", "Banco Mundial"))),
    ("Divisas", (("si", "BCE"), ("si", "BCE"), ("si", "BCE"), ("si", "BCE"))),
    ("Índices", (("no", "S&P DJI"), ("no", "BME/SIX"), ("no", "B3"), ("no", "NSE/BSE"))),
    ("Materias primas", (("mas", "BM, mensual"), ("mas", "BM, mensual"), ("mas", "BM, mensual"), ("mas", "BM, mensual"))),
)

_MARCAS = {
    "si": ("✓", "apta", "disponible y con licencia aparentemente apta"),
    "mas": ("~", "pendiente", "disponible con restricción o trabajo extra"),
    "no": ("✗", "no", "existe, pero su licencia lo prohíbe"),
    "falta": ("—", "no", "no hay fuente"),
}

#: Las catorce capas del producto y si se encienden a coste cero.
CAPAS: tuple[tuple[str, bool, str], ...] = (
    ("Identidad de empresa", True, "Regulador"),
    ("Estados financieros", True, "Regulador"),
    ("Crecimiento", True, "Calculado"),
    ("Rentabilidad y márgenes", True, "Calculado"),
    ("Balance y solvencia", True, "Calculado"),
    ("Flujo de caja", True, "Calculado"),
    ("Valoración", False, "Requiere precios"),
    ("Análisis técnico", False, "Requiere precios"),
    ("Benchmark y alfa", False, "Requiere precios e índices"),
    ("Operaciones de iniciados", True, "Regulador"),
    ("Posiciones cortas", True, "FINRA y CNMV"),
    ("Hechos relevantes", True, "Regulador"),
    ("Noticias y tono", True, "GDELT"),
    ("Contexto macro y divisa", True, "BCE y Banco Mundial"),
)

#: Los siete puntos que hay que verificar antes de cobrarle a nadie.
VERIFICACION: tuple[tuple[str, str, str], ...] = (
    (
        "Que la SEC no restringe la reutilización comercial de EDGAR",
        "https://www.sec.gov/about/webmaster-frequently-asked-questions",
        "Se cae el mercado principal. Es el mayor riesgo del proyecto.",
    ),
    (
        "La nota legal de la CNMV, no solo la Ley 37/2007",
        "https://cnmv.es/portal/utilidades/notalegal.aspx",
        "Se cae España.",
    ),
    (
        "La licencia de cada dataset de CVM, uno a uno",
        "https://dados.cvm.gov.br/about",
        "Se cae Brasil, entero o por partes.",
    ),
    (
        "El aviso legal del BCE, con el texto literal de la condición de cita",
        "https://www.ecb.europa.eu/services/using-our-site/disclaimer/html/index.en.html",
        "Se cae la capa de divisas.",
    ),
    (
        "Los términos del Banco Mundial y el formato exacto de atribución",
        "https://datacatalog.worldbank.org/public-licenses",
        "Se cae la capa macro.",
    ),
    (
        "Los términos de GDELT, literales",
        "https://gdeltproject.org/about.html",
        "Se cae la capa de noticias.",
    ),
    (
        "Los términos de FINRA Data",
        "https://www.finra.org/finra-data/browse-catalog/equity-short-interest",
        "Se cae el short interest de EE. UU.",
    ),
)


# --------------------------------------------------------------------------
# Generacion
# --------------------------------------------------------------------------


def generar(registro: Registro | None = None, hoy: date | None = None) -> str:
    """La pagina completa, como una cadena."""
    reg = registro if registro is not None else licencias.cargar()
    fecha = hoy or date.today()
    p: list[str] = []

    p.append("<!doctype html>")
    p.append('<html lang="es"><head><meta charset="utf-8">')
    p.append('<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">')
    p.append("<title>La Lonja — Research de fuentes de datos</title>")
    p.append(
        '<meta name="description" content="Qué fuentes de datos bursátiles son '
        "gratuitas y legalmente utilizables en un producto comercial para EE. UU., "
        'España, Brasil e India.">'
    )
    p.append(f"<style>{_ESTILO}</style>")
    p.append("</head><body>")

    p.append(_cabecera(fecha))
    p.append('<main class="envoltura">')
    p.append(_aviso_verificacion())
    p.append(_respuesta())
    p.append(_regulador_bolsa())
    p.append(_puede_no_puede())
    p.append(_semaforo(reg))
    p.append(_matriz())
    p.append(_capas())
    p.append(_huecos())
    p.append(_verificacion())
    p.append("</main>")
    p.append(_pie(reg, fecha))
    p.append("</body></html>")
    return "\n".join(p)


def escribir(destino: Path | str = "sitio/index.html", **kwargs) -> Path:
    """Genera el sitio y lo deja en disco."""
    ruta = Path(destino)
    ruta.parent.mkdir(parents=True, exist_ok=True)
    ruta.write_text(generar(**kwargs), encoding="utf-8")
    return ruta


# --------------------------------------------------------------------------
# Secciones
# --------------------------------------------------------------------------


def _cabecera(fecha: date) -> str:
    enlaces = (
        ("#respuesta", "La respuesta"),
        ("#fuentes", "Fuentes"),
        ("#matriz", "Matriz"),
        ("#capas", "Capas"),
        ("#verificacion", "Verificación"),
    )
    nav = "".join(f'<a href="{h}">{_e(t)}</a>' for h, t in enlaces)
    return (
        '<header class="cab"><div class="envoltura cab-int">'
        '<div class="marca"><span class="logo">La Lonja</span>'
        f'<span class="fecha">Research de fuentes · {fecha:%d/%m/%Y}</span></div>'
        f'<nav class="nav">{nav}</nav>'
        "</div></header>"
    )


def _aviso_verificacion() -> str:
    return (
        '<aside class="aviso grave" id="aviso">'
        "<h2>Nada de esto está verificado contra la fuente primaria</h2>"
        "<p>El entorno donde se hizo este research tiene el egreso de red bloqueado "
        "por política. Comprobado al escribirlo:</p>"
        "<pre><code>$ curl -sS https://www.sec.gov/os/webmaster-faq\n"
        "curl: (56) CONNECT tunnel failed, response 403</code></pre>"
        "<p>La búsqueda web sí funciona, así que se ha podido <strong>localizar</strong> "
        "cada término de uso y formarse un hallazgo, pero <strong>no leerlo</strong>. "
        "Todo lo que sigue está marcado <span class=\"marca-verif\">PROVISIONAL</span>: "
        "el enlace oficial está, el texto no se ha leído.</p>"
        "<p>Un <em>provisional</em> favorable no es permiso para usar una fuente con "
        "clientes de pago. Es una hipótesis con un sitio donde comprobarla, y la lista "
        'de las que hay que comprobar está <a href="#verificacion">al final</a>.</p>'
        "<p class=\"ejemplo\"><strong>Por qué esto no es exceso de celo.</strong> Durante "
        "el research, una búsqueda sobre el copyright de la SEC devolvió un texto rotundo "
        "que prohibía «strictly» la redistribución de datos de EDGAR. Al mirar de dónde "
        "salía, resultó venir de los <em>filings</em> de una empresa llamada EDGAR Online "
        "Inc. — no de ninguna política de la SEC. Escrito sin comprobar la procedencia, "
        "este documento habría descartado la fuente más importante del proyecto por "
        "confundir a una empresa con el regulador.</p>"
        "</aside>"
    )


def _respuesta() -> str:
    return (
        '<section id="respuesta">'
        "<h2>La pregunta</h2>"
        '<p class="pregunta">¿Se puede construir una aplicación de análisis bursátil '
        "para EE. UU., España, Brasil e India usando únicamente fuentes gratuitas y sin "
        "pagar por <i>market data</i>?</p>"
        '<p class="respuesta-corta">Sí, pero no la aplicación que uno se imagina.</p>'
        "<p>Los fundamentales son gratis y son legales: los publican los reguladores. "
        "Los precios no lo son en ninguno de los cuatro mercados, y con ellos se cae "
        "la valoración, el análisis técnico y la comparación con índices. Queda en pie "
        "un analista de fundamentales, gobierno corporativo, flujos, iniciados, macro, "
        "divisas y noticias — que son <strong>once de las catorce capas</strong> del "
        "producto, y cuestan cero euros.</p>"
        "</section>"
    )


def _regulador_bolsa() -> str:
    filas = (
        ("🇺🇸 EE. UU.", "SEC EDGAR", "apta", "NYSE / Nasdaq", "no"),
        ("🇪🇸 España", "CNMV", "apta", "BME", "no"),
        ("🇧🇷 Brasil", "CVM", "apta", "B3", "no"),
        ("🇮🇳 India", "SEBI", "pendiente", "NSE / BSE", "no"),
    )
    cuerpo = "".join(
        f"<tr><td>{_e(pais)}</td>"
        f'<td><span class="punto {er}"></span>{_e(reg)}</td>'
        f'<td><span class="punto {eb}"></span>{_e(bolsa)}</td></tr>'
        for pais, reg, er, bolsa, eb in filas
    )
    return (
        '<section id="patron">'
        "<h2>El patrón que explica casi todo</h2>"
        '<blockquote class="clave">El regulador publica porque su mandato es la '
        "transparencia. La bolsa vende porque el <i>market data</i> es su negocio.</blockquote>"
        '<div class="desliza"><table class="tabla">'
        "<thead><tr><th>Mercado</th><th>Regulador (filings públicos)</th>"
        "<th>Bolsa (market data)</th></tr></thead>"
        f"<tbody>{cuerpo}</tbody></table></div>"
        "<p>Por eso la jerarquía de fuentes no es una preferencia estética. Los "
        "fundamentales brasileños no salen de B3: salen de la CVM, que los publica en "
        "abierto y no los prohíbe. Y por eso India es el mercado que no sale — es el "
        "único donde el regulador no publica datos estructurados y el dato público "
        "solo se distribuye por un canal que prohíbe recolectarlo.</p>"
        "</section>"
    )


def _puede_no_puede() -> str:
    si = (
        "Estados financieros completos, con fecha real de publicación",
        "Crecimiento, márgenes, ROE / ROA / ROIC",
        "Balance, solvencia y cobertura de intereses",
        "Flujo de caja y FCF, calculados en casa",
        "Operaciones de iniciados en EE. UU., España y Brasil",
        "Posiciones cortas en EE. UU. y España",
        "Hechos relevantes y participaciones significativas",
        "Macro de los cuatro países y divisas",
        "Noticias, recuento, tendencia y tono",
    )
    no = (
        "Enseñar un precio o un gráfico de cotización",
        "Capitalización bursátil",
        "PER, EV/EBITDA, P/B, P/S, FCF yield",
        "Cualquier indicador técnico",
        "Comparación con índice, alfa, beta, drawdown",
        "Technical Score",
        "India, entera",
    )
    return (
        '<section id="alcance">'
        "<h2>Qué se puede y qué no</h2>"
        '<div class="dos">'
        '<div class="col apta"><h3>Con fuentes a 0 €</h3><ul>'
        + "".join(f"<li>{_e(x)}</li>" for x in si)
        + "</ul></div>"
        '<div class="col no"><h3>Sin licencia de datos de mercado</h3><ul>'
        + "".join(f"<li>{_e(x)}</li>" for x in no)
        + "</ul></div></div>"
        "<p class=\"nota\">Conviene que quede claro por qué se cae la columna de la "
        "derecha: <strong>no es una limitación técnica, es de licencia.</strong> El "
        "código para calcular todo eso está escrito y probado. Lo que falta es el "
        "derecho a alimentarlo.</p>"
        "</section>"
    )


def _semaforo(reg: Registro) -> str:
    orden = {"apta": 0, "pendiente": 1, "no": 2}
    fichas = sorted(
        reg.fuentes,
        key=lambda f: (orden[_SEMAFORO[f.status][0]], f.tier, f.priority, f.name),
    )
    tarjetas = "".join(_tarjeta_fuente(f) for f in fichas)
    n_apta = sum(1 for f in reg.fuentes if _SEMAFORO[f.status][0] == "apta")
    n_pend = sum(1 for f in reg.fuentes if _SEMAFORO[f.status][0] == "pendiente")
    n_no = sum(1 for f in reg.fuentes if _SEMAFORO[f.status][0] == "no")
    return (
        '<section id="fuentes">'
        "<h2>El semáforo de fuentes</h2>"
        "<p>Las {n} fuentes investigadas, con su estado, su licencia y el enlace a sus "
        "términos oficiales. Esta tabla no está escrita a mano: <strong>se genera desde "
        "el mismo fichero que el código obedece al arrancar</strong>, así que una fuente "
        "que aparezca aquí como apta es una fuente que el sistema deja usar de "
        "verdad.</p>".format(n=len(reg.fuentes))
        + '<div class="leyenda">'
        f'<span class="clave-l"><span class="punto apta"></span>{n_apta} se pueden usar</span>'
        f'<span class="clave-l"><span class="punto pendiente"></span>{n_pend} todavía no</span>'
        f'<span class="clave-l"><span class="punto no"></span>{n_no} nunca</span>'
        "</div>"
        f'<div class="fuentes">{tarjetas}</div>'
        "</section>"
    )


def _tarjeta_fuente(f: Ficha) -> str:
    estado, explicacion = _SEMAFORO[f.status]
    pais = _PAIS.get(f.country, f.country)
    campos = [
        ("Uso comercial", f.commercial_use),
        ("Almacenar", f.storage_allowed),
        ("Redistribuir", f.redistribution_allowed),
        ("Atribución", f.attribution_required),
    ]
    filas = "".join(
        f"<div class=\"campo\"><dt>{_e(k)}</dt><dd>{_valor(v)}</dd></div>"
        for k, v in campos
    )
    terminos = (
        f'<a class="terminos" href="{_e(f.terms_url)}" rel="noopener">Términos oficiales ↗</a>'
        if f.terms_url
        else '<span class="terminos ninguno">Sin términos localizables</span>'
    )
    verif = (
        '<span class="verif ok">verificado</span>'
        if f.verificada
        else f'<span class="verif">{_e(f.verification.lower())}</span>'
    )
    nota = " ".join(f.notes.split())
    return (
        f'<article class="fuente {estado}">'
        f'<div class="fuente-cab">'
        f'<h3><span class="punto {estado}"></span>{_e(f.name)}</h3>'
        f'<div class="fuente-meta">'
        f'<span class="pais">{_e(pais)}</span>'
        f'<span class="tier">Tier {f.tier}</span>'
        f"</div></div>"
        f'<p class="estado"><code>{_e(f.status)}</code> — {_e(explicacion)}</p>'
        f'<dl class="campos">{filas}</dl>'
        f'<p class="nota-fuente">{_e(nota)}</p>'
        f'<p class="meta">{terminos} {verif}</p>'
        f"</article>"
    )


def _valor(v: object) -> str:
    if v is True:
        return '<span class="si">sí</span>'
    if v is False or v is None:
        return '<span class="nd">—</span>'
    texto = str(v)
    if texto in ("si", "sí"):
        return '<span class="si">sí</span>'
    if texto == "no":
        return '<span class="nop">no</span>'
    if texto.startswith("no_localizad"):
        return '<span class="nd">no localizado</span>'
    return f'<span class="otro">{_e(texto.replace("_", " "))}</span>'


def _matriz() -> str:
    cuerpo = []
    for dato, celdas in MATRIZ:
        tds = []
        for marca, texto in celdas:
            simbolo, estado, titulo = _MARCAS[marca]
            tds.append(
                f'<td class="celda {estado}" title="{_e(titulo)}">'
                f'<span class="simbolo">{simbolo}</span>'
                f'<span class="fuente-celda">{_e(texto)}</span></td>'
            )
        cuerpo.append(f"<tr><th scope=\"row\">{_e(dato)}</th>{''.join(tds)}</tr>")
    leyenda = "".join(
        f'<span class="clave-l"><span class="simbolo {est}">{sim}</span>{_e(txt)}</span>'
        for sim, est, txt in _MARCAS.values()
    )
    return (
        '<section id="matriz">'
        "<h2>La matriz: qué dato, en qué país, de qué fuente</h2>"
        f'<div class="leyenda">{leyenda}</div>'
        '<div class="desliza"><table class="tabla matriz">'
        "<thead><tr><th>Dato</th><th>🇺🇸 EE. UU.</th><th>🇪🇸 España</th>"
        "<th>🇧🇷 Brasil</th><th>🇮🇳 India</th></tr></thead>"
        f"<tbody>{''.join(cuerpo)}</tbody></table></div>"
        "<p class=\"nota\">Las dos primeras filas llevan «existe, pero su licencia lo "
        "prohíbe» y no «no hay fuente», y la diferencia importa: el dato se descarga con "
        "dos líneas de Python. Lo que falta no es el dato, es el derecho a usarlo. Un "
        "hueco se arregla buscando mejor; una prohibición se arregla firmando.</p>"
        "</section>"
    )


def _capas() -> str:
    encendidas = sum(1 for _, ok, _ in CAPAS if ok)
    items = "".join(
        f'<li class="{"apta" if ok else "no"}">'
        f'<span class="punto {"apta" if ok else "no"}"></span>'
        f"<span class=\"capa\">{_e(nombre)}</span>"
        f'<span class="dep">{_e(dep)}</span></li>'
        for nombre, ok, dep in CAPAS
    )
    return (
        '<section id="capas">'
        "<h2>Las capas del producto</h2>"
        f'<p class="grande"><strong>{encendidas} de {len(CAPAS)}</strong> se encienden '
        "a coste cero.</p>"
        f'<ul class="capas">{items}</ul>'
        "<p class=\"nota\">Las tres que no dependen todas del mismo dato que falta, así "
        "que <strong>una sola licencia las enciende las tres</strong> — y de paso, "
        "India. Eso es lo que hace que la hoja de ruta sea corta.</p>"
        "</section>"
    )


def _huecos() -> str:
    filas = (
        ("Precios y volumen", "los 4 mercados", "Licencia EOD comercial", "~20–100 €/mes"),
        ("Valoración, técnico y benchmark", "los 4", "Consecuencia directa de la anterior", "—"),
        ("India entera", "🇮🇳", "La misma licencia, o IR empresa a empresa", "incluido"),
        ("Estados financieros de España", "🇪🇸", "Extracción sobre IPP e IR", "~2 semanas"),
        ("Cortos en Brasil e India", "🇧🇷 🇮🇳", "Sin vía localizada", "—"),
        ("Índices y benchmarks", "los 4", "Licencia de índices", "miles €/mes"),
    )
    cuerpo = "".join(
        f"<tr><td>{_e(a)}</td><td>{_e(b)}</td><td>{_e(c)}</td><td>{_e(d)}</td></tr>"
        for a, b, c, d in filas
    )
    return (
        '<section id="huecos">'
        "<h2>Los huecos, y lo que cuesta taparlos</h2>"
        '<div class="desliza"><table class="tabla">'
        "<thead><tr><th>Hueco</th><th>Dónde</th><th>Se tapa con</th><th>Coste</th></tr></thead>"
        f"<tbody>{cuerpo}</tbody></table></div>"
        "<p>Los tres primeros <strong>son el mismo hueco</strong>. El producto no "
        "redistribuye la serie de precios: muestra puntuaciones y métricas derivadas. "
        "Eso encaja en una licencia de uso derivado sin redistribución, que cuesta "
        "decenas de euros al mes y no miles, y que además suele traer India dentro.</p>"
        "<p class=\"nota\">Con una salvedad que conviene no diluir: esa distinción "
        "<strong>no</strong> convierte una fuente gratuita no comercial en utilizable. "
        "Yahoo sigue fuera, porque su licencia es personal, y una licencia personal no "
        "se arregla usando el dato solo por dentro. Lo que la distinción cambia es el "
        "precio de la licencia que sí hay que comprar.</p>"
        "</section>"
    )


def _verificacion() -> str:
    items = "".join(
        f"<li><h3>{_e(que)}</h3>"
        f'<p class="riesgo">{_e(riesgo)}</p>'
        f'<a href="{_e(url)}" rel="noopener">{_e(url)} ↗</a></li>'
        for que, url, riesgo in VERIFICACION
    )
    return (
        '<section id="verificacion">'
        "<h2>Lo que hay que verificar antes de cobrarle a nadie</h2>"
        "<p>Siete páginas web. Media jornada de trabajo. Y es lo único que separa este "
        "research de ser una opinión informada.</p>"
        f'<ol class="verificar">{items}</ol>'
        "</section>"
    )


def _pie(reg: Registro, fecha: date) -> str:
    pendientes = len(reg.pendientes_de_verificar())
    return (
        '<footer class="pie"><div class="envoltura">'
        "<p><strong>La Lonja</strong> — research de fuentes de datos para análisis "
        "bursátil. Documento propio. No redistribuye datos de terceros.</p>"
        f"<p>Generado el {fecha:%d/%m/%Y} desde <code>config/fuentes.yaml</code>. "
        f"<strong>{pendientes} fuentes</strong> en uso o previstas siguen sin verificar "
        "contra su fuente primaria.</p>"
        "<p class=\"descargo\">Esto no es asesoramiento de inversión, ni asesoramiento "
        "legal. El análisis de licencias que hay aquí es una lectura de buena fe hecha "
        "por búsqueda web, no por un abogado, y está expresamente marcada como no "
        "verificada. Antes de construir un negocio encima, que lo mire alguien que "
        "cobre por mirarlo.</p>"
        "</div></footer>"
    )


# --------------------------------------------------------------------------
# Estilo
# --------------------------------------------------------------------------

_ESTILO = """
:root {
  color-scheme: light;
  --plano: #f9f9f7; --sup: #fcfcfb; --sup2: #f2f2ee;
  --tinta: #0b0b0b; --tinta2: #52514e; --tinta3: #898781;
  --borde: rgba(11,11,11,0.10); --borde2: rgba(11,11,11,0.18);
  --apta: #2a78d6; --pendiente: #8f7f0e; --no: #c93a5c;
  --apta-suave: rgba(42,120,214,0.08);
  --pendiente-suave: rgba(143,127,14,0.10);
  --no-suave: rgba(201,58,92,0.08);
}
@media (prefers-color-scheme: dark) {
  :root:where(:not([data-theme="light"])) {
    color-scheme: dark;
    --plano: #0d0d0d; --sup: #1a1a19; --sup2: #232322;
    --tinta: #ffffff; --tinta2: #c3c2b7; --tinta3: #898781;
    --borde: rgba(255,255,255,0.10); --borde2: rgba(255,255,255,0.18);
    --apta: #3987e5; --pendiente: #a8940f; --no: #e2586b;
    --apta-suave: rgba(57,135,229,0.12);
    --pendiente-suave: rgba(168,148,15,0.14);
    --no-suave: rgba(226,88,107,0.12);
  }
}
* { box-sizing: border-box; }
html { scroll-behavior: smooth; }
body {
  margin: 0; background: var(--plano); color: var(--tinta);
  font: 16px/1.65 system-ui, -apple-system, "Segoe UI", sans-serif;
  -webkit-text-size-adjust: 100%;
}
.envoltura { max-width: 980px; margin: 0 auto; padding: 0 20px; }

/* Cabecera */
.cab {
  border-bottom: 1px solid var(--borde); background: var(--sup);
  position: sticky; top: 0; z-index: 10;
  padding-top: env(safe-area-inset-top, 0px);
}
.cab-int {
  display: flex; align-items: center; justify-content: space-between;
  gap: 16px; flex-wrap: wrap; padding-top: 12px; padding-bottom: 12px;
}
.marca { display: flex; align-items: baseline; gap: 12px; flex-wrap: wrap; }
.logo { font-size: 1.05rem; font-weight: 700; letter-spacing: -0.02em; }
.fecha { font-size: .78rem; color: var(--tinta3); }
.nav { display: flex; gap: 16px; flex-wrap: wrap; font-size: .85rem; }
.nav a { color: var(--tinta2); text-decoration: none; }
.nav a:hover { color: var(--apta); text-decoration: underline; }

main.envoltura { padding-bottom: calc(64px + env(safe-area-inset-bottom, 0px)); }
section { margin: 56px 0; scroll-margin-top: 90px; }
h2 { font-size: 1.45rem; margin: 0 0 14px; letter-spacing: -0.02em; line-height: 1.25; }
h3 { font-size: .98rem; margin: 0 0 6px; letter-spacing: -0.01em; }
p { margin: 0 0 14px; }
a { color: var(--apta); }
code { font: .86em ui-monospace, SFMono-Regular, Menlo, monospace; }

/* Aviso */
.aviso {
  margin: 36px 0; padding: 22px 24px; border-radius: 12px;
  background: var(--sup); border: 1px solid var(--borde);
  border-left: 4px solid var(--no);
}
.aviso h2 { font-size: 1.15rem; color: var(--no); }
.aviso p { font-size: .93rem; color: var(--tinta2); }
.aviso strong, .aviso em { color: var(--tinta); }
.aviso pre {
  background: var(--sup2); border-radius: 8px; padding: 12px 14px;
  overflow-x: auto; font-size: .8rem; margin: 0 0 14px;
}
.aviso .ejemplo {
  margin: 18px 0 0; padding-top: 16px; border-top: 1px solid var(--borde);
  font-size: .88rem;
}
.marca-verif {
  font-size: .72rem; font-weight: 700; letter-spacing: .06em;
  background: var(--pendiente-suave); color: var(--pendiente);
  padding: 2px 7px; border-radius: 4px; white-space: nowrap;
}

/* Respuesta */
.pregunta {
  font-size: 1.3rem; line-height: 1.35; letter-spacing: -0.015em;
  color: var(--tinta2); margin-bottom: 18px;
}
.respuesta-corta {
  font-size: 2.1rem; font-weight: 650; line-height: 1.15;
  letter-spacing: -0.03em; margin: 0 0 20px;
}
blockquote.clave {
  margin: 20px 0; padding: 18px 22px; border-radius: 12px;
  background: var(--apta-suave); border-left: 4px solid var(--apta);
  font-size: 1.08rem; font-weight: 550; line-height: 1.45; letter-spacing: -0.01em;
}
.grande { font-size: 1.3rem; letter-spacing: -0.01em; }
.nota { font-size: .9rem; color: var(--tinta2); }
.nota strong { color: var(--tinta); }

/* Punto de estado: siempre acompanado del texto, nunca solo */
.punto {
  width: 10px; height: 10px; border-radius: 50%; flex: none;
  display: inline-block; margin-right: 7px; vertical-align: baseline;
}
.punto.apta { background: var(--apta); }
.punto.pendiente { background: var(--pendiente); }
.punto.no { background: var(--no); }

/* Tablas */
.desliza { overflow-x: auto; margin: 0 0 14px; -webkit-overflow-scrolling: touch; }
.tabla { border-collapse: collapse; width: 100%; font-size: .9rem; min-width: 480px; }
.tabla th, .tabla td {
  text-align: left; padding: 9px 12px; border-bottom: 1px solid var(--borde);
  vertical-align: top;
}
.tabla thead th {
  color: var(--tinta3); font-weight: 600; font-size: .76rem;
  text-transform: uppercase; letter-spacing: .05em; white-space: nowrap;
}
.tabla tbody tr:hover { background: var(--sup); }
.matriz th[scope="row"] { font-weight: 550; }
.celda .simbolo { font-weight: 700; margin-right: 6px; }
.celda.apta .simbolo { color: var(--apta); }
.celda.pendiente .simbolo { color: var(--pendiente); }
.celda.no .simbolo { color: var(--no); }
.fuente-celda { color: var(--tinta2); font-size: .85rem; }

/* Leyendas */
.leyenda {
  display: flex; gap: 20px; flex-wrap: wrap; margin: 0 0 16px;
  font-size: .85rem; color: var(--tinta2);
}
.clave-l { display: inline-flex; align-items: center; gap: 4px; }
.leyenda .simbolo { font-weight: 700; margin-right: 3px; }
.leyenda .simbolo.apta { color: var(--apta); }
.leyenda .simbolo.pendiente { color: var(--pendiente); }
.leyenda .simbolo.no { color: var(--no); }

/* Dos columnas */
.dos { display: grid; gap: 16px; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); }
.col {
  background: var(--sup); border: 1px solid var(--borde);
  border-radius: 12px; padding: 18px 20px;
}
.col.apta { border-top: 3px solid var(--apta); }
.col.no { border-top: 3px solid var(--no); }
.col h3 { color: var(--tinta2); font-size: .82rem; text-transform: uppercase; letter-spacing: .05em; }
.col ul { margin: 0; padding-left: 20px; font-size: .92rem; }
.col li { margin-bottom: 6px; }

/* Fichas de fuente */
.fuentes { display: grid; gap: 12px; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); }
.fuente {
  background: var(--sup); border: 1px solid var(--borde);
  border-radius: 12px; padding: 16px 18px; border-left: 4px solid var(--borde2);
}
.fuente.apta { border-left-color: var(--apta); }
.fuente.pendiente { border-left-color: var(--pendiente); }
.fuente.no { border-left-color: var(--no); }
/* La cabecera de la ficha no se desmonta cuando el nombre es largo: el punto
   viaja con el titulo, y pais y tier van en su propia linea. */
.fuente-cab { margin-bottom: 8px; }
.fuente-cab h3 { margin: 0 0 3px; font-size: 1rem; line-height: 1.3; }
.fuente-cab h3 .punto { margin-right: 8px; }
.fuente-meta { display: flex; align-items: center; gap: 8px; }
.pais { font-size: .78rem; color: var(--tinta3); }
.tier {
  font-size: .7rem; font-weight: 700; letter-spacing: .04em;
  color: var(--tinta3); border: 1px solid var(--borde2);
  border-radius: 4px; padding: 1px 6px; margin-left: auto; white-space: nowrap;
}
.estado { font-size: .82rem; color: var(--tinta2); margin: 0 0 12px; }
.estado code { font-size: .78rem; font-weight: 600; }
.campos { display: grid; grid-template-columns: repeat(auto-fit, minmax(120px, 1fr)); gap: 8px 12px; margin: 0 0 12px; }
.campo dt { font-size: .68rem; color: var(--tinta3); text-transform: uppercase; letter-spacing: .05em; }
.campo dd { margin: 1px 0 0; font-size: .85rem; }
.campo .si { color: var(--apta); font-weight: 600; }
.campo .nop { color: var(--no); font-weight: 600; }
.campo .nd { color: var(--tinta3); }
.campo .otro { color: var(--pendiente); font-weight: 550; }
.nota-fuente { font-size: .82rem; color: var(--tinta2); margin: 0 0 12px; line-height: 1.55; }
.meta { margin: 0; font-size: .76rem; display: flex; gap: 10px; flex-wrap: wrap; align-items: center; }
.terminos { color: var(--apta); text-decoration: none; }
.terminos:hover { text-decoration: underline; }
.terminos.ninguno { color: var(--tinta3); font-style: italic; }
.verif {
  font-size: .66rem; font-weight: 700; letter-spacing: .06em; text-transform: uppercase;
  background: var(--pendiente-suave); color: var(--pendiente);
  padding: 2px 6px; border-radius: 4px;
}
.verif.ok { background: var(--apta-suave); color: var(--apta); }

/* Capas */
.capas { list-style: none; padding: 0; margin: 0 0 14px; display: grid; gap: 6px;
         grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); }
.capas li {
  display: flex; align-items: center; gap: 4px; padding: 9px 14px;
  background: var(--sup); border: 1px solid var(--borde); border-radius: 8px;
  font-size: .9rem;
}
.capas li.no { background: var(--no-suave); }
.capas .capa { flex: 1; }
.capas .dep { font-size: .75rem; color: var(--tinta3); text-align: right; }

/* Verificacion */
.verificar { margin: 0; padding-left: 24px; }
.verificar li { margin-bottom: 20px; }
.verificar h3 { margin-bottom: 4px; }
.verificar .riesgo { font-size: .85rem; color: var(--no); margin: 0 0 4px; }
.verificar a { font-size: .8rem; word-break: break-all; }

/* Pie */
.pie {
  border-top: 1px solid var(--borde); background: var(--sup);
  padding: 32px 0 calc(40px + env(safe-area-inset-bottom, 0px));
  color: var(--tinta2); font-size: .86rem;
}
.pie .descargo { color: var(--tinta3); font-size: .8rem; margin-top: 18px; }

@media (max-width: 560px) {
  body { font-size: 15px; }
  .respuesta-corta { font-size: 1.65rem; }
  .pregunta { font-size: 1.1rem; }
  .cab { position: static; }
  section { margin: 40px 0; }
}
@media (prefers-reduced-motion: reduce) { html { scroll-behavior: auto; } }
"""
