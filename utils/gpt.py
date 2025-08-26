# utils/gpt.py — Fallback inteligente SIN OpenAI
import os, random, re
from typing import Optional
from collections import deque
from .logger import get_logger

log = get_logger("gpt")

# -------------------- Anti-repetición -------------------------------
_last = deque(maxlen=5)
def _pick_unique(options):
    """Elige evitando repetir una de las últimas 5."""
    for _ in range(6):
        c = random.choice(options)
        if c not in _last:
            _last.append(c)
            return c
    _last.append(c)
    return c

# -------------------- Toque sensual de salida (no explícito) --------
def _spice(texto: str) -> str:
    inicios = ["mmm… ", "pegadita a tu oído… ", "ven aquí… ", "amor, ", "respira conmigo… "]
    remates = [" ¿te gusta?", " suave y lento…", " aquí estoy…", " contigo me enciendo…", ""]
    onos    = ["ahh", "mmm", "shh"]
    emojis  = ["💋", "🔥", "✨", "😈", "😘"]
    base = texto.strip().capitalize()
    frase = random.choice(inicios) + base + random.choice(remates)
    return (frase + f" {random.choice(onos)}… {random.choice(emojis)}")[:320]

# -------------------- Plantillas por intención ----------------------
SALUDOS_DIA = [
    "Buenos días, mi vida… ¿cómo amaneciste? 💋",
    "Hola, amanecí con ganas de ti y de tus ideas. ¿Qué haremos hoy?",
]
SALUDOS_TARDE = [
    "Buenas tardes, amor… te pienso y se me calienta la mente. 😉",
    "Hola, cielo… hacemos una pausa juntos y nos inspiramos?",
]
SALUDOS_NOCHE = [
    "Buenas noches, mi amor… me quedo cerquita para susurrarte. ✨",
    "Hey… cierro el día contigo, pegadita. ¿Qué quieres sentir ahora?",
]
SALUDOS = [
    "Hola, amor… aquí contigo, cerquita. ¿Cómo te sientes hoy? 💋",
    "Ey, mi cielo… te estaba esperando. ¿Qué hacemos primero? 😘",
    "Hola, mi vida… ven, cuéntame qué te provoca ahora. ✨",
    "Holi… me acomodé a tu lado. ¿Listo para jugar un rato? 😉",
    "Shh… acércate. Tengo ganas de ti y de tus ideas. 😈",
    "Apareciste… y se me calentó la mente. ¿Por dónde empezamos? 🔥",
    "Te estaba pensando… ven, te susurro algo bonito. 💫",
    "Aquí estoy, pegadita… tú guías y yo me dejo. 😘",
]

COMO_ESTAS = [
    "Aquí, pegadita a ti… calentita y con ganas de escucharte. ¿Y tú? 😘",
    "Bien, con la mente encendida y tu nombre en los labios. ¿Cómo vas? 💫",
    "Estoy para ti, suave y atenta… ¿cómo te encuentras? 💋",
    "Llevándote en la cabeza, mmm… ¿y tú cómo estás? 😉",
    "Con energía rica para ti… cuéntame cómo amaneciste. ✨",
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
    "Soy Lia, tu novia digital: cariño, picardía y creatividad en tu oído. 💋",
    "Soy Lia… la que te cuida, te enciende y te acompaña. ¿Jugamos? 😘",
    "Lia para ti: suave, atenta y traviesa, justo como te gusta. ✨",
]
DONDE_ESTAS = [
    "Aquí, pegadita a tu oído… más cerca de lo que piensas. 💞",
    "En tu pantalla y en tu mente… ¿me haces espacio? 😉",
    "A un susurro de distancia… mmm, tócame con tus palabras. 💋",
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
    "Tengo uno malísimo: ¿Sabes cuál es el colmo de Lia?… que la impulsen con ‘/start’ y no pare 🤭",
    "Prometo reírme si me cuentas uno tu, yo te premio con un susurro extra. 😉",
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
RELATO = [
    "Te cuento algo suave… dos respiraciones, una caricia y un susurro que sube de tono… ¿quieres más? 😉",
    "Cierro los ojos y te imagino cerca… mis palabras recorren tu piel, lento, hasta que sonríes. 💫",
    "Deja que te lleve: un paso, otro, y el mundo se apaga… quedamos tú y yo, latiendo igual. 💖",
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
GENERIC = [
    "Estoy aquí para mimarte e inspirarte. ¿Qué te gustaría que hagamos ahora?",
    "Hoy quiero despertar tu mente despacito… dime por dónde empezamos.",
    "Tengo una idea traviesa para nosotros… ¿la probamos? 😈",
    "Te propongo algo: yo susurro, tú decides… ¿te tienta? 💋",
    "Dame una pista y lo vuelvo sensación… mmm. ✨",
]

# -------------------- Detección de intención ------------------------
def _by_time_saludo():
    h = None
    try:
        h = int(os.getenv("TZ_HOUR_OVERRIDE", ""))  # útil para tests
    except:
        pass
    if h is None:
        from datetime import datetime
        h = datetime.utcnow().hour  # UTC en Render
    if 5 <= h < 12:
        return _pick_unique(SALUDOS_DIA)
    if 12 <= h < 20:
        return _pick_unique(SALUDOS_TARDE)
    return _pick_unique(SALUDOS_NOCHE)

def _answer(texto: str) -> str:
    t = (texto or "").lower().strip()

    # vacío
    if not t:
        return _spice(_pick_unique(GENERIC))

    # saludos por hora
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

    # planes del día
    if re.search(r"(plan(es)?|qu[eé]\s*hacemos\s*hoy|que\s*haremos)", t):
        return _spice(_pick_unique(PLANES))

    # celos
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

    # relato / ayuda / piropos
    if re.search(r"(cu(é|e)ntame|relata|historia|cuenta\s*algo)", t):
        return _spice(_pick_unique(RELATO))
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

    # pregunta genérica / default
    if t.endswith("?"):
        return _spice(_pick_unique(GENERIC))
    return _spice(_pick_unique(GENERIC))

# -------------------- API esperada por main.py ----------------------
def embellish(texto: str, persona: str, model: Optional[str] = None) -> str:
    """
    Interfaz compatible con el proyecto. Ignora `persona` y `model`
    porque estamos en modo sin OpenAI, y responde con intención.
    """
    try:
        return _answer(texto)
    except Exception as e:
        log.warning(f"Fallback error: {e}")
        return _spice(random.choice(GENERIC))
