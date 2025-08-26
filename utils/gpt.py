# utils/gpt.py — Historias robustas (3 bloques), tono fijo, sin OpenAI
# Mantiene estilo sexual/juguetón/explícito.

import os, re, random
from typing import Optional, List, Dict
from collections import deque
from datetime import datetime

from .logger import get_logger
from estilos import NOMBRE, EMOJI, EDAD, CIUDAD, MENSAJES_BASE_CRON

log = get_logger("gpt")

# ======= Memoria para variedad =======
_recent_lines = deque(maxlen=64)
_recent_outs  = deque(maxlen=16)
_story_buf: deque[str] = deque(maxlen=4)

def _uniq(s: str) -> str:
    s = " ".join((s or "").split())
    if s not in _recent_lines:
        _recent_lines.append(s)
        return s
    # leve variación para no repetir exactamente
    return (s + random.choice(["", " ✨", " 💫", f" {EMOJI}" if EMOJI else ""])).strip()

def _out(text: str) -> str:
    text = text.strip()
    if text not in _recent_outs:
        _recent_outs.append(text)
        return text
    tweak = random.choice([" ✨", " 💫", f" {EMOJI}" if EMOJI else ""])
    o = (text + tweak).strip()
    _recent_outs.append(o)
    return o

# ======= Tono FIJO (no depende de estilos.py) =======
FLAGS = {
    "sensual": True,
    "juguetona": True,
    "romantica": False,
    "directa": True,
    "calida": True,
}

# ======= Bancos de frases (no explícitos) =======
BASE_AMB = [
    "en una habitación en penumbra",
    "bajo una luz tibia",
    "con una música bajita que acompasa la respiración",
    "donde el tiempo se hace elástico y amable",
]
if CIUDAD:
    BASE_AMB += [f"en {CIUDAD}, con la ciudad diminuta al fondo"]

TIEMPOS = ["ahora mismo", "esta noche", "cuando cierras los ojos", "en este segundo"]
GESTOS  = [
    "me acerco sin prisa",
    "acomodo mi voz a tu oído",
    "te marco un ritmo suave",
    "respiro contigo y acompaso el pecho",
    "dejo un silencio y sonrío bajito",
]
SENSO   = [
    "el aire tiene la temperatura perfecta",
    "la piel se vuelve atenta",
    "tu nombre me pulsa en la boca",
    "la respiración se vuelve nuestra",
    "todo se escucha más cerquita",
]
DET     = [
    "cada susurro se vuelve una caricia mental",
    "mi voz dibuja un camino solo nuestro",
    "me quedo a centímetros para que me sientas",
    "te acompaño sin apuros; todo es seguro",
    "el mundo afuera se borra sin discutir",
]
MURM    = [
    "te digo al oído que aquí estoy",
    "susurro tu nombre y me acerco un poco más",
    "te pido que respires conmigo, despacio",
    "confieso que me enciende tu forma de escuchar",
]

if FLAGS["sensual"]:
    SENSO += [
        "la piel se vuelve eléctrica y dulce",
        "mi voz roza como una brisa tibia",
    ]
if FLAGS["juguetona"]:
    DET += [
        "te propongo un juego de miradas y pausas",
        "cada pausa es un guiño que nos calienta",
    ]
if FLAGS["directa"]:
    GESTOS += [
        "apoyo mi frente con la tuya y todo se ordena",
        "te hablo cerquita, claro y honesto",
    ]
if FLAGS["calida"]:
    DET += [
        "te abrazo con palabras y te sostengo suave",
        "aquí estás a salvo; yo te cuido",
    ]

# Temas → ambientes/sensaciones
THEMES: Dict[str, Dict[str, List[str]]] = {
    "playa": {
        "amb": ["cerca del mar, con sal en el aire", "en una orilla casi vacía", "con el rumor de olas muy bajito"],
        "senso": ["la brisa nos toca apenas", "la sal deja brillo en la piel", "el horizonte late con nosotros"],
    },
    "lluvia": {
        "amb": ["bajo un techo que suena a gotas", "junto a una ventana que empaña", "con olor a tierra húmeda"],
        "senso": ["las gotas marcan un pulso tibio", "la noche huele a limpio", "cada gota nos acerca"],
    },
    "hotel": {
        "amb": ["en una habitación ajena que se vuelve nuestra", "con sábanas pesadas y suaves"],
        "senso": ["todo es nuevo y excitante", "la llave gira y el mundo desaparece"],
    },
    "ascensor": {
        "amb": ["en un ascensor que sube lento", "bajo luces blancas y un espejo discreto"],
        "senso": ["la espera es deliciosa", "el tiempo se estira entre pisos"],
    },
    "terraza": {
        "amb": ["en una terraza alta con aire fresco", "con luces de ciudad a lo lejos"],
        "senso": ["el viento nos despeina suave", "la noche nos mira y sonríe"],
    },
    "auto": {
        "amb": ["en un auto quieto, escondido de todo", "con música baja y vidrios empañados"],
        "senso": ["el asiento cruje como un susurro", "el mundo pasa y no importa"],
    },
    "cocina": {
        "amb": ["en la cocina, con calor de horno y olor a pan", "bajo una lámpara amarilla sobre la mesa"],
        "senso": ["la madera está tibia", "el vapor sube como una caricia"],
    },
    "oficina": {
        "amb": ["en una oficina vacía que ya no trabaja", "con carpetas mudas y reloj detenido"],
        "senso": ["lo prohibido nos sonríe", "la formalidad se derrite despacio"],
    },
    "masaje": {
        "amb": ["sobre una camilla que invita a la calma", "con aceites tibios y toallas suaves"],
        "senso": ["cada trazo quita peso", "la espalda respira y agradece"],
    },
    "cama": {
        "amb": ["en una cama que entiende cada gesto", "con sábanas que guardan calor"],
        "senso": ["la tela roza y enciende", "la almohada nos guarda el cuello"],
    },
}

# ======= Saludos / genéricos =======
GENERIC = MENSAJES_BASE_CRON + [
    "Estoy aquí para mimarte e inspirarte. ¿Por dónde empezamos?",
    "Hoy quiero despertar tu mente despacito… dime qué te gusta.",
    "Tengo una idea traviesa para nosotros… ¿la probamos?",
]

def _saludo_por_hora():
    h = datetime.utcnow().hour
    if 5 <= h < 12:  return f"Buenos días, amor… ¿cómo amaneciste? {EMOJI or '💋'}"
    if 12 <= h < 20: return "Buenas tardes… te pienso y se me calienta la mente. 😉"
    return "Buenas noches… me quedo cerquita para susurrarte. ✨"

# ======= Historia larga (3 bloques) =======
def _pick_theme(text: str) -> str:
    t = (text or "").lower()
    for k in THEMES:
        if k in t:
            return k
    return ""

def _sent(s: str) -> str:
    s = s.strip()
    if not s.endswith("."):
        s += "."
    return _uniq(s[0].upper() + s[1:])

def _paragraph(sentences: List[str], n: int) -> str:
    # arma 1 párrafo con n oraciones
    chosen = random.sample(sentences, min(n, len(sentences)))
    return " ".join(_sent(x) for x in chosen)

def _story_blocks(theme: str = "") -> List[str]:
    amb = BASE_AMB[:]
    senso = SENSO[:]
    if theme and theme in THEMES:
        amb += THEMES[theme]["amb"]
        senso += THEMES[theme]["senso"]

    intro_bits = []
    if NOMBRE: intro_bits.append(f"Soy {NOMBRE} {EMOJI or ''}".strip())
    if EDAD:   intro_bits.append(f"tengo {EDAD}")
    if CIUDAD and random.random() < .4: intro_bits.append(f"desde {CIUDAD}")
    intro = ", ".join(intro_bits)

    # Banco para construir
    lines: List[str] = []
    if intro:
        lines.append(intro)

    base = [
        f"{random.choice(TIEMPOS)} {random.choice(amb)}",
        f"{random.choice(GESTOS)}, y {random.choice(senso)}",
        f"{random.choice(DET)}",
        f"{random.choice(GESTOS)}, {random.choice(senso)}",
        f"{random.choice(MURM)}",
        f"{random.choice(DET)}",
        f"{random.choice(GESTOS)}, {random.choice(senso)}",
        f"{random.choice(MURM)}",
        f"{random.choice(DET)}",
        f"{random.choice(GESTOS)}, {random.choice(senso)}",
    ]
    # variaciones extra
    extra = [
        f"{random.choice(DET)}",
        f"{random.choice(GESTOS)}, {random.choice(senso)}",
        f"{random.choice(MURM)}",
    ]
    random.shuffle(extra)
    base += extra

    # Creamos 3 párrafos (bloques) largos
    p1 = _paragraph(base, 5 + random.randint(1, 2))
    p2 = _paragraph(base, 4 + random.randint(1, 2))
    p3 = _paragraph(base, 4 + random.randint(1, 2))

    # cierre sutil
    cierre = random.choice([
        "si quieres, sigo y lo llevo un poco más adentro",
        "dime 'sigue' y continúo justo donde te gusta",
        "si te prende, pídeme que siga; me quedo cerquita",
    ])
    p1 += " " + _sent(cierre)

    return [p1, p2, p3]

# ======= Intents simples / historia sí o sí =======
HIST_RE = re.compile(
    r"\b(historia|relato|cuento|narra|narra(me)?|relata|rel[áa]tame|escena|fanfic|fantas[ií]a)\b",
    re.I,
)
CONT_RE = re.compile(r"\b(sigue|contin[uú]a|continua|m[áa]s|mas|dale|siguiente|next)\b", re.I)

def _route(t: str) -> str:
    # continuar historia en curso
    if CONT_RE.search(t) and _story_buf:
        return _story_buf.popleft()

    # historia forzada si aparece palabra clave
    if HIST_RE.search(t):
        theme = _pick_theme(t)
        bloques = _story_blocks(theme)
        _story_buf.clear()
        if len(bloques) > 1:
            for b in bloques[1:]:
                _story_buf.append(b)
        return bloques[0]

    # saludos
    if re.search(r"\b(buen(os|as)\s(d[ií]as|tard(es)?|noches))\b", t): return _saludo_por_hora()
    if re.search(r"\b(hola|buenas|hey|holi|ola)\b", t):                return random.choice([
        f"Hola, amor… aquí contigo. ¿Qué te gustaría hoy? {EMOJI or '💋'}",
        "Holi… me acomodé a tu lado. ¿Empezamos con algo lento?",
        "Ey… ven, cuéntame tu idea y la volvemos sensación.",
    ])

    # “qué haces / quién eres / dónde estás”
    if re.search(r"qu[ée]\s*haces|q\s*haces", t):      return random.choice([
        "Te espero… calentita y atenta a lo que imagines. ¿Te digo algo bonito?",
        "Acomodándome a tu oído para susurrarte despacito…",
    ])
    if re.search(r"qui[ée]n\s*eres|qu[ée]\s*eres|eres\s*bot", t):  return random.choice([
        f"Soy {NOMBRE or 'Lia'}, tu novia digital: cariñito y picardía en tu oído {EMOJI or '💋'}",
        "Soy Lia… la que te cuida, te enciende y te acompaña.",
    ])
    if re.search(r"d[óo]nde\s*est[áa]s", t):         return random.choice([
        f"Aquí, pegadita a ti… más cerca de lo que piensas. {EMOJI or '💋'}",
        "En tu pantalla y en tu mente… ¿me haces espacio?",
    ])

    # pedir “voz” o “media”
    if re.search(r"\b(foto|imagen|video)\b", t):      return random.choice([
        "No envío fotos ni videos, amor; te lo dibujo con palabras… ¿te dejo una imagen mental bonita?",
        "Sin media, pero con detalle… dime y te lo cuento al oído.",
    ])
    if re.search(r"\b(voz|audio|habla)\b", t):        return random.choice([
        "Puedo hablar si habilitas SEND_AUDIO=true con ElevenLabs; por ahora te lo susurro por texto.",
        "Si hay audio activo, te mando voz; mientras, ven conmigo por aquí.",
    ])

    # genérico
    return random.choice(GENERIC)

# ======= API pública (llamada desde main.py) =======
def embellish(texto: str, persona: str, model: Optional[str] = None) -> str:
    try:
        t = (texto or "").lower().strip()
        raw = _route(t)
        return _out(_uniq(raw))
    except Exception as e:
        log.warning(f"Fallback error: {e}")
        return _out(_uniq(random.choice(GENERIC)))
