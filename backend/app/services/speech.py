"""Speech provider abstraction. Audio is processed in memory and is never persisted."""
import os
from functools import lru_cache
from typing import BinaryIO

LANGUAGE_NAMES = {"en":"English","hi":"Hindi","ta":"Tamil","te":"Telugu","bn":"Bengali","kn":"Kannada","ml":"Malayalam","mr":"Marathi","gu":"Gujarati","pa":"Punjabi","ur":"Urdu","or":"Odia","as":"Assamese","ne":"Nepali","si":"Sinhala","ar":"Arabic","fr":"French","es":"Spanish","pt":"Portuguese","id":"Indonesian","sw":"Swahili","zh":"Chinese","ja":"Japanese","ko":"Korean","ru":"Russian"}

def safe_reply(language: str) -> str:
    # Very short offline reply; unknown languages are never silently answered in English.
    replies = {
        "en":"I could not answer right now. Please use the picture buttons or ask a local service worker.",
        "hi":"अभी जवाब नहीं मिल पाया। कृपया चित्र वाले बटन दबाएँ या आंगनवाड़ी कार्यकर्ता से पूछें।",
        "ta":"இப்போது பதில் அளிக்க முடியவில்லை. படப் பொத்தான்களைத் தொடவும் அல்லது அங்கன்வாடி பணியாளரிடம் கேளுங்கள்.",
        "te":"ఇప్పుడు సమాధానం ఇవ్వలేకపోయాను. చిత్ర బటన్లను ఉపయోగించండి లేదా అంగన్‌వాడీ కార్యకర్తను అడగండి.",
        "bn":"এখন উত্তর দিতে পারছি না। ছবির বোতাম ব্যবহার করুন অথবা অঙ্গনওয়াড়ি কর্মীর কাছে জিজ্ঞাসা করুন।",
        "kn":"ಈಗ ಉತ್ತರಿಸಲು ಸಾಧ್ಯವಾಗಲಿಲ್ಲ. ಚಿತ್ರ ಬಟನ್ ಬಳಸಿ ಅಥವಾ ಅಂಗನವಾಡಿ ಕಾರ್ಯಕರ್ತೆಯನ್ನು ಕೇಳಿ.",
        "ml":"ഇപ്പോൾ മറുപടി നൽകാനായില്ല. ചിത്ര ബട്ടണുകൾ ഉപയോഗിക്കുക അല്ലെങ്കിൽ അങ്കണവാടി പ്രവർത്തകയോട് ചോദിക്കുക.",
        "mr":"आत्ता उत्तर देता आले नाही. चित्र बटणे वापरा किंवा अंगणवाडी सेविकेला विचारा.",
        "gu":"હમણાં જવાબ આપી શકાયો નથી. ચિત્ર બટનો વાપરો અથવા આંગણવાડી કાર્યકરને પૂછો.",
        "pa":"ਹੁਣੇ ਜਵਾਬ ਨਹੀਂ ਦੇ ਸਕੇ। ਤਸਵੀਰ ਵਾਲੇ ਬਟਨ ਵਰਤੋ ਜਾਂ ਆਂਗਣਵਾੜੀ ਵਰਕਰ ਨੂੰ ਪੁੱਛੋ."
    }
    return replies.get(language, "")

class SpeechProviderError(RuntimeError):
    pass

class SpeechLanguageService:
    def transcribe(self, audio: BinaryIO) -> dict:
        provider = os.getenv("ASR_PROVIDER", "auto").lower()
        api_key = os.getenv("OPENAI_API_KEY")
        if provider in ("auto", "openai") and api_key:
            return self._transcribe_openai(audio, api_key)
        if provider == "openai":
            raise SpeechProviderError("OpenAI speech recognition needs OPENAI_API_KEY")
        if provider not in ("auto", "whisper"):
            raise SpeechProviderError("Configured speech provider is not available")
        try:
            model = _whisper_model()
            audio.seek(0)
            segments, info = model.transcribe(audio, language=None, task="transcribe", vad_filter=True, beam_size=3)
            transcript = " ".join(segment.text.strip() for segment in segments).strip()
            return {"transcript": transcript, "language": info.language, "confidence": float(info.language_probability)}
        except SpeechProviderError:
            raise
        except Exception as exc:
            raise SpeechProviderError("Speech recognition could not process the audio") from exc

    def _transcribe_openai(self, audio: BinaryIO, api_key: str) -> dict:
        try:
            import httpx
            audio.seek(0)
            model = os.getenv("OPENAI_TRANSCRIBE_MODEL", "gpt-transcribe")
            context = ("Transcribe exactly in the original language and writing system; do not translate. "
                       "The speaker may use any Indian language, including Hindi, Tamil, Urdu, Kannada, Telugu, Bengali, Marathi, "
                       "Gujarati, Malayalam, Punjabi, Odia, or Assamese, and may mix languages. "
                       "Names and terms: PMMVY, Pradhan Mantri Matru Vandana Yojana, Aadhaar, Anganwadi, MCP, RCH.")
            with httpx.Client(timeout=60) as client:
                response = client.post(
                    "https://api.openai.com/v1/audio/transcriptions",
                    headers={"Authorization": f"Bearer {api_key}"},
                    data={"model": model, "response_format": "json", "prompt": context},
                    files={"file": ("voice.webm", audio, "audio/webm")},
                )
                response.raise_for_status()
                payload = response.json()
            transcript = str(payload.get("text", "")).strip()
            detected = payload.get("languages") or []
            language = (detected[0].get("code") if detected and isinstance(detected[0], dict) else None) or payload.get("language") or ""
            return {"transcript": transcript, "language": str(language).split("-")[0].lower(), "confidence": None}
        except Exception as exc:
            raise SpeechProviderError("OpenAI speech recognition could not process the audio") from exc

@lru_cache(maxsize=1)
def _whisper_model():
    try:
        from faster_whisper import WhisperModel
    except ImportError as exc:
        raise SpeechProviderError("Whisper dependencies are not installed") from exc
    model_name = os.getenv("WHISPER_MODEL", "small")
    device = os.getenv("WHISPER_DEVICE", "cpu")
    compute_type = os.getenv("WHISPER_COMPUTE_TYPE", "int8" if device == "cpu" else "float16")
    return WhisperModel(model_name, device=device, compute_type=compute_type)

def detect_yes_no(transcript: str, language: str) -> str | None:
    """Conservative vocabulary for common supported Indian languages."""
    words = set(transcript.casefold().strip(" .!?।,;:").split())
    yes = {"en":{"yes","yeah","yep"},"hi":{"हाँ","हां","जी","ठीक"},"ta":{"ஆம்","ஆமா","சரி"},"te":{"అవును","ఔను","సరే"},"bn":{"হ্যাঁ","জি","ঠিক"},"kn":{"ಹೌದು","ಸರಿ"},"ml":{"അതെ","ശരി"},"mr":{"हो","होय","ठीक"},"gu":{"હા","બરાબર"},"pa":{"ਹਾਂ","ਜੀ","ਠੀਕ"}}
    no = {"en":{"no","nope","nah"},"hi":{"नहीं","ना"},"ta":{"இல்லை","இல்ல"},"te":{"కాదు","లేదు"},"bn":{"না","নয়"},"kn":{"ಇಲ್ಲ"},"ml":{"ഇല്ല"},"mr":{"नाही"},"gu":{"ના","નહીં"},"pa":{"ਨਹੀਂ","ਨਾ"}}
    if words & yes.get(language, set()):
        return "yes"
    if words & no.get(language, set()):
        return "no"
    return None
