from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health():
    assert client.get("/api/health").json()["status"] == "ok"

def test_openai_chat_and_realtime_report_missing_configuration(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    chat = client.post("/api/openai/chat", data={"message": "Help me understand PMMVY"})
    voice = client.post("/api/openai/realtime-token", data={"language": "English"})
    assert chat.status_code == 503
    assert voice.status_code == 503

def test_schemes_and_rule_loading():
    assert client.get("/api/schemes").json()["schemes"][0]["scheme_id"] == "pmmvy"
    assert "official_source" in client.get("/api/schemes/pmmvy").json()

def test_eligibility_is_guidance_only():
    response = client.post("/api/eligibility/check", json={"pregnant": True, "first_child": True, "has_eligibility_proof": True})
    assert response.status_code == 200
    assert response.json()["determination"] == "guidance_only"

def test_invalid_and_missing_input():
    assert client.post("/api/eligibility/check", json={"pregnant": "yes"}).status_code == 422

def test_chat_fallback(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    response = client.post("/api/chat", json={"message": "What is this?", "language": "en"})
    assert response.status_code == 200
    assert response.json()["mode"] == "fallback"

def test_gemini_failure_fallback(monkeypatch):
    import httpx
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    def broken_client(*args, **kwargs):
        raise httpx.ConnectError("offline")
    monkeypatch.setattr(httpx, "AsyncClient", broken_client)
    response = client.post("/api/chat", json={"message": "What is this?", "language": "en"})
    assert response.status_code == 200
    assert response.json()["mode"] == "fallback"

def test_session():
    created = client.post("/api/session", json={"language": "ta", "demo_mode": True}).json()
    assert client.get("/api/session/" + created["session_id"]).json()["language"] == "ta"

def test_voice_language_detection_and_same_language_fallback(monkeypatch):
    from app.main import speech_service
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.setattr(speech_service, "transcribe", lambda audio: {"transcript": "ஆம்", "language": "ta", "confidence": 0.91})
    response = client.post("/api/voice/chat", files={"audio": ("sample.webm", b"audio-bytes", "audio/webm")})
    assert response.status_code == 200
    assert response.json()["language"] == "ta"
    assert response.json()["intent"] == "yes"
    assert response.json()["reply_language"] == "ta"

def test_openai_transcriber_uses_indian_language_context_and_detected_language(monkeypatch):
    import httpx
    from io import BytesIO
    from app.services.speech import SpeechLanguageService
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    captured = {}
    class FakeResponse:
        def raise_for_status(self): pass
        def json(self): return {"text": "à²¨à²¾à²¨à³ à²…à²°à³à²¹à²¤à³† à²¤à²¿à²³à²¿à²¦à³à²•à³Šà²³à³à²³à²¬à³‡à²•à³", "languages": [{"code": "kn"}]}
    class FakeClient:
        def __init__(self, **kwargs): pass
        def __enter__(self): return self
        def __exit__(self, *args): pass
        def post(self, url, **kwargs):
            captured.update(url=url, **kwargs)
            return FakeResponse()
    monkeypatch.setattr(httpx, "Client", FakeClient)
    result = SpeechLanguageService().transcribe(BytesIO(b"audio"))
    assert result["language"] == "kn"
    assert result["transcript"]
    assert result["confidence"] is None
    assert captured["data"]["model"] == "gpt-transcribe"
    assert "Tamil" in captured["data"]["prompt"]

def test_openai_detected_language_is_used_for_voice_reply(monkeypatch):
    import asyncio
    from app.main import speech_service
    import app.main as main
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setattr(speech_service, "transcribe", lambda audio: {"transcript": "à²¨à²¾à²¨à³ à²¯à³‹à²œà²¨à³† à²¬à²—à³à²—à³† à²•à³‡à²³à²²à³ à²¬à²¯à²¸à³à²¤à³à²¤à³‡à²¨à³†", "language": "kn", "confidence": None})
    async def fake_chat(**kwargs):
        assert "à²¨à²¾à²¨à³ à²¯à³‹à²œà²¨à³†" in kwargs["message"]
        return {"reply": "à²‡à²¦à³ PMMVY à²¯à³‹à²œà²¨à³†à²¯ à²®à²¾à²°à³à²—à²¦à²°à³à²¶à²¨.", "reply_language": "kn"}
    monkeypatch.setattr(main, "openai_chat", fake_chat)
    response = client.post("/api/voice/chat", files={"audio": ("sample.webm", b"audio", "audio/webm")})
    assert response.status_code == 200
    assert response.json()["language"] == "kn"
    assert response.json()["reply_language"] == "kn"
    assert response.json()["speech_provider"] == "openai"

def test_voice_low_confidence_asks_for_retry(monkeypatch):
    from app.main import speech_service
    monkeypatch.setattr(speech_service, "transcribe", lambda audio: {"transcript": "maybe", "language": "en", "confidence": 0.2})
    response = client.post("/api/voice/chat", files={"audio": ("sample.webm", b"audio-bytes", "audio/webm")})
    assert response.status_code == 200
    assert response.json()["needs_repeat"] is True
    assert response.json()["reply"] is None

def test_voice_rejects_non_audio():
    response = client.post("/api/voice/chat", files={"audio": ("sample.txt", b"not audio", "text/plain")})
    assert response.status_code == 415

def test_voice_reply_fallback_without_gemini(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    response = client.post("/api/voice/synthesize", json={"text": "à®µà®£à®•à¯à®•à®®à¯", "language": "ta"})
    assert response.status_code == 503
