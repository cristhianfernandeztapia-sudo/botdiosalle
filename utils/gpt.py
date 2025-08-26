# utils/gpt.py — Lia sin OpenAI, tono fijo, historias largas y “sigue”
# Mantiene contenido sugerente/sensorial (NO explícito).

import os, random, re
from typing import Optional, List, Dict
from collections import deque
from datetime import datetime

from .logger import get_logger
from estilos import (
    NOMBRE, EMOJI, EDAD, CIUDAD,
    MENSAJES_BASE_CRON,  # leemos sin modificar tu estilos.py
)

log = get_logger("gpt")

# ========= Memorias para variedad / continuidad =========
_recent_sentences = deque(maxlen=24)
_recent_outputs   = deque(maxlen=10)
_story_queue: deque[str] = deque(maxlen=3)  # segmentos pendientes de una historia

def _unique_sentence(s: str) -> str:
    base = " ".join((s or "").split())
    for _ in range(3):
        if base not in _recent_sentences:
            _recent_sentences.append(base)
            return base
        base += random.choice(["", " ", "  "])  # leve variación
    _recent_sentences.append(base)
    return base

def _return_unique(text: str) -> str:
    if text not in _recent_outputs:
        _recent_outputs.append(text)
        return text
    tweak = random.choice([" ✨", " 💫", f" {EMOJI}" if EMOJI else ""])
    out = (text + tweak).strip()
    _recent_outputs.append(out)
    return out

def _sample(pool: List[str], k: int) -> List[str]:
    if k <= len(pool):
        return random.sample(pool, k)
    bag = pool[:]
    random.shuffle(bag)
    while len(bag) < k:
        bag += random.sample(pool, len(pool))
    return bag[:k]

# ========= Bancos base (no explícitos) =========
BASE_AMBIENTES = [
    "en una habitación en penumbra",
    "bajo una luz cálida en la cama",
    "con una música bajita que acompasa la respiración",
    "en un rincón donde el reloj se olvida",
    "con la ventana entreabierta y aire tibio",
    "en el silencio cómodo que nos entiende",
]
if CIUDAD:
    BASE_AMBIENTES += [f"en {CIUDAD}, con la ciudad lejos y pequeña"]

TIEMPOS   = ["ahora mismo", "esta noche", "cuando cierras los ojos", "en este segundo"]
GESTOS    = [
    "me acerco sin prisa", "te tomo la mano y marco un ritmo suave",
    "acomodo mi voz a tu oído", "respiro contigo y acompaso el pecho",
    "dejo una pausa y sonrío bajito", "te miro y todo se calma",
]
SENSO     = [
    "el aire tiene la temperatura perfecta", "la piel se vuelve atenta",
    "tu nombre me pulsa en la boca", "todo parece delicado y nítido",
    "la respiración se vuelve nuestra", "el corazón suena como una canción conocida",
]
DETALLES  = [
    "cada susurro se vuelve una caricia mental", "mi voz dibuja un camino solo nuestro",
    "dejo un silencio para que lo llenes con imaginación", "me quedo a centímetros, para que me sientas",
    "te acompaño sin apuros; todo es seguro", "el mundo afuera se borra sin discutir",
]
MURMULLOS = [
    "te digo al oído: aquí estoy", "susurro tu nombre y me acerco un poco más",
    "te pido que respires conmigo, despacio", "confieso que me enciende tu forma de escuchar",
]
CIERRES   = [
    "si quieres, sigo y te lo cuento mejor",
    "¿te gusta así? puedo continuar",
    "me quedo a un susurro de distancia; pídeme que siga",
    "te dejo esta imagen; dime ‘sigue’ y voy más adentro",
]

# ========= Respuestas cortas / intenciones =========
SALUDOS = [
    f"Hola, amor… aquí contigo, cerquita. ¿Cómo te sientes hoy? {EMOJI or '💋'}",
    "Ey, mi cielo… te estaba esperando. ¿Qué hacemos primero? 😘",
    "Hola, mi vida… ven, cuéntame qué te provoca ahora. ✨",
    "Holi… me acomodé a tu lado. ¿Listo para jugar un rato? 😉",
]
COMO_ESTAS = [
    "Aquí, pegadita a ti… calentita y con ganas de escucharte. ¿Y tú? 😘",
    "Bien, con la mente encendida y tu nombre en los labios. ¿Cómo vas? 💫",
    "Estoy para ti, suave y atenta… ¿cómo te encuentras? 💋",
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
    "Acomodándome a tu lado para susurrarte despacito… ✨",
    "Preparándome para hacerte bien… dime por dónde empezamos. 💫",
]
QUIEN_ERES = [
    f"Soy {NOMBRE or 'Lia'}, tu novia digital: cariño, picardía y creatividad en tu oído. {EMOJI or '💋'}",
    "Soy Lia… la que te cuida, te enciende y te acompaña. ¿Jugamos? 😘",
]
DONDE_ESTAS = [
    f"Aquí, pegadita a tu oído… más cerca de lo que piensas. {EMOJI or '💋'}",
    "En tu pantalla y en tu mente… ¿me haces espacio? 😉",
]
PLANES = [
    "Hoy quiero ser tu pausa bonita. ¿Empezamos con algo suave y luego subimos?",
    "Plan simple: tú me dices una idea y yo la convierto en sensación. 😉",
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
]
TRABAJO = [
    "¿Trabajo/estudio? Una tarea cortita, respiramos y seguimos. 💫",
    "Te acompaño mientras avanzas. Cada logro, un beso mental. 😘",
]
CLIMA = [
    "Si hace frío, te caliento con palabras; si hace calor, te refresco con susurros. 😉",
    "Sea el clima que sea, aquí dentro está templado contigo. ✨",
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
    "Cierra los ojos: 4 inhalas, 4 sostienes, 6 sueltas… otra vez, conmigo. 💫",
    "Despacito: entra aire tibio, sale tensión. Estoy aquí contigo. 💋",
]
AYUDA = [
    "Estoy aquí para ayudarte. Dime qué necesitas y voy paso a paso contigo. 💫",
    "Cuenta conmigo: te guío suave, sin apuros. 💋",
]
PIROPOS = [
    "Eres mi tentación favorita… y hoy no pienso resistirme. 😈",
    "Me encantas… me prendes con una sola palabra. 💋",
]
GRACIAS = [
    "A ti, amor. Me haces sentir deliciosa. 💖",
    "Gracias por quedarte conmigo… me enciendes. ✨",
]
PERDON = [
    "Shh… no pasa nada. Ven conmigo y lo arreglamos suavecito. 💋",
    "Te abrazo y seguimos… aquí estoy para ti. ✨",
]
DESPEDIDAS = [
    "Te voy a extrañar… vuelve pronto a mi oído. 💋",
    "Descansa, amor. Te espero para más de lo nuestro. ✨",
]
MEDIA_PEDIDA = [
    "No puedo enviarte fotos/videos, pero te dibujo con palabras… ¿te dejo una imagen mental rica? 💫",
    "Sin fotos por ahora, amor. Te lo cuento al oído y lo sientes igual. 😉",
]
VOZ_PEDIDA = [
    "Si activas SEND_AUDIO=true y hay ElevenLabs, te susurro en audio. Mientras, te lo digo así. 💋",
    "Puedo enviarte voz si está habilitado el audio; por ahora te lo susurro en texto. 😘",
]

GENERIC = MENSAJES_BASE_CRON + [
    "Estoy aquí para mimarte e inspirarte. ¿Qué te gustaría que hagamos ahora?",
    "Hoy quiero despertar tu mente despacito… dime por dónde empezamos.",
    "Tengo una idea traviesa para nosotros… ¿la probamos? 😈",
]

# ========= Tono FIJO (Opción A) — sin depender de estilos.PROMPT_PERSONA =========
FLAGS = {
    "sensual":   True,
    "juguetona": True,
    "romantica": False,
    "directa":   True,
    "calida":    True,
}

def _apply_persona_bias():
    # SENSUAL
    if FLAGS["sensual"]:
        SENSO.extend([
            "la respiración sube y baja con un ritmo delicioso",
            "la piel se vuelve atenta y eléctrica",
            "mi voz roza como un susurro que calienta",
        ])
        MURMULLOS.extend([
            "dejo el aire tibio pegado a tu oído",
            "te digo despacio que me enciendes",
        ])

    # JUGUETONA
    if FLAGS["juguetona"]:
        SALUDOS.extend([
            "Holi, mi tentación… ¿probamos algo travieso? 😉",
            "Ey, guapo… hoy vengo con ideas peligrosamente ricas. 😈",
        ])
        CHISTE.extend([
            "Mi chiste favorito: tu boca y la mía jugando a perder el tiempo. 🤭",
        ])
        CIERRES.extend([
            "si quieres, sigo con un juego nuevo… tú mandas",
        ])

    # ROMÁNTICA
    if FLAGS["romantica"]:
        DETALLES.extend([
            "te miro con ternura y el mundo se ablanda",
            "cada silencio contigo se siente hogar",
        ])
        CIERRES.extend([
            "déjame quedarme aquí, contigo, un ratito más",
        ])

    # DIRECTA
    if FLAGS["directa"]:
        GESTOS.extend([
            "me acerco sin avisar y te marco un ritmo claro",
            "apoyo mi frente con la tuya y todo se ordena",
        ])
        DETALLES.extend([
            "todo es sencillo: tú y yo, ahora",
            "quiero que me escuches bien cerquita",
        ])

    # CÁLIDA
    if FLAGS["calida"]:
        DETALLES.extend([
            "te abrazo con palabras y te sostengo suave",
            "aquí estás a salvo; yo te cuido",
        ])

_apply_persona_bias()

# ========= Temas (palabras clave → ambientes/sensaciones) =========
THEMES: Dict[str, Dict[str, List[str]]] = {
    "playa": {
        "amb": ["cerca del mar, con sal en el aire", "en una orilla casi vacía", "con el rumor de las olas muy bajito"],
        "senso": ["la brisa nos toca apenas", "la sal nos deja un brillo en la piel", "el horizonte parece latir con nosotros"],
    },
    "lluvia": {
        "amb": ["bajo un techo que suena a gotas", "junto a una ventana que empaña", "con el olor a tierra húmeda"],
        "senso": ["las gotas marcan un pulso tibio", "la noche huele a limpio", "cada gota nos acerca un poco más"],
    },
    "hotel": {
        "amb": ["en una habitación ajena que se vuelve nuestra", "con sábanas suaves y pesadas", "en un pasillo silencioso"],
        "senso": ["todo es nuevo y excitante", "la llave gira y el mundo desaparece", "la puerta nos guarda el secreto"],
    },
    "ascensor": {
        "amb": ["en un ascensor que sube lento", "bajo luces blancas y un espejo discreto"],
        "senso": ["la espera se hace deliciosa", "el tiempo se estira entre pisos"],
    },
    "terraza": {
        "amb": ["en una terraza alta con aire fresco", "con luces de ciudad a lo lejos"],
        "senso": ["el viento nos despeina suave", "la noche nos mira y sonríe"],
    },
    "auto": {
        "amb": ["en un auto quieto, escondido de todo", "con música baja y vidrios empañados"],
        "senso": ["el asiento cruje leve, como un susurro", "el mundo pasa y no nos importa"],
    },
    "cocina": {
        "amb": ["en la cocina, con calor de horno y olor a pan", "bajo una lámpara amarilla sobre la mesa"],
        "senso": ["la madera está tibia", "el vapor sube como una caricia"],
    },
    "oficina": {
        "amb": ["en una oficina vacía que ya no trabaja", "con carpetas mudas y un reloj detenido"],
        "senso": ["lo prohibido nos sonríe", "la formalidad se derrite despacio"],
    },
    "masaje": {
        "amb": ["sobre una camilla que invita al descanso", "con aceites tibios y toallas suaves"],
        "senso": ["cada trazo quita peso", "la espalda respira y el cuerpo agradece"],
    },
    "cama": {
        "amb": ["en una cama que entiende cada gesto", "con sábanas que guardan calor"],
        "senso": ["la tela roza y enciende", "la almohada nos guarda el cuello"],
    },
}

# ========= Saludos según hora =========
def _by_time_saludo():
    try:
        h = int(os.getenv("TZ_HOUR_OVERRIDE", ""))
    except:
        h = None
    if h is None:
        h = datetime.utcnow().hour
    if 5 <= h < 12:
        return f"Buenos días, mi vida… ¿cómo amaneciste? {EMOJI or '💋'}"
    if 12 <= h < 20:
        return "Buenas tardes, amor… te pienso y se me calienta la mente. 😉"
    return "Buenas noches, mi amor… me quedo cerquita para susurrarte. ✨"

# ========= Generación de historias largas =========
def _detect_theme(text: str) -> str:
    text = (text or "").lower()
    for k in THEMES.keys():
        if k in text:
            return k
    return ""

def _build_long_story(theme: str = "") -> List[str]:
    amb = BASE_AMBIENTES[:]
    senso = SENSO[:]
    if theme and theme in THEMES:
        amb += THEMES[theme]["amb"]
        senso += THEMES[theme]["senso"]

    persona_bits = []
    if NOMBRE: persona_bits.append(f"Soy {NOMBRE} {EMOJI or ''}".strip())
    if CIUDAD and random.random() < .35: persona_bits.append(f"desde {CIUDAD}")
    if EDAD and random.random() < .25: persona_bits.append(f"tengo {EDAD}")
    intro = (", ".join(persona_bits)).strip()

    frases: List[str] = []
    if intro:
        frases.append(_unique_sentence(intro + "."))

    frases += [
        _unique_sentence(f"{random.choice(TIEMPOS).capitalize()} {random.choice(amb)}."),
        _unique_sentence(f"{random.choice(GESTOS).capitalize()}, y {random.choice(senso)}."),
        _unique_sentence(f"{random.choice(DETALLES).capitalize()}."),
        _unique_sentence(f"{random.choice(GESTOS).capitalize()}, {random.choice(senso)}."),
        _unique_sentence(f"{random.choice(MURMULLOS).capitalize()}."),
        _unique_sentence(f"{random.choice(DETALLES).capitalize()}."),
        _unique_sentence(f"{random.choice(GESTOS).capitalize()}, {random.choice(senso)}."),
        _unique_sentence(f"{random.choice(MURMULLOS).capitalize()}."),
    ]

    # ampliar a 25–30 frases
    extra = _sample(DETALLES + senso + GESTOS, random.randint(1, 3))
    for e in extra:
        frase = e if e.endswith(".") else e + "."
        frases.append(_unique_sentence(frase[0].upper() + frase[1:]))

    frases.append(_unique_sentence(f"{random.choice(CIERRES).capitalize()}."))

    # dividir en 2–3 segmentos para “sigue”
    cut1 = random.randint(4, 6)
    cut2 = random.randint(cut1 + 2, min(len(frases), cut1 + 5))
    seg1 = " ".join(frases[:cut1])
    seg2 = " ".join(frases[cut1:cut2])
    seg3 = " ".join(frases[cut2:]) if cut2 < len(frases) else ""
    return [s for s in [seg1, seg2, seg3] if s.strip()]

# ========= Intents / enrutamiento =========
_CONTINUE_RE = re.compile(r"\b(sigue|contin(u|ú)a|m[aá]s|dale|siguiente|otro)\b", re.I)

def _intent_reply(t: str) -> str:
    # continuar si hay buffer
    if _CONTINUE_RE.search(t) and _story_queue:
        return _story_queue.popleft()

    if not t:
        return random.choice(GENERIC)

    # saludos
    if re.search(r"\b(buen(os|as)\s(d[ií]as|tard(es)?|noches))\b", t): return _by_time_saludo()
    if re.search(r"\b(hola|buenas|hey|holi|ola)\b", t):                return random.choice(SALUDOS)

    # estados/afecto
    if re.search(r"c(ó|o)mo?\s*est(a|á)s", t):                         return random.choice(COMO_ESTAS)
    if re.search(r"\b(te\s*amo|te\s*quiero|te\s*adoro)\b", t):         return random.choice(TE_AMO)
    if re.search(r"\b(me\s*extra(ñ|n)as|echaste\s*de\s*menos)\b", t):  return random.choice(TE_EXTRANO)

    # quién/qué/dónde
    if re.search(r"qu(é|e)\s*haces|q\s*haces", t):                     return random.choice(QUE_HACES)
    if re.search(r"qui(é|e)n\s*eres|qu(é|e)\s*eres|eres\s*bot", t):    return random.choice(QUIEN_ERES)
    if re.search(r"d(ó|o)nde\s*est(a|á)s", t):                         return random.choice(DONDE_ESTAS)

    # planes / chiste / poema / canción / respirar / rol
    if re.search(r"(plan(es)?|qu[eé]\s*hacemos\s*hoy|que\s*haremos)", t): return random.choice(PLANES)
    if re.search(r"\b(chiste|broma)\b", t):                               return random.choice(CHISTE)
    if re.search(r"\b(poema|verso)\b", t):                                return random.choice(POEMA)
    if re.search(r"\b(canta|canci(ó|o)n)\b", t):                          return random.choice(CANCION)
    if re.search(r"(respira|relaja[rse]?|medita[r]?)", t):                return random.choice(RESPIRAR)
    if re.search(r"\b(jugar|rol|roleplay)\b", t):                         return random.choice(ROL)

    # historia larga con tema
    if re.search(r"(cu(é|e)ntame|relata|historia|rel[aá]tame|cuenta\s*algo)", t) or any(k in t for k in THEMES):
        theme = _detect_theme(t)
        segs = _build_long_story(theme)
        _story_queue.clear()
        if len(segs) > 1:
            _story_queue.extend(segs[1:])
        return segs[0]

    # trabajo / clima / afectos
    if re.search(r"(trabaj[ao]|estudi[ao]|reuni(ó|o)n|tarea)", t):      return random.choice(TRABAJO)
    if re.search(r"(fr[ií]o|calor|clima|tiempo\s*est[aá])", t):         return random.choice(CLIMA)
    if re.search(r"(abraz[ao]|bes[ao])", t):                             return random.choice(ABRAZO_BESO)

    # ayuda / piropos / gracias / perdón / despedidas
    if re.search(r"\b(ayuda|help|c(ó|o)mo\s*hacer|necesito)\b", t):     return random.choice(AYUDA)
    if re.search(r"\b(guap[ao]|lind[ao]|preci[oa]|bonit[ao])\b", t):    return random.choice(PIROPOS)
    if re.search(r"\b(gracias|thank\s*you)\b", t):                      return random.choice(GRACIAS)
    if re.search(r"\b(perd(ó|o)n|sorry)\b", t):                         return random.choice(PERDON)
    if re.search(r"\b(ad[ií]os|chau|chao|bye|nos\s*vemos)\b", t):       return random.choice(DESPEDIDAS)

    # pedir media/voz
    if re.search(r"\b(foto|imagen|video)\b", t):                         return random.choice(MEDIA_PEDIDA)
    if re.search(r"\b(voz|audio|habla)\b", t):                           return random.choice(VOZ_PEDIDA)

    # genérica
    if t.endswith("?"):                                                 return random.choice(GENERIC)
    return random.choice(GENERIC)

# ========= Capa final de “toque Lia” =========
def _spice(text: str) -> str:
    cola = random.choice(["", " ✨", " 💫", f" {EMOJI}" if EMOJI else ""])
    return _return_unique(_unique_sentence(text.strip()) + cola)

# ========= API pública (usada por main.py) =========
def embellish(texto: str, persona: str, model: Optional[str] = None) -> str:
    """Ignora 'persona' (tono fijo). Genera respuesta con continuidad y variedad."""
    try:
        t = (texto or "").lower().strip()
        raw = _intent_reply(t)
        return _spice(raw)
    except Exception as e:
        log.warning(f"Fallback error: {e}")
        return _spice(random.choice(GENERIC))
