"""Constrained multilingual realization: model-selected claims, fact-preserving templates."""

from .models import Claim, Match, Overlay

LABELS = {
    "en": {
        "goals": "goals",
        "shots": "shots",
        "recoveries": "recoveries",
        "pressure": "pressure events",
        "passes_completed": "completed passes",
        "final_third_entries": "final-third entries",
    },
    "hi": {
        "goals": "गोल",
        "shots": "शॉट",
        "recoveries": "गेंद वापसी",
        "pressure": "दबाव की घटनाएँ",
        "passes_completed": "सफल पास",
        "final_third_entries": "अंतिम तिहाई में प्रवेश",
    },
    "es": {
        "goals": "goles",
        "shots": "tiros",
        "recoveries": "recuperaciones",
        "pressure": "acciones de presión",
        "passes_completed": "pases completados",
        "final_third_entries": "entradas al último tercio",
    },
}
WHY = {
    "en": {
        "score": "The score changes the match state. The events show what happened, not who will win.",
        "shot_threat": "More shots indicate attacking activity; shot counts alone do not establish chance quality.",
        "pressing": "These actions suggest defensive activity. They do not prove a tactical cause or a future goal.",
        "territory": "Crossing into the final third puts the ball nearer goal; it does not guarantee a chance.",
        "circulation": "Completed passes describe circulation, not necessarily dominance.",
    },
    "hi": {
        "score": "स्कोर से मैच की स्थिति बदलती है। इससे विजेता की भविष्यवाणी नहीं की जा सकती।",
        "shot_threat": "शॉट आक्रामक गतिविधि दिखाते हैं; केवल संख्या मौके की गुणवत्ता नहीं बताती।",
        "pressing": "ये घटनाएँ रक्षात्मक सक्रियता दिखाती हैं। इनसे रणनीतिक कारण या अगले गोल की पुष्टि नहीं होती।",
        "territory": "अंतिम तिहाई में प्रवेश गेंद को गोल के करीब लाता है; मौका बनना तय नहीं है।",
        "circulation": "सफल पास गेंद के आदान-प्रदान को दिखाते हैं, जरूरी नहीं कि दबदबा हो।",
    },
    "es": {
        "score": "El marcador cambia el estado del partido; no predice al ganador.",
        "shot_threat": "Los tiros indican actividad ofensiva, pero su número no demuestra calidad.",
        "pressing": "Estas acciones sugieren actividad defensiva; no prueban una causa táctica ni un gol futuro.",
        "territory": "Entrar al último tercio acerca el balón a la portería, pero no garantiza una ocasión.",
        "circulation": "Los pases completados describen circulación, no necesariamente dominio.",
    },
}
HEADINGS = {
    "en": {
        "score": "The score tells a new story",
        "shot_threat": "An attack taking shape",
        "pressing": "Pressure, with the evidence",
        "territory": "Moving the game forward",
        "circulation": "Building through the ball",
    },
    "hi": {
        "score": "स्कोर की नई कहानी",
        "shot_threat": "हमले की तस्वीर",
        "pressing": "दबाव के पीछे के तथ्य",
        "territory": "गोल की ओर बढ़ते कदम",
        "circulation": "पास से बनता खेल",
    },
    "es": {
        "score": "Una nueva historia en el marcador",
        "shot_threat": "Un ataque que toma forma",
        "pressing": "La presión y sus pruebas",
        "territory": "Avanzando hacia la portería",
        "circulation": "Construir con el balón",
    },
}


def publish(match: Match, claim: Claim, audience: str, language: str, overlay_type="lower_third") -> dict:
    if audience not in ("fan", "analyst", "broadcaster") or language not in LABELS:
        raise ValueError("unsupported audience or language")
    team = match.home if claim.team_id == match.home.id else match.away
    label = LABELS[language][claim.metric]
    n, old = int(claim.value), int(claim.previous_value)
    minutes = round((claim.window_end_ms - claim.window_start_ms) / 60_000, 1)
    if language == "en":
        period = "in the match so far" if claim.metric == "goals" else f"in the latest {minutes:g} minutes"
        body = f"{team.name}: {n} {label} {period}."
        if audience == "analyst":
            body += f" Previous window: {old}. Change: {n - old:+d}. Evidence: {len(claim.source_event_ids)} events."
        elif audience == "fan":
            body += " A moment to watch." if claim.metric != "goals" else " The story has moved on."
        else:
            body = f"{team.short} | {n} {label} | {period}."
    elif language == "hi":
        period = "मैच में अब तक" if claim.metric == "goals" else f"पिछले {minutes:g} मिनट में"
        body = f"{team.name}: {period} {n} {label}।"
        if audience == "analyst":
            body += f" पिछली अवधि: {old}। अंतर: {n - old:+d}। साक्ष्य: {len(claim.source_event_ids)} घटनाएँ।"
        elif audience == "fan":
            body += " खेल का यह पहलू ध्यान देने लायक है।"
    else:
        period = (
            "en lo que va de partido" if claim.metric == "goals" else f"en los últimos {minutes:g} minutos"
        )
        body = f"{team.name}: {n} {label} {period}."
        if audience == "analyst":
            body += f" Ventana anterior: {old}. Cambio: {n - old:+d}. Pruebas: {len(claim.source_event_ids)} eventos."
        elif audience == "fan":
            body += " Un aspecto del juego que merece atención."
    heading = HEADINGS[language][claim.reason_code]
    overlay = Overlay(
        overlay_id=f"overlay-{claim.claim_id}-{audience}-{language}",
        match_id=match.id,
        start_ms=claim.window_end_ms,
        end_ms=min(match.duration_ms + 15_000, claim.window_end_ms + 15_000),
        overlay_type=overlay_type,
        heading=heading,
        supporting_statistic=body,
        source_event_ids=claim.source_event_ids,
        audience=audience,
        language=language,
    )
    return {
        "claim": claim.model_dump(),
        "headline": heading,
        "text": body,
        "why": WHY[language][claim.reason_code],
        "confidence": claim.confidence,
        "audience": audience,
        "language": language,
        "overlay": overlay.model_dump(),
    }
