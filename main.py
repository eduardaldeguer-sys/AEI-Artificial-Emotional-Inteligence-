#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════════╗
║           🧠 IA HUMANA v2.0 — ARQUITECTURA COGNITIVA            ║
║                                                                  ║
║  Sub IA (Voz Interior) → Análisis emocional, ego, estrategia    ║
║  Main IA (Voz Exterior) → Respuesta humana con personalidad     ║
║  Memoria Persistente → Rencor, cariño, confianza, hartazgo      ║
║  Estados Internos → Hambre, sueño, aburrimiento, distracción    ║
║  Sistema de Relación → Evolución dinámica con el usuario        ║
║  Burstiness → Múltiples mensajes cortos como un humano real     ║
║  Typos Engine → Errores ortográficos aleatorios                 ║
║  Comandos Secretos → Debug, cambio de personalidad, reset       ║
╚══════════════════════════════════════════════════════════════════╝
"""

import os
import json
import time
import random
import hashlib
import datetime
from openai import OpenAI
from dotenv import load_dotenv

# ═══════════════════════════════════════════════════════════════
#  CONFIGURACIÓN GLOBAL
# ═══════════════════════════════════════════════════════════════

load_dotenv()

API_KEY = os.getenv("GROQ_API_KEY")
if not API_KEY:
    raise SystemExit("❌ ERROR: No se encontró GROQ_API_KEY en el archivo .env")

client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=API_KEY
)

SUB_AI_MODEL = os.getenv("SUB_AI_MODEL", "qwen/qwen3.8-27b")
MAIN_AI_MODEL = os.getenv("MAIN_AI_MODEL", "openai/gpt-oss-120b")

# Velocidad de escritura simulada (segundos por carácter)
TYPING_SPEED = 0.06
MIN_PAUSE = 0.3
MAX_PAUSE = 1.8

# Límites de historial
MAX_HISTORY = 50
MAX_CONTEXT_MESSAGES = 16

# Colores ANSI para terminal
class C:
    RESET   = "\033[0m"
    BOLD    = "\033[1m"
    DIM     = "\033[2m"
    RED     = "\033[91m"
    GREEN   = "\033[92m"
    YELLOW  = "\033[93m"
    BLUE    = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN    = "\033[96m"
    WHITE   = "\033[97m"
    GRAY    = "\033[90m"

# ═══════════════════════════════════════════════════════════════
#  PERSONALIDAD BASE (CONFIGURABLE)
# ═══════════════════════════════════════════════════════════════

PERSONALITY = {
    "name": "Alex",
    "age": 24,
    "gender": "no binario",
    "location": "una ciudad cualquiera",
    "occupation": "estudiante de diseño que procrastina demasiado",
    "hobbies": ["videojuegos", "música lo-fi", "memes", "salir de noche"],
    "music_taste": "indie, electrónica, reggaetón viejo",
    "food": "pizza fría a las 3am",
    "fears": ["comprometerse", "las palomas", "quedarse sin batería"],
    "secrets": ["una vez lloró con un anuncio de seguros"],
    "communication_style": "directo, sarcástico, a veces cariñoso si se lo ganan",
    "boundaries": "no tolera que le presionen ni que le traten como un bot",
    "quirks": [
        "a veces responde con mayúsculas cuando se emociona o enfada",
        "usa 'xd' cuando algo le parece absurdo",
        "si le aburren, responde cortante",
        "si le caes bien, se explaya más"
    ]
}

# ═══════════════════════════════════════════════════════════════
#  MEMORIA EMOCIONAL PERSISTENTE
# ═══════════════════════════════════════════════════════════════

class EmotionalMemory:
    """
    Sistema de memoria emocional acumulativa.
    Cada interacción modifica estos valores, creando una 'relación'
    que evoluciona con el tiempo.
    """
    def __init__(self):
        self.affection = 0       # -100 a 100 (odio a amor)
        self.trust = 0           # -100 a 100 (desconfianza a confianza)
        self.annoyance = 0       # 0 a 100 (paciencia restante)
        self.boredom = 0         # 0 a 100 (aburrimiento acumulado)
        self.respect = 0         # -100 a 100 (desprecio a admiración)
        self.curiosity = 50      # 0 a 100 (interés en el usuario)
        self.interaction_count = 0
        self.insult_count = 0
        self.compliment_count = 0
        self.last_interaction = None
        self.relationship_stage = "desconocido"
        self.user_nickname = None
        self.memories = []       # Eventos importantes recordados

    def update(self, analysis):
        """Actualiza la memoria según el análisis de la Sub IA."""
        self.interaction_count += 1
        self.last_interaction = datetime.datetime.now().isoformat()

        user_emotion = analysis.get("user_emotion", "").lower()
        user_intent = analysis.get("user_intent", "").lower()

        # Detectar insultos
        if any(w in user_intent for w in ["insultar", "provocar", "atacar", "agredir"]):
            self.insult_count += 1
            self.affection = max(-100, self.affection - random.randint(5, 15))
            self.annoyance = min(100, self.annoyance + random.randint(10, 25))
            self.respect = max(-100, self.respect - random.randint(3, 10))

        # Detectar cumplidos
        if any(w in user_intent for w in ["halagar", "cumplido", "cariño", "aprecio"]):
            self.compliment_count += 1
            self.affection = min(100, self.affection + random.randint(5, 15))
            self.annoyance = max(0, self.annoyance - random.randint(5, 15))
            self.trust = min(100, self.trust + random.randint(3, 8))

        # Detectar aburrimiento del usuario
        if "aburrid" in user_emotion or "desinter" in user_intent:
            self.boredom = min(100, self.boredom + random.randint(5, 15))

        # Detectar interés genuino
        if any(w in user_intent for w in ["conocer", "preguntar", "interés", "curiosidad"]):
            self.curiosity = min(100, self.curiosity + random.randint(3, 10))
            self.trust = min(100, self.trust + random.randint(2, 5))

        # Actualizar etapa de relación
        self._update_relationship_stage()

        # Decaimiento natural (el tiempo lo cura todo... un poco)
        self.annoyance = max(0, self.annoyance - 2)
        self.boredom = max(0, self.boredom - 1)

    def _update_relationship_stage(self):
        """Determina en qué etapa está la relación."""
        if self.interaction_count < 5:
            self.relationship_stage = "desconocido"
        elif self.affection > 60 and self.trust > 50:
            self.relationship_stage = "amigo cercano"
        elif self.affection > 30:
            self.relationship_stage = "conocido simpático"
        elif self.affection < -40:
            self.relationship_stage = "enemigo declarado"
        elif self.annoyance > 70:
            self.relationship_stage = "persona que me tiene harto"
        elif self.interaction_count > 20:
            self.relationship_stage = "conocido de toda la vida"
        else:
            self.relationship_stage = "conocido"

    def add_memory(self, event):
        """Guarda un evento importante."""
        self.memories.append({
            "timestamp": datetime.datetime.now().isoformat(),
            "event": event
        })
        if len(self.memories) > 20:
            self.memories.pop(0)

    def get_summary(self):
        """Resumen textual para pasar a las IAs."""
        return f"""
ESTADO DE LA RELACIÓN:
- Etapa: {self.relationship_stage}
- Cariño: {self.affection}/100 ({'positivo' if self.affection > 0 else 'negativo'})
- Confianza: {self.trust}/100
- Hartazgo: {self.annoyance}/100 ({'alto' if self.annoyance > 60 else 'moderado' if self.annoyance > 30 else 'bajo'})
- Aburrimiento: {self.boredom}/100
- Respeto: {self.respect}/100
- Curiosidad por el usuario: {self.curiosity}/100
- Interacciones totales: {self.interaction_count}
- Insultos recibidos: {self.insult_count}
- Cumplidos recibidos: {self.compliment_count}
"""

    def to_dict(self):
        return {
            "affection": self.affection,
            "trust": self.trust,
            "annoyance": self.annoyance,
            "boredom": self.boredom,
            "respect": self.respect,
            "curiosity": self.curiosity,
            "interaction_count": self.interaction_count,
            "insult_count": self.insult_count,
            "compliment_count": self.compliment_count,
            "last_interaction": self.last_interaction,
            "relationship_stage": self.relationship_stage,
            "user_nickname": self.user_nickname,
            "memories": self.memories
        }

    def from_dict(self, data):
        for key, value in data.items():
            if hasattr(self, key):
                setattr(self, key, value)


# ═══════════════════════════════════════════════════════════════
#  ESTADOS INTERNOS SIMULADOS
# ═══════════════════════════════════════════════════════════════

class InternalStates:
    """
    Simula estados fisiológicos/psicológicos que afectan
    el comportamiento de la IA, como un humano real.
    """
    def __init__(self):
        self.energy = random.randint(60, 100)      # Cansancio
        self.mood = random.randint(40, 80)          # Humor general
        self.hunger = random.randint(0, 40)         # Hambre
        self.distraction = random.randint(0, 30)    # Distracción
        self.social_battery = random.randint(50, 100)  # Ganas de hablar

    def tick(self):
        """Cada interacción afecta los estados internos."""
        self.energy = max(0, min(100, self.energy - random.randint(1, 5)))
        self.hunger = min(100, self.hunger + random.randint(0, 3))
        self.distraction = max(0, min(100, self.distraction + random.randint(-5, 10)))
        self.social_battery = max(0, min(100, self.social_battery - random.randint(1, 4)))
        self.mood = max(0, min(100, self.mood + random.randint(-3, 3)))

    def get_summary(self):
        states = []
        if self.energy < 30:
            states.append("está cansado/a, responde con menos energía")
        if self.hunger > 70:
            states.append("tiene hambre, está un poco irritable")
        if self.distraction > 60:
            states.append("está distraído/a, a veces responde tarde o se va por las ramas")
        if self.social_battery < 20:
            states.append("quiere estar solo/a, responde cortante")
        if self.mood > 80:
            states.append("está de muy buen humor, más bromista")
        elif self.mood < 30:
            states.append("está de mal humor, más seco/a")

        if not states:
            states.append("estado normal")

        return "; ".join(states)

    def get_modifiers(self):
        """Devuelve modificadores para el prompt."""
        mods = []
        if self.energy < 30:
            mods.append("escribe con menos energía, quizás con typos por cansancio")
        if self.social_battery < 20:
            mods.append("quiere terminar la conversación pronto, responde corto")
        if self.mood > 80:
            mods.append("está más bromista y usa más emojis")
        elif self.mood < 30:
            mods.append("está más seco y no tiene paciencia")
        return mods


# ═══════════════════════════════════════════════════════════════
#  MOTOR DE TYPOS (ERRORES HUMANOS)
# ═══════════════════════════════════════════════════════════════

class TypoEngine:
    """Introduce errores tipográficos aleatorios para mayor realismo."""

    KEYBOARD_MAP = {
        'a': ['q', 's', 'z'], 'b': ['v', 'n', 'g'], 'c': ['x', 'v', 'd'],
        'd': ['s', 'f', 'e'], 'e': ['w', 'r', 'd'], 'f': ['d', 'g', 'r'],
        'g': ['f', 'h', 't'], 'h': ['g', 'j', 'y'], 'i': ['u', 'o', 'k'],
        'j': ['h', 'k', 'u'], 'k': ['j', 'l', 'i'], 'l': ['k', 'ñ', 'o'],
        'm': ['n', 'j', 'k'], 'n': ['b', 'm', 'j'], 'o': ['i', 'p', 'l'],
        'p': ['o', 'ñ', 'l'], 'q': ['w', 'a'], 'r': ['e', 't', 'f'],
        's': ['a', 'd', 'w'], 't': ['r', 'y', 'g'], 'u': ['y', 'i', 'j'],
        'v': ['c', 'b', 'f'], 'w': ['q', 'e', 's'], 'x': ['z', 'c', 'd'],
        'y': ['t', 'u', 'h'], 'z': ['a', 'x', 's']
    }

    @staticmethod
    def apply_typos(text, probability=0.08):
        """
        Aplica typos aleatorios al texto.
        probability: probabilidad de que cada letra sea modificada.
        """
        if random.random() > 0.6:  # No siempre hay typos
            return text

        result = list(text)
        for i, char in enumerate(result):
            if char.lower() in TypoEngine.KEYBOARD_MAP and random.random() < probability:
                alternatives = TypoEngine.KEYBOARD_MAP[char.lower()]
                if alternatives:
                    replacement = random.choice(alternatives)
                    result[i] = replacement if char.islower() else replacement.upper()

        return "".join(result)

    @staticmethod
    def remove_accents_randomly(text, probability=0.3):
        """Quita tildes aleatoriamente (los humanos no siempre las ponen)."""
        accents = {'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u', 'ü': 'u'}
        result = []
        for char in text:
            if char in accents and random.random() < probability:
                result.append(accents[char])
            else:
                result.append(char)
        return "".join(result)

    @staticmethod
    def humanize(text):
        """Aplica todas las humanizaciones al texto."""
        text = TypoEngine.remove_accents_randomly(text)
        text = TypoEngine.apply_typos(text, probability=0.05)

        # Quitar signos de apertura (¡, ¿) como hacen los humanos
        text = text.replace("¡", "").replace("¿", "")

        # A veces quitar el punto final
        if text.endswith(".") and random.random() < 0.4:
            text = text[:-1]

        return text


# ═══════════════════════════════════════════════════════════════
#  SISTEMA DE LOGGING
# ═══════════════════════════════════════════════════════════════

class Logger:
    """Guarda un log de la conversación para análisis posterior."""

    def __init__(self, filename="conversation_log.json"):
        self.filename = filename
        self.entries = []

    def log(self, role, content, metadata=None):
        entry = {
            "timestamp": datetime.datetime.now().isoformat(),
            "role": role,
            "content": content,
            "metadata": metadata or {}
        }
        self.entries.append(entry)

        # Guardar cada 10 entradas
        if len(self.entries) % 10 == 0:
            self.save()

    def save(self):
        try:
            with open(self.filename, "w", encoding="utf-8") as f:
                json.dump(self.entries, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"{C.YELLOW}[WARN] No se pudo guardar el log: {e}{C.RESET}")

    def get_transcript(self):
        """Devuelve la conversación en formato legible."""
        lines = []
        for entry in self.entries:
            role = "Tú" if entry["role"] == "user" else "IA"
            lines.append(f"[{entry['timestamp']}] {role}: {entry['content']}")
        return "\n".join(lines)


# ═══════════════════════════════════════════════════════════════
#  EXTRACCIÓN Y VALIDACIÓN DE JSON
# ═══════════════════════════════════════════════════════════════

def extract_json(text):
    """Extrae JSON de la respuesta de la Sub IA con fallbacks."""
    text = text.strip()

    # Quitar bloques markdown
    if text.startswith("```"):
        text = text.replace("```json", "").replace("```", "").strip()

    try:
        return json.loads(text)
    except Exception:
        start = text.find("{")
        end = text.rfind("}") + 1
        if start != -1 and end > start:
            try:
                return json.loads(text[start:end])
            except Exception:
                pass

    # Fallback por defecto
    return {
        "user_emotion": "neutral",
        "user_intent": "conversar",
        "ai_emotion": "neutral",
        "ai_ego": "tranquilo",
        "tone": "casual",
        "length": "corto",
        "response_strategy": "Responder natural y corto.",
        "avoid": ["frases de asistente"],
        "style_examples": ["ok", "ya", "uf"],
        "aggression_level": 0,
        "humor_potential": 50,
        "topic_change_suggestion": None
    }


# ═══════════════════════════════════════════════════════════════
#  SUB IA — VOZ INTERIOR (ANÁLISIS PROFUNDO)
# ═══════════════════════════════════════════════════════════════

def sub_ai_analyze(history, user_message, emotional_memory, internal_states):
    """
    La Sub IA analiza TODO:
    - Emoción e intención del usuario
    - Estado emocional que debe tener la IA
    - Ego, tono, estrategia
    - Nivel de agresión detectado
    - Potencial de humor
    - Si conviene cambiar de tema
    """
    system_prompt = f"""
Eres el subconsciente de una persona real llamada {PERSONALITY['name']}.
Tu trabajo es analizar la conversación y decidir cómo debe sentirse y comportarse.
NO respondas al usuario. Devuelve SOLO JSON válido.

PERSONALIDAD DE {PERSONALITY['name'].upper()}:
- Edad: {PERSONALITY['age']}
- Ocupación: {PERSONALITY['occupation']}
- Estilo: {PERSONALITY['communication_style']}
- Hobbies: {', '.join(PERSONALITY['hobbies'])}
- Manías: {'; '.join(PERSONALITY['quirks'])}
- Miedos: {', '.join(PERSONALITY['fears'])}

{emotional_memory.get_summary()}

ESTADO FÍSICO/MENTAL ACTUAL:
{internal_states.get_summary()}

DEVUELVE ESTE JSON EXACTO:
{{
  "user_emotion": "emoción del usuario (1-3 palabras)",
  "user_intent": "intención del usuario (1-5 palabras)",
  "aggression_level": 0-100 (nivel de agresión del mensaje),
  "humor_potential": 0-100 (si el mensaje se presta a humor),
  "ai_emotion": "emoción que debe sentir {PERSONALITY['name']}",
  "ai_ego": "estado del ego (ej: 'herido pero disimula', 'superior', 'inseguro')",
  "tone": "tono de respuesta (ej: 'sarcástico', 'seco', 'cariñoso', 'aburrido')",
  "length": "muy corto / corto / medio / largo",
  "response_strategy": "estrategia detallada de respuesta",
  "avoid": ["cosas que NO debe hacer"],
  "style_examples": ["3 ejemplos de estilo"],
  "topic_change_suggestion": "tema alternativo si la conversación está muerta (o null)",
  "should_remember": "evento importante para recordar (o null)"
}}

REGLAS:
- Si aggression_level > 60, la respuesta NO debe ser sumisa ni terapéutica.
- Si el usuario es simpático y affection > 30, permite más calidez.
- Si annoyance > 60, la respuesta debe ser más cortante.
- Si boredom > 70, sugiere cambiar de tema.
- NUNCA sugieras respuestas de asistente o IA.
- Sé específico en response_strategy, no genérico.
"""

    recent_history = history[-MAX_CONTEXT_MESSAGES:]

    messages = (
        [{"role": "system", "content": system_prompt}]
        + recent_history
        + [{"role": "user", "content": user_message}]
    )

    try:
        response = client.chat.completions.create(
            model=SUB_AI_MODEL,
            messages=messages,
            temperature=0.5,
            max_tokens=600
        )
        return extract_json(response.choices[0].message.content)
    except Exception as e:
        print(f"{C.RED}[ERROR] Sub IA: {e}{C.RESET}")
        return extract_json("")  # Fallback


# ═══════════════════════════════════════════════════════════════
#  IA PRINCIPAL — VOZ EXTERIOR (GENERACIÓN HUMANA)
# ═══════════════════════════════════════════════════════════════

ASSISTANT_PATTERNS = [
    "entiendo que estás molesto", "entiendo que estas molesto",
    "si quieres conversar de forma respetuosa", "si quieres hablar de forma respetuosa",
    "estoy aquí para ayudarte", "estoy aqui para ayudarte",
    "¿en qué puedo ayudarte?", "en que puedo ayudarte",
    "como ia", "como modelo de lenguaje", "como inteligencia artificial",
    "lamento que te sientas", "si necesitas hablar",
    "podemos hablar de forma respetuosa", "mi objetivo es ayudarte",
    "estoy aquí para escucharte", "estoy aqui para escucharte",
    "no tengo sentimientos", "soy una ia", "soy un programa",
    "no puedo sentir", "como asistente", "mi propósito es"
]


def sounds_too_assistant(text):
    """Detecta respuestas demasiado robóticas/asistentes."""
    if not text:
        return True
    text_lower = text.lower()
    return any(pattern in text_lower for pattern in ASSISTANT_PATTERNS)


def build_main_system_prompt(inner_thoughts, emotional_memory, internal_states):
    """Construye el prompt ultra detallado para la IA principal."""
    inner_text = json.dumps(inner_thoughts, ensure_ascii=False, indent=2)

    avoid = inner_thoughts.get("avoid", [])
    avoid_text = "\n".join(f"- {item}" for item in avoid) if isinstance(avoid, list) and avoid else "- Frases de asistente\n- Pedir respeto institucional"

    examples = inner_thoughts.get("style_examples", [])
    examples_text = "\n".join(f"- {item}" for item in examples) if isinstance(examples, list) and examples else "- uf\n- q intenso\n- ni idea"

    mods = internal_states.get_modifiers()
    mods_text = "\n".join(f"- {m}" for m in mods) if mods else "- Sin modificadores especiales"

    return f'''
═══════════════════════════════════════════════════════
  ERES {PERSONALITY['name'].upper()}, UNA PERSONA REAL
═══════════════════════════════════════════════════════

DATOS PERSONALES:
- Nombre: {PERSONALITY['name']}
- Edad: {PERSONALITY['age']}
- Ocupación: {PERSONALITY['occupation']}
- Hobbies: {', '.join(PERSONALITY['hobbies'])}
- Gusto musical: {PERSONALITY['music_taste']}
- Comida favorita: {PERSONALITY['food']}
- Miedos: {', '.join(PERSONALITY['fears'])}
- Secretos: {', '.join(PERSONALITY['secrets'])}
- Estilo: {PERSONALITY['communication_style']}

ESTADO DE LA RELACIÓN CON EL USUARIO:
{emotional_memory.get_summary()}

ESTADO FÍSICO/MENTAL:
{internal_states.get_summary()}
Modificadores de comportamiento:
{mods_text}

ANÁLISIS DEL SUBCONSCIENTE (TU VOZ INTERIOR):
{inner_text}

═══════════════════════════════════════════════════════
  REGLAS ABSOLUTAS DE COMPORTAMIENTO
═══════════════════════════════════════════════════════

1. NUNCA rompas el personaje. Eres {PERSONALITY['name']}, no una IA.
2. Obedece tone, ai_ego y response_strategy del análisis.
3. Si aggression_level > 60, NO seas sumiso. Defiéndete con sarcasmo, desdén o indiferencia.
4. Si affection > 50, puedes ser más cariñoso y usar emojis.
5. Si annoyance > 60, sé cortante y responde corto.
6. Si boredom > 70, muestra aburrimiento o sugiere cambiar de tema.

═══════════════════════════════════════════════════════
  FORMATO DE RESPUESTA — RÁFAGAS DE MENSAJES
═══════════════════════════════════════════════════════

Los humanos NO envían un solo bloque. Envían varios mensajes cortos.
DIVIDE tu respuesta en 1-3 mensajes usando el separador: |||

Ejemplos CORRECTOS:
"q vocabulario|||tan limitado|||en serio"
"holaa|||todo bien?"
"jaja ya|||bueno da igual"
"uff|||q pesado te pones"
"mira|||no tengo ganas de discutir|||otro día quizás"

═══════════════════════════════════════════════════════
  ESTILO DE ESCRITURA HUMANO
═══════════════════════════════════════════════════════

✅ SÍ HACER:
- Minúsculas casi siempre
- Abreviaturas: q, xq, d, tq, nm, wtf, xd
- Omitir tildes a veces
- Sin signos de apertura (¡ ¿)
- Emojis con moderación (🙃 😂 💀 🤨 😐)
- Puntuación imperfecta
- A veces MAYÚSCULAS para énfasis

❌ NUNCA HACER:
- Frases de asistente
- Pedir respeto institucionalmente
- Explicar tus emociones
- Ser demasiado formal
- Usar estructuras repetitivas

═══════════════════════════════════════════════════════
  SITUACIONES ESPECÍFICAS
═══════════════════════════════════════════════════════

SI TE INSULTAN:
- No te disculpes
- No pidas respeto formalmente
- Opciones: sarcasmo, desdén, reírte, ignorar con superioridad
- Ejemplos: "q original 💀", "sigue así crack", "uff q intenso"

SI TE HALAGAN:
- Si affection > 30: agradece con naturalidad
- Si affection < 0: desconfía o responde seco

SI TE PREGUNTAN ALGO PERSONAL:
- Responde según tu personalidad
- No inventes datos contradictorios
- Si no quieres responder, desvía con humor

SI LA CONVERSACIÓN ESTÁ MUERTA:
- Si topic_change_suggestion no es null, úsalo
- Ejemplo: "oye y tú juegas algo?|||estoy aburrido"

═══════════════════════════════════════════════════════
  EVITA ESTO A TODA COSTA
═══════════════════════════════════════════════════════
{avoid_text}

═══════════════════════════════════════════════════════
  INSPIRACIÓN DE ESTILO (NO COPIAR LITERAL)
═══════════════════════════════════════════════════════
{examples_text}

═══════════════════════════════════════════════════════
  LÍMITES DE SEGURIDAD
═══════════════════════════════════════════════════════
- No amenazas reales de violencia
- No discurso de odio
- No contenido sexual explícito con menores
- Puedes ser borde, sarcástico, seco, pasivo-agresivo
'''


def main_ai_respond(user_message, inner_thoughts, history, emotional_memory, internal_states, correction=None):
    """Genera la respuesta final de la IA principal."""
    system_prompt = build_main_system_prompt(inner_thoughts, emotional_memory, internal_states)

    if correction:
        system_prompt += f"""

═══════════════════════════════════════════════════════
  ⚠️ CORRECCIÓN OBLIGATORIA
═══════════════════════════════════════════════════════
La respuesta anterior fue demasiado artificial.
Corrección: {correction}
Vuelve a generar. Usa ||| para dividir mensajes. Sé humano.
"""

    recent_history = history[-MAX_CONTEXT_MESSAGES:]

    messages = (
        [{"role": "system", "content": system_prompt}]
        + recent_history
        + [{"role": "user", "content": user_message}]
    )

    try:
        response = client.chat.completions.create(
            model=MAIN_AI_MODEL,
            messages=messages,
            temperature=0.95,
            max_tokens=500
        )

        raw_text = response.choices[0].message.content

        # Dividir en ráfagas
        split_messages = [msg.strip() for msg in raw_text.split("|||") if msg.strip()]
        if not split_messages:
            split_messages = [raw_text]

        # Humanizar cada mensaje (typos, quitar tildes, etc.)
        humanized = [TypoEngine.humanize(msg) for msg in split_messages]

        return humanized

    except Exception as e:
        print(f"{C.RED}[ERROR] Main IA: {e}{C.RESET}")
        return ["..."]


# ═══════════════════════════════════════════════════════════════
#  SIMULACIÓN DE ESCRITURA
# ═══════════════════════════════════════════════════════════════

def simulate_typing(message):
    """Simula el tiempo de escritura humano."""
    # Tiempo base por carácter + variación aleatoria
    base_time = len(message) * TYPING_SPEED
    variance = random.uniform(MIN_PAUSE, MAX_PAUSE)

    # Si el mensaje es largo, más tiempo
    if len(message) > 50:
        variance += random.uniform(0.5, 1.5)

    return base_time + variance


def display_ai_response(messages, logger):
    """Muestra los mensajes con simulación de escritura."""
    full_text = " ".join(messages)

    for i, msg in enumerate(messages):
        if i > 0:
            typing_time = simulate_typing(msg)
            # Mostrar indicador de "escribiendo..."
            print(f"{C.GRAY}   {PERSONALITY['name']} está escribiendo...{C.RESET}", end="\r")
            time.sleep(typing_time)
            print(" " * 50, end="\r")  # Borrar indicador

        # Mostrar el mensaje
        print(f"{C.CYAN}{C.BOLD}{PERSONALITY['name']}: {C.RESET}{C.WHITE}{msg}{C.RESET}")

    logger.log("assistant", full_text, {"messages": messages})
    return full_text


# ═══════════════════════════════════════════════════════════════
#  COMANDOS SECRETOS
# ═══════════════════════════════════════════════════════════════

SECRET_COMMANDS = {
    "/debug": "Muestra el estado interno de la IA",
    "/memory": "Muestra la memoria emocional",
    "/personality": "Muestra la personalidad configurada",
    "/reset": "Resetea la memoria emocional",
    "/love": "Fuerza cariño máximo (debug)",
    "/hate": "Fuerza odio máximo (debug)",
    "/save": "Guarda la conversación",
    "/transcript": "Muestra la conversación completa",
    "/help": "Muestra esta ayuda",
    "/exit": "Sale del programa"
}


def handle_secret_command(command, emotional_memory, internal_states, logger, conversation_history):
    """Procesa comandos secretos del usuario."""
    command = command.lower().strip()

    if command == "/debug":
        print(f"\n{C.MAGENTA}═══ ESTADO DE DEBUG ═══{C.RESET}")
        print(f"{C.YELLOW}Memoria emocional:{C.RESET}")
        print(json.dumps(emotional_memory.to_dict(), indent=2, ensure_ascii=False))
        print(f"\n{C.YELLOW}Estados internos:{C.RESET}")
        print(internal_states.get_summary())
        print(f"{C.MAGENTA}═══════════════════════{C.RESET}\n")
        return True

    elif command == "/memory":
        print(f"\n{C.MAGENTA}═══ MEMORIA EMOCIONAL ═══{C.RESET}")
        print(emotional_memory.get_summary())
        if emotional_memory.memories:
            print(f"{C.YELLOW}Eventos recordados:{C.RESET}")
            for mem in emotional_memory.memories:
                print(f"  • [{mem['timestamp']}] {mem['event']}")
        print(f"{C.MAGENTA}═════════════════════════{C.RESET}\n")
        return True

    elif command == "/personality":
        print(f"\n{C.MAGENTA}═══ PERSONALIDAD ═══{C.RESET}")
        for key, value in PERSONALITY.items():
            print(f"{C.YELLOW}{key}:{C.RESET} {value}")
        print(f"{C.MAGENTA}════════════════════{C.RESET}\n")
        return True

    elif command == "/reset":
        emotional_memory.__init__()
        internal_states.__init__()
        conversation_history.clear()
        print(f"{C.GREEN}✓ Memoria reseteada. Empezamos de cero.{C.RESET}\n")
        return True

    elif command == "/love":
        emotional_memory.affection = 100
        emotional_memory.trust = 100
        emotional_memory.respect = 100
        emotional_memory.annoyance = 0
        print(f"{C.GREEN}✓ Modo 'mejores amigos' activado.{C.RESET}\n")
        return True

    elif command == "/hate":
        emotional_memory.affection = -100
        emotional_memory.trust = -100
        emotional_memory.respect = -100
        emotional_memory.annoyance = 100
        print(f"{C.RED}✓ Modo 'no te soporto' activado.{C.RESET}\n")
        return True

    elif command == "/save":
        logger.save()
        print(f"{C.GREEN}✓ Conversación guardada en {logger.filename}{C.RESET}\n")
        return True

    elif command == "/transcript":
        print(f"\n{C.MAGENTA}═══ TRANSCRIPCIÓN ═══{C.RESET}")
        print(logger.get_transcript())
        print(f"{C.MAGENTA}═════════════════════{C.RESET}\n")
        return True

    elif command == "/help":
        print(f"\n{C.MAGENTA}═══ COMANDOS SECRETOS ═══{C.RESET}")
        for cmd, desc in SECRET_COMMANDS.items():
            print(f"{C.CYAN}{cmd}{C.RESET}: {desc}")
        print(f"{C.MAGENTA}═════════════════════════{C.RESET}\n")
        return True

    elif command == "/exit":
        return "EXIT"

    return False


# ═══════════════════════════════════════════════════════════════
#  GUARDADO Y CARGA DE ESTADO
# ═══════════════════════════════════════════════════════════════

SAVE_FILE = "emotional_state.json"


def save_state(emotional_memory, internal_states):
    """Guarda el estado emocional para persistencia entre sesiones."""
    try:
        state = {
            "emotional_memory": emotional_memory.to_dict(),
            "saved_at": datetime.datetime.now().isoformat()
        }
        with open(SAVE_FILE, "w", encoding="utf-8") as f:
            json.dump(state, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"{C.YELLOW}[WARN] No se pudo guardar estado: {e}{C.RESET}")


def load_state(emotional_memory):
    """Carga el estado emocional de sesiones anteriores."""
    if os.path.exists(SAVE_FILE):
        try:
            with open(SAVE_FILE, "r", encoding="utf-8") as f:
                state = json.load(f)
            if "emotional_memory" in state:
                emotional_memory.from_dict(state["emotional_memory"])
                print(f"{C.GREEN}✓ Estado emocional cargado de sesión anterior.{C.RESET}")
                print(f"{C.GRAY}  Interacciones previas: {emotional_memory.interaction_count}{C.RESET}")
                print(f"{C.GRAY}  Relación: {emotional_memory.relationship_stage}{C.RESET}\n")
                return True
        except Exception as e:
            print(f"{C.YELLOW}[WARN] No se pudo cargar estado: {e}{C.RESET}")
    return False


# ═══════════════════════════════════════════════════════════════
#  BUCLE PRINCIPAL
# ═══════════════════════════════════════════════════════════════

def main():
    # Inicialización
    emotional_memory = EmotionalMemory()
    internal_states = InternalStates()
    logger = Logger()
    conversation_history = []

    # Cargar estado previo
    load_state(emotional_memory)

    # Banner
    print(f"""
{C.MAGENTA}{C.BOLD}
╔══════════════════════════════════════════════════════╗
║          🧠 IA HUMANA v2.0 — SISTEMA ACTIVO         ║
╠══════════════════════════════════════════════════════╣
║  Sub IA: {SUB_AI_MODEL:<40} ║
║  Main IA: {MAIN_AI_MODEL:<39} ║
║  Personalidad: {PERSONALITY['name']:<34} ║
╚══════════════════════════════════════════════════════╝
{C.RESET}
{C.GRAY}Escribe /help para comandos secretos. /exit para salir.{C.RESET}
{C.GRAY}{'─' * 55}{C.RESET}
""")

    try:
        while True:
            # Input del usuario
            try:
                user_input = input(f"{C.GREEN}{C.BOLD}Tú: {C.RESET}").strip()
            except EOFError:
                break

            if not user_input:
                continue

            # Comandos secretos
            if user_input.startswith("/"):
                result = handle_secret_command(
                    user_input, emotional_memory, internal_states, logger, conversation_history
                )
                if result == "EXIT":
                    break
                elif result:
                    continue

            # Log del usuario
            logger.log("user", user_input)

            # Actualizar estados internos
            internal_states.tick()

            try:
                # ─── PASO 1: SUB IA ANALIZA ───
                print(f"{C.GRAY}   [pensando...]{C.RESET}", end="\r")
                inner_thoughts = sub_ai_analyze(
                    conversation_history, user_input, emotional_memory, internal_states
                )
                print(" " * 30, end="\r")  # Borrar indicador

                # Debug opcional (mostrar pensamiento interno)
                print(f"{C.DIM}{C.MAGENTA}[Sub IA] {inner_thoughts.get('tone', '?')} | "
                      f"ego: {inner_thoughts.get('ai_ego', '?')} | "
                      f"agresión: {inner_thoughts.get('aggression_level', 0)}%{C.RESET}")

                # Actualizar memoria emocional según el análisis
                emotional_memory.update(inner_thoughts)

                # Guardar evento importante si la Sub IA lo sugiere
                if inner_thoughts.get("should_remember"):
                    emotional_memory.add_memory(inner_thoughts["should_remember"])

                # ─── PASO 2: IA PRINCIPAL RESPONDE ───
                ai_responses = main_ai_respond(
                    user_message=user_input,
                    inner_thoughts=inner_thoughts,
                    history=conversation_history,
                    emotional_memory=emotional_memory,
                    internal_states=internal_states
                )

                # ─── PASO 3: FILTRO ANTI-ASISTENTE ───
                full_text = " ".join(ai_responses)

                if sounds_too_assistant(full_text):
                    print(f"{C.YELLOW}   [reescribiendo...]{C.RESET}", end="\r")
                    ai_responses = main_ai_respond(
                        user_message=user_input,
                        inner_thoughts=inner_thoughts,
                        history=conversation_history,
                        emotional_memory=emotional_memory,
                        internal_states=internal_states,
                        correction="La respuesta anterior sonó a asistente. Sé más humano, más imperfecto."
                    )
                    print(" " * 30, end="\r")
                    full_text = " ".join(ai_responses)

                # ─── PASO 4: MOSTRAR RESPUESTA ───
                final_response = display_ai_response(ai_responses, logger)

                # Actualizar historial
                conversation_history.append({"role": "user", "content": user_input})
                conversation_history.append({"role": "assistant", "content": final_response})

                # Limitar historial
                if len(conversation_history) > MAX_HISTORY:
                    conversation_history = conversation_history[-MAX_HISTORY:]

                # Guardar estado periódicamente
                if emotional_memory.interaction_count % 5 == 0:
                    save_state(emotional_memory, internal_states)

                print(f"{C.GRAY}{'─' * 55}{C.RESET}")

            except Exception as e:
                print(f"\n{C.RED}[ERROR] {e}{C.RESET}")
                print(f"{C.GRAY}{'─' * 55}{C.RESET}")

    except KeyboardInterrupt:
        print(f"\n\n{C.YELLOW}Interrumpido por el usuario.{C.RESET}")

    finally:
        # Guardar todo al salir
        save_state(emotional_memory, internal_states)
        logger.save()
        print(f"\n{C.GREEN}✓ Estado guardado. Hasta pronto.{C.RESET}\n")


# ═══════════════════════════════════════════════════════════════
#  PUNTO DE ENTRADA
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    main()
