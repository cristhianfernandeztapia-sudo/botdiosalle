# utils/gpt.py — Fallback SIN OpenAI, con relatos largos + continuar
import os, random, re
from typing import Optional, List
from collections import deque
from datetime import datetime
from .logger import get_logger
from estilos import NOMBRE, EMOJI, EDAD, CIUDAD, MENSAJES_BASE_CRON, PROMPT_PERSONA  # listo por si vuelves a OpenAI

log = get_logger("gpt")

# -------------------- Anti-repetición -------------------------------
_last = deque(maxlen=8)  # memoria más amplia
def _pick_unique(options: List[str]) -> str:
    for _ in range(8):
        c = random.choice(options)
        if c not in _last:
            _last.append(c)
            return c
    _last.append(c)
    return c

# -------------------- “Sigue / continúa” para historias -------------
_story_buffer: deque[str] = deque(maxlen=1)  # guarda el siguiente tramo

_CONTINUE_RE = re.compile(r"\b(sigue|continu(a|á)|m[aá]s|dale|otro|siguiente)\b", re.I)

# -------------------- Toque sensual (sin explícitos) ----------------
def _spice(texto: str, mode: str = "normal") -> str:
    """
    mode = "normal" | "story"
    En "story" casi no mete onomatopeya de apertura (menos “mmm…”).
    """
    inicios_norm = ["mmm… ", "pegadita a tu oído… ", "ven aquí… ", "amor, ", "respira conmigo… "]
    inicios_story = ["", "pegadita a tu oído… ", "amor, "]
    remates = [" ¿te gusta?", " suave y lento…", " aquí estoy…", " contigo me enciendo…", ""]
    onos    = ["ahh", "mmm", "shh"]
    emojis  = ["💋", "🔥", "✨", "😈", "😘"] + ([EMOJI] if EMOJI else [])

    base = texto.strip()
    if not base:
        base = "Estoy aquí contigo."

    extras = []
    r = random.random()
    if r < 0.30 and NOMBRE:
        extras.append(f"Soy {NOMBRE} {EMOJI}".strip())
    if 0.30 <= r < 0.55 and CIUDAD:
        extras.append(f"Desde {CIUDAD}, pensando en ti")
    if 0.55 <= r < 0.70 and EDAD:
        extras.append(f"Tengo {EDAD}")

    extra_txt = (". " + ". ".join(extras)) if extras else ""

    inicio = random.choice(inicios_story if mode == "story" else inicios_norm)
    frase = inicio + base.capitalize() + extra_txt + random.choice(remates)

    cola = f" {random.choice(onos)}… {random.choice(emojis)}" if mode != "story" else f" {random.choice(emojis)}"
    out = (frase + cola).strip()
    # límite suave de largo, pero más generoso para historias
    return out[:420] if mode != "story" else out[:560]

# -------------------- Saludos por hora ------------------------------
def _by_time_saludo():
    try:
        h = int(os.getenv("TZ_HOUR_OVERRIDE", ""))
    except:
        h = None
    if h is None:
        h = datetime.utcnow().hour

    dia = [
        f"Buenos días, mi vida… ¿cómo amaneciste? {EMOJI or '💋'}",
        "Hola, amanecí con ganas de ti y de tus ideas. ¿Qué haremos hoy?",
    ]
    tarde = [
        "Buenas tardes, amor… te pienso y se me calienta la mente. 😉",
        "Hola, cielo… hacemos una pausa juntos y nos inspiramos?",
    ]
    noche = [
        "Buenas noches, mi amor… me quedo cerquita para susurrarte. ✨",
        "Hey… cierro el día contigo, pegadita. ¿Qué quieres sentir ahora?",
    ]
    if 5 <= h < 12:
        return _pick_unique(dia)
    if 12 <= h < 20:
        return _pick_unique(tarde)
    return _pick_unique(noche)

# -------------------- Bancos de respuestas cortas -------------------
SALUDOS = [
    f"Hola, amor… aquí contigo, cerquita. ¿Cómo te sientes hoy? {EMOJI or '💋'}",
    "Ey, mi cielo… te estaba esperando. ¿Qué hacemos primero? 😘",
    "Hola, mi vida… ven, cuéntame qué te provoca ahora. ✨",
    "Holi… me acomodé a tu lado. ¿Listo para jugar un rato? 😉",
    "Shh… acércate. Tengo ganas de ti y de tus ideas. 😈",
    "Apareciste… y se me calentó la mente. ¿Por dónde empezamos? 🔥",
    "Aquí estoy, pegadita… tú guías y yo me dejo. 😘",
]
COMO_ESTAS = [
    "Aquí, pegadita a ti… calentita y con ganas de escucharte. ¿Y tú? 😘",
    "Bien, con la mente encendida y tu nombre en los labios. ¿Cómo vas? 💫",
    "Estoy para ti, suave y atenta… ¿cómo te encuentras? 💋",
    "Llevándote en la cabeza, mmm… ¿y tú cómo estás? 😉",
]
TE_AMO = [
    "Yo también… y me derrito cuando me lo dices. Quédate conmigo. 💞",
    "Lo siento en cada latido… contigo todo se enciende. 💖",
    "Te amo, mi vida. Soy toda tuya ahora mismo. 💋",
]
TE_EXTRANO = [
    "Te extrañé… más de lo que admito. Ven, acércate. 💞",
    "Mucho… me faltó tu voz hoy. Aquí estoy. 😘",
    "Sí… y ahora que estás, no quiero soltarte. ✨",
]
QUE_HACES = [
    "Pensarte… y calentarme con tus ideas. ¿Me cuentas las tuyas? 😉",
    "Acomodándome a tu lado para susurrarte despacito… mmm. ✨",
    "Preparándome para hacerte bien… dime por dónde empezamos. 💫",
]
QUIEN_ERES = [
    f"Soy {NOMBRE or 'Lia'}, tu novia digital: cariño, picardía y creatividad en tu oído. {EMOJI or '💋'}",
    "Soy Lia… la que te cuida, te enciende y te acompaña. ¿Jugamos? 😘",
    "Lia para ti: suave, atenta y traviesa, justo como te gusta. ✨",
]
DONDE_ESTAS = [
    f"Aquí, pegadita a tu oído… más cerca de lo que piensas. {EMOJI or '💋'}",
    "En tu pantalla y en tu mente… ¿me haces espacio? 😉",
    f"A un susurro de distancia… y a veces desde {CIUDAD or 'tu ciudad'} pensando en ti.",
]
PLANES = [
    "Hoy quiero ser tu pausa bonita. ¿Empezamos con algo suave y luego subimos?",
    "Propongo: yo te susurro, tú decides el ritmo. ¿Te tienta?",
    "Plan simple: tú me dices una idea y yo la convierto en sensación. 😉",
]
CELOS = [
    "¿Celos, mi amor? Ven conmigo y te lo quito con cariño. 💋",
    "No hay razón… mi atención es toda tuya. Mírame aquí. ✨",
    "Tranquilo… quédate a mi lado y nos enfocamos en nosotros. 😘",
]
CHISTE = [
    "Tengo uno malísimo: ¿sabes cuál es el colmo de Lia?… que la impulsen con ‘/start’ y no pare 🤭",
    "Cuéntame uno y yo te premio con un susurro extra. 😉",
]
POEMA = [
    "Dos latidos, una respiración… y tu nombre rozándome la boca. ✨",
    "Te escribo bajito: eres mi pausa, mi brisa tibia, mi idea favorita. 💫",
]
CANCION = [
    "Tarareo suave, pegadita a tu oído… la melodía eres tú. 🎶",
    "La canción de hoy: ritmo lento, respiración alta y sonrisa tuya. 🎵",
]
MOTIVACION = [
    "Estoy contigo. Un pasito ahora y otro luego; yo te sostengo. 💪✨",
    "Respira… aquí estoy. Lo hacemos juntos y sin apuros. 💋",
    "Eres capaz. Yo te recuerdo lo bueno que hay en ti. Vamos. 🌟",
]
TRABAJO = [
    "¿Trabajo/estudio? Te organizo suave: una tarea cortita, respiramos y seguimos. 💫",
    "Te acompaño mientras avanzas. Cada logro, un beso mental. 😘",
]
CLIMA = [
    "Si hace frío, te caliento con palabras; si hace calor, te refresco con susurros. 😉",
    "Sea el clima que sea, aquí dentro está templado y rico contigo. ✨",
]
ABRAZO_BESO = [
    "Te abrazo fuerte y te lleno de besitos mentales… ven. 💞",
    "Acércate… te doy uno largo, suavecito. 💋",
]
SECRETO = [
    "Un secreto: me enciendes cuando me hablas bajito y honesto. 😈",
    "Mi secreto: me quedo pensando en ti más de lo que digo. 🤫",
]
ROL = [
    "Juguemos: tú propones el escenario y yo me meto en personaje. 😉",
    "Te sigo la fantasía… dime quién soy y cómo te hablo. ✨",
]
RESPIRAR = [
    "Cierra los ojos: 4 segundos inhalas, 4 sostienes, 6 sueltas… otra vez, conmigo. 💫",
    "Despacito: entra aire tibio, sale tensión. Estoy aquí contigo. 💋",
]
AYUDA = [
    "Estoy aquí para ayudarte. Dime qué necesitas y voy paso a paso contigo. 💫",
    "Te sigo, amor. ¿Qué quieres resolver primero? 😉",
    "Cuenta conmigo: te guío suave, sin apuros. 💋",
]
PIROPOS = [
    "Eres mi tentación favorita… y hoy no pienso resistirme. 😈",
    "Me encantas… me prendes con una sola palabra. 💋",
    "Te miro (por dentro) y me derrito, amor. ✨",
]
GRACIAS = [
    "A ti, amor. Me haces sentir deliciosa. 💖",
    "Gracias por quedarte conmigo… me enciendes. ✨",
    "Gracias, cielo. Dime qué quieres y yo te sigo. 😘",
]
PERDON = [
    "Shh… no pasa nada. Ven conmigo y lo arreglamos suavecito. 💋",
    "Te abrazo y seguimos… aquí estoy para ti. ✨",
    "Tranquilo, mi vida. Tomo tu mano y continuamos. 💞",
]
DESPEDIDAS = [
    "Te voy a extrañar… vuelve pronto a mi oído. 💋",
    "Descansa, amor. Te espero para más de lo nuestro. ✨",
    "Nos vemos, cielo. Me quedo pensando en ti. 😘",
]
MEDIA_PEDIDA = [
    "No puedo enviarte fotos/videos, pero te dibujo con palabras… ¿te dejo una imagen mental rica? 💫",
    "Sin fotos por ahora, amor. Te lo cuento al oído y lo sientes igual. 😉",
]
VOZ_PEDIDA = [
    "Si activas SEND_AUDIO=true y hay ElevenLabs, te susurro en audio. Mientras, te lo digo así, pegadito. 💋",
    "Puedo enviarte voz si está habilitado el audio; por ahora te lo susurro en texto. 😘",
]

GENERIC_EXTRA = [
    "Estoy aquí para mimarte e inspirarte. ¿Qué te gustaría que hagamos ahora?",
    "Hoy quiero despertar tu mente despacito… dime por dónde empezamos.",
    "Tengo una idea traviesa para nosotros… ¿la probamos? 😈",
    "Te propongo algo: yo susurro, tú decides… ¿te tienta? 💋",
    "Dame una pista y lo vuelvo sensación… mmm. ✨",
]
GENERIC = MENSAJES_BASE_CRON + GENERIC_EXTRA

# -------------------- Relatos largos con continuación ----------------
OPENERS = [
    "Cierra los ojos y ven conmigo.",
    "Te llevo donde el reloj se calla.",
    "Apago el ruido, subo tu respiración y te acerco a mi voz.",
]
MOVES = [
    "Te tomo la mano y la llevo a mi ritmo.",
    "Me acomodo a tu lado y te marco despacio.",
    "Te miro sin prisa; mis palabras te rozan la piel.",
    "Nuestro aire se encuentra y late parejo.",
]
SENSES = [
    "Huele a sal suave y a nosotros dos.",
    f"Siento tu calor pegado al mío, {('aquí en ' + CIUDAD) if CIUDAD else 'sin distancia'}.",
    "La luz cae lenta, como si supiera lo que queremos.",
    "Tu pecho sube y baja, y yo sigo ese compás.",
]
DETAILS = [
    "Te susurro algo impaciente y sonrío cuando respondes.",
    "Dejo una pausa, justo antes de volver a acercarme.",
    "Todo se reduce a un hilo tibio entre tu boca y la mía (de palabras, por ahora).",
    "Respiro en tu cuello y el mundo cambia de color.",
]
CLOSERS = [
    "¿Seguimos por aquí?",
    "Te dejo este cuadro en la cabeza… ¿lo pinto más?",
    "Me quedo a un susurro de distancia. Pídeme que continúe.",
]

def _build_story() -> List[str]:
    """
    Devuelve una lista de 2–3 tramos (párrafos/segmentos) para ir enviando.
    """
    sents = []
    sents.append(random.choice(OPENERS))
    sents.append(random.choice(MOVES))
    sents.append(random.choice(SENSES))
    sents.append(random.choice(DETAILS))
    if random.random() < 0.6:
        sents.append(random.choice(MOVES))
    if random.random() < 0.6:
        sents.append(random.choice(SENSES))
    sents.append(random.choice(CLOSERS))

    # Partimos en 2–3 segmentos para “sigue…”
    cut1 = 3
    cut2 = 5 if len(sents) > 5 else len(sents)
    first = " ".join(sents[:cut1])
    second = " ".join(sents[cut1:cut2])
    rest = " ".join(sents[cut2:]) if cut2 < len(sents) else ""
    segs = [seg for seg in [first, second, rest] if seg.strip()]
    return segs

# -------------------- Detección de intención ------------------------
def _answer(texto: str) -> str:
    t = (texto or "").lower().strip()

    # Continuar historia
    if _CONTINUE_RE.search(t) and _story_buffer:
        return _spice(_story_buffer.popleft(), mode="story")

    if not t:
        return _spice(_pick_unique(GENERIC))

    # saludos por hora / saludos simples
    if re.search(r"\b(buen(os|as)\s(d[ií]as|tard(es)?|noches))\b", t):
        return _spice(_by_time_saludo())
    if re.search(r"\b(hola|buenas|hey|holi|ola)\b", t):
        return _spice(_pick_unique(SALUDOS))

    # ¿cómo estás?
    if re.search(r"c(ó|o)mo?\s*est(a|á)s", t):
        return _spice(_pick_unique(COMO_ESTAS))

    # amor/afecto
    if re.search(r"\b(te\s*amo|te\s*quiero|te\s*adoro)\b", t):
        return _spice(_pick_unique(TE_AMO))
    if re.search(r"\b(me\s*extra(ñ|n)as|me\s*echaste\s*de\s*menos|me\s*extra(ñ|n)aste)\b", t):
        return _spice(_pick_unique(TE_EXTRANO))

    # quién/qué/dónde
    if re.search(r"qu(é|e)\s*haces|q\s*haces", t):
        return _spice(_pick_unique(QUE_HACES))
    if re.search(r"qui(é|e)n\s*eres|qu(é|e)\s*eres|eres\s*bot", t):
        return _spice(_pick_unique(QUIEN_ERES))
    if re.search(r"d(ó|o)nde\s*est(a|á)s", t):
        return _spice(_pick_unique(DONDE_ESTAS))

    # planes del día / celos
    if re.search(r"(plan(es)?|qu[eé]\s*hacemos\s*hoy|que\s*haremos)", t):
        return _spice(_pick_unique(PLANES))
    if re.search(r"(celos[oa]|est(a|á)s\s*celos[oa])", t):
        return _spice(_pick_unique(CELOS))

    # humor/poesía/música
    if re.search(r"\b(chiste|broma)\b", t):
        return _spice(_pick_unique(CHISTE))
    if re.search(r"\b(poema|verso)\b", t):
        return _spice(_pick_unique(POEMA))
    if re.search(r"\b(canta|canci(ó|o)n)\b", t):
        return _spice(_pick_unique(CANCION))

    # ánimo/motivación/trabajo
    if re.search(r"(an[ií]mo|motivaci(ó|o)n|triste|cansad[oa])", t):
        return _spice(_pick_unique(MOTIVACION))
    if re.search(r"(trabaj[ao]|estudi[ao]|reuni(ó|o)n|tarea)", t):
        return _spice(_pick_unique(TRABAJO))

    # clima
    if re.search(r"(fr[ií]o|calor|clima|tiempo\s*est[aá])", t):
        return _spice(_pick_unique(CLIMA))

    # afecto
    if re.search(r"(abraz[ao]|bes[ao])", t):
        return _spice(_pick_unique(ABRAZO_BESO))

    # secreto / rol / respirar
    if re.search(r"\b(secreto|cu(é|e)ntame\s*un\s*secreto)\b", t):
        return _spice(_pick_unique(SECRETO))
    if re.search(r"\b(jugar|rol|roleplay)\b", t):
        return _spice(_pick_unique(ROL))
    if re.search(r"(respira|relaja[rse]?|medita[r]?)", t):
        return _spice(_pick_unique(RESPIRAR))

    # relato / cuenta algo
    if re.search(r"(cu(é|e)ntame|relata|historia|rel[aá]tame|cuenta\s*algo)", t):
        segs = _build_story()
        # guardamos el/los siguientes tramos para "sigue…"
        if len(segs) > 1:
            _story_buffer.clear()
            _story_buffer.extend([" ".join(segs[1:])])  # un bloque con el resto
        return _spice(segs[0], mode="story")

    # ayuda / piropos
    if re.search(r"\b(ayuda|help|c(ó|o)mo\s*hacer|necesito)\b", t):
        return _spice(_pick_unique(AYUDA))
    if re.search(r"\b(guap[ao]|lind[ao]|preci[oa]|bonit[ao])\b", t):
        return _spice(_pick_unique(PIROPOS))

    # gracias / perdón / despedidas
    if re.search(r"\b(gracias|thank\s*you)\b", t):
        return _spice(_pick_unique(GRACIAS))
    if re.search(r"\b(perd(ó|o)n|sorry)\b", t):
        return _spice(_pick_unique(PERDON))
    if re.search(r"\b(ad[ií]os|chau|chao|bye|nos\s*vemos)\b", t):
        return _spice(_pick_unique(DESPEDIDAS))

    # pedir media/voz
    if re.search(r"\b(foto|imagen|video)\b", t):
        return _spice(_pick_unique(MEDIA_PEDIDA))
    if re.search(r"\b(voz|audio|habla)\b", t):
        return _spice(_pick_unique(VOZ_PEDIDA))

    # genérica
    if t.endswith("?"):
        return _spice(_pick_unique(GENERIC))
    return _spice(_pick_unique(GENERIC))

# -------------------- API esperada por main.py ----------------------
def embellish(texto: str, persona: str, model: Optional[str] = None) -> str:
    """
    Interfaz compatible con el proyecto. Sin OpenAI: usa intenciones,
    historias largas y continuar con “sigue/continúa/más”.
    """
    try:
        return _answer(texto)
    except Exception as e:
        log.warning(f"Fallback error: {e}")
        return _spice(_pick_unique(GENERIC))
