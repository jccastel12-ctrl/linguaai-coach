from datetime import datetime, timedelta, timezone

from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.pronunciation.models import PronunciationAttempt
from app.domains.pronunciation.scoring import score_transcript
from app.domains.pronunciation.schemas import PronunciationEvaluateRequest, PronunciationExercise
from app.domains.users.models import User


EXERCISES: dict[str, dict[str, list[tuple[str, str | None, str]]]] = {
    "en": {
        "A1": [
            ("Hello, how are you today?", "h / th", "Mantén un ritmo tranquilo y marca claramente how y today."),
            ("I would like a glass of water.", "w", "Redondea los labios al iniciar would y water."),
            ("Three small trees are near the street.", "th", "Para /θ/, coloca suavemente la lengua entre los dientes."),
        ],
        "A2": [("Could you tell me where the station is?", "t / st", "Pronuncia station con una /s/ inicial clara."), ("I usually work from home on Fridays.", "r", "Evita una vibración fuerte en la r inglesa."), ("This weather is better than yesterday.", "th", "Diferencia this /ð/ de weather y than.")],
        "B1": [("I have been learning English for several months.", "linking", "Une have been sin cortar demasiado el flujo."), ("Would you mind explaining that one more time?", "intonation", "Usa entonación ascendente suave al formular la petición."), ("The project requires careful planning and clear communication.", "r / cl", "Mantén claras las consonantes finales y los grupos consonánticos.")],
        "B2": [("Although the meeting was challenging, we reached an agreement.", "stress", "Marca las palabras de contenido: meeting, challenging, reached, agreement."), ("I would appreciate it if you could send the updated document.", "connected speech", "Practica la unión natural entre would appreciate y could send."), ("Reliable communication is essential in international teams.", "r / l", "Distingue r y l en reliable e international.")],
        "C1": [("The proposal raises several ethical concerns that deserve careful consideration.", "sentence stress", "Reduce palabras funcionales y acentúa ethical, concerns, careful, consideration."), ("Had I known about the delay, I would have adjusted the schedule accordingly.", "weak forms", "Evita pronunciar cada palabra con el mismo peso."), ("Effective leadership depends on clarity, empathy, and consistent decision-making.", "rhythm", "Busca ritmo por grupos de sentido, no palabra por palabra.")],
        "C2": [("Subtle differences in intonation can completely alter the perceived meaning of a statement.", "intonation", "Practica cambios de tono sin perder claridad articulatoria."), ("The argument is compelling, although its underlying assumptions remain open to scrutiny.", "stress", "Contrasta compelling y assumptions con una prosodia natural."), ("Fluency involves precision, flexibility, and control over nuanced patterns of speech.", "rhythm", "Mantén fluidez sin sacrificar consonantes finales.")],
    },
    "es": {
        "A1": [("Hola, mucho gusto. ¿Cómo estás?", "r / s", "Pronuncia cada sílaba con claridad y evita alargar las vocales."), ("Quiero una taza de café, por favor.", "r", "La r de quiero es suave; no la conviertas en rr."), ("Mi familia vive cerca del centro.", "r", "Marca la vibrante suave de cerca y centro.")],
        "A2": [("Mañana voy a visitar a unos amigos.", "ñ", "La ñ debe sonar como una sola consonante palatal."), ("¿Podrías recomendarme un restaurante tranquilo?", "rr", "En restaurante, la r inicial es vibrante fuerte."), ("Ayer llegamos temprano al aeropuerto.", "ll / y", "Mantén un sonido consistente para ll según tu variedad de español.")],
        "B1": [("Me gustaría mejorar mi pronunciación para hablar con más confianza.", "r / rr", "Distingue r suave de rr fuerte en mejorar y pronunciación."), ("Aunque estaba cansado, terminé el trabajo antes de salir.", "d", "Evita eliminar por completo las d intervocálicas."), ("La tecnología puede facilitar la comunicación entre culturas.", "c / r", "Cuida la articulación de comunicación y culturas.")],
        "B2": [("La experiencia demuestra que escuchar con atención mejora la fluidez.", "rhythm", "Agrupa la frase por sentido y no pauses entre cada palabra."), ("Necesitamos una estrategia clara para resolver el problema de manera eficiente.", "tr / r", "Mantén definido el grupo consonántico tr."), ("El aprendizaje constante requiere disciplina, curiosidad y paciencia.", "stress", "Marca las sílabas tónicas sin exagerarlas.")],
        "C1": [("La precisión lingüística depende tanto del vocabulario como de la intención comunicativa.", "prosody", "Usa pausas naturales para separar ideas, no palabras."), ("Una explicación convincente debe ser clara, matizada y coherente con la evidencia.", "d / t", "Cuida consonantes finales e intervocálicas."), ("Comprender los matices del discurso permite adaptar el registro a cada contexto.", "rhythm", "Mantén continuidad en grupos largos de palabras.")],
        "C2": [("La entonación puede modificar sutilmente la interpretación pragmática de un enunciado.", "intonation", "Practica una curva melódica natural y estable."), ("La argumentación rigurosa exige precisión conceptual y una articulación fluida de las ideas.", "r / rr", "Controla las vibrantes sin perder el ritmo general."), ("La competencia oral avanzada combina espontaneidad, exactitud y sensibilidad al contexto.", "prosody", "Busca equilibrio entre velocidad, claridad y énfasis.")],
    },
    "sr": {
        "A1": [("Zdravo, kako si danas?", "r", "Izgovori r kratko i jasno, bez dodavanja samoglasnika."), ("Ja se zovem Ana i živim u Beogradu.", "ž", "Glas ž je zvučan; zadrži vibraciju u grlu."), ("Hvala lepo, vidimo se sutra.", "lj", "Lj izgovori kao jednu celinu, ne kao l + j odvojeno.")],
        "A2": [("Možete li mi pokazati gde je stanica?", "č / ć", "Obrati pažnju na razliku između č i ć."), ("Danas je vreme hladno, ali sunčano.", "č", "U sunčano izgovori č jasno i kratko."), ("Želeo bih da rezervišem sobu za dve noći.", "ž / ć", "Vežbaj zvučnost ž i mekši izgovor ć.")],
        "B1": [("Učim srpski jer želim bolje da razgovaram sa ljudima.", "č / lj", "Ne spajaj č i lj sa susednim samoglasnicima."), ("Mislim da je važno pažljivo slušati sagovornika.", "š / ž", "Razlikuj bezvučno š od zvučnog ž."), ("Prošlog vikenda smo posetili veoma zanimljiv grad.", "lj", "U zanimljiv održavaj lj kao palatalni glas.")],
        "B2": [("Dobra komunikacija zahteva jasnoću, strpljenje i međusobno razumevanje.", "đ", "Đ izgovori meko i zvučno."), ("Iako je zadatak bio složen, uspeli smo da pronađemo rešenje.", "ž", "U složen i rešenje zadrži jasno ž."), ("Važno je prilagoditi stil govora situaciji i sagovorniku.", "r", "R ostaje kratko i stabilno i u dužim rečenicama.")],
        "C1": [("Jezičke nijanse često menjaju način na koji sagovornik razume poruku.", "nj / č", "Održi nj kao jednu glasovnu celinu i razlikuj č."), ("Uverljiva argumentacija zahteva preciznost, doslednost i dobru strukturu.", "lj / r", "Ne gubi lj i r pri većoj brzini govora."), ("Sposobnost prilagođavanja registra važna je u profesionalnoj komunikaciji.", "ž", "Sačuvaj zvučnost ž u važna i složenijim rečima.")],
        "C2": [("Suptilne promene intonacije mogu potpuno izmeniti pragmatičko značenje iskaza.", "intonation", "Kontroliši melodiju rečenice bez gubitka artikulacije."), ("Tečna komunikacija podrazumeva preciznost, spontanost i osećaj za kontekst.", "č / ć", "Održi jasnu razliku između tvrdih i mekših afrikata."), ("Napredan govornik prilagođava ritam i naglasak nameri i situaciji.", "rhythm", "Grupiši reči po smislu i izbegavaj mehaničan ritam.")],
    },
}

def _feedback(score: int, missing: list[str], focus_sound: str | None) -> str:
    if score >= 92:
        base = "Muy buena coincidencia. El reconocimiento captó la frase casi completa."
    elif score >= 78:
        base = "Buen intento. La frase fue reconocida con bastante claridad; repite una vez buscando mayor precisión."
    elif score >= 60:
        base = "La idea general se reconoce, pero varias palabras cambiaron o no fueron detectadas. Habla un poco más despacio y articula cada grupo de palabras."
    else:
        base = "La coincidencia es baja. Escucha el modelo, repite por fragmentos cortos y vuelve a intentarlo."
    if missing:
        base += f" Presta atención a: {', '.join(missing[:4])}."
    if focus_sound:
        base += f" Foco sugerido: {focus_sound}."
    return base


async def evaluate(db: AsyncSession, user: User, data: PronunciationEvaluateRequest) -> tuple[PronunciationAttempt, list[str], list[str]]:
    score = score_transcript(data.expected_text, data.recognized_text, data.language_code)
    feedback = _feedback(score.overall_score, score.missing_words, data.focus_sound)

    attempt = PronunciationAttempt(
        user_id=user.id,
        language_code=data.language_code.lower(),
        cefr_level=data.cefr_level,
        expected_text=data.expected_text.strip(),
        recognized_text=data.recognized_text.strip(),
        overall_score=score.overall_score,
        word_accuracy=score.word_accuracy,
        transcript_similarity=score.transcript_similarity,
        browser_confidence=data.browser_confidence,
        feedback=feedback,
        focus_sound=data.focus_sound,
    )
    db.add(attempt)
    await db.commit()
    await db.refresh(attempt)
    return attempt, score.missing_words, score.extra_words


async def stats(db: AsyncSession, user: User) -> dict[str, int | None]:
    cutoff = datetime.now(timezone.utc) - timedelta(days=7)
    total = await db.scalar(select(func.count()).select_from(PronunciationAttempt).where(PronunciationAttempt.user_id == user.id)) or 0
    avg = await db.scalar(select(func.avg(PronunciationAttempt.overall_score)).where(PronunciationAttempt.user_id == user.id))
    best = await db.scalar(select(func.max(PronunciationAttempt.overall_score)).where(PronunciationAttempt.user_id == user.id))
    recent = await db.scalar(select(func.count()).select_from(PronunciationAttempt).where(PronunciationAttempt.user_id == user.id, PronunciationAttempt.created_at >= cutoff)) or 0
    return {"total_attempts": int(total), "average_score": round(avg) if avg is not None else None, "best_score": int(best) if best is not None else None, "attempts_last_7_days": int(recent)}


async def recent_attempts(db: AsyncSession, user: User, limit: int = 10) -> list[PronunciationAttempt]:
    result = await db.scalars(select(PronunciationAttempt).where(PronunciationAttempt.user_id == user.id).order_by(desc(PronunciationAttempt.created_at)).limit(limit))
    return list(result.all())
