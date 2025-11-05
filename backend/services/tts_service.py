import os
import tempfile
from typing import Optional
from loguru import logger
from config import settings


def _synthesize_with_gtts(text: str, lang: str = "ar") -> Optional[str]:
    try:
        from gtts import gTTS
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        tts = gTTS(text=text, lang=lang, slow=False)
        tts.save(tmp.name)
        return tmp.name
    except Exception as e:
        logger.error(f"gTTS synthesis failed: {e}")
        return None


def _synthesize_with_azure(text: str, voice: str) -> Optional[str]:
    try:
        import azure.cognitiveservices.speech as speechsdk
        key = settings.AZURE_SPEECH_KEY
        region = settings.AZURE_SPEECH_REGION
        if not key or not region:
            raise ValueError("Azure Speech credentials missing")
        speech_config = speechsdk.SpeechConfig(subscription=key, region=region)
        speech_config.speech_synthesis_voice_name = voice
        audio_config = speechsdk.audio.AudioOutputConfig(use_default_speaker=False)
        # Synthesize to file via temp
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        audio_config = speechsdk.audio.AudioOutputConfig(filename=tmp.name)
        synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)
        result = synthesizer.speak_text_async(text).get()
        if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
            return tmp.name
        else:
            logger.error(f"Azure TTS failed: {result.reason}")
            return None
    except Exception as e:
        logger.error(f"Azure synthesis failed: {e}")
        return None


def _synthesize_with_elevenlabs(text: str, voice_id: str) -> Optional[str]:
    try:
        from elevenlabs import generate, set_api_key
        set_api_key(settings.ELEVENLABS_API_KEY)
        audio = generate(text=text, voice=voice_id, model="eleven_multilingual_v2")
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        with open(tmp.name, "wb") as f:
            f.write(audio)
        return tmp.name
    except Exception as e:
        logger.error(f"ElevenLabs synthesis failed: {e}")
        return None


def synthesize_speech(text: str) -> Optional[str]:
    """Return path to synthesized audio file or None on failure."""
    provider = (settings.TTS_PROVIDER or "gtts").lower()
    # Prefer Egyptian dialect voice where applicable
    voice = settings.AZURE_SPEECH_VOICE
    if provider == "azure":
        path = _synthesize_with_azure(text, voice=voice)
        if path:
            return path
        logger.warning("Falling back to gTTS after Azure failure")
        return _synthesize_with_gtts(text, lang="ar")
    if provider == "elevenlabs":
        if not settings.ELEVENLABS_API_KEY or not settings.ELEVENLABS_VOICE_ID:
            logger.warning("ElevenLabs credentials missing; using gTTS")
            return _synthesize_with_gtts(text, lang="ar")
        path = _synthesize_with_elevenlabs(text, voice_id=settings.ELEVENLABS_VOICE_ID)
        if path:
            return path
        logger.warning("Falling back to gTTS after ElevenLabs failure")
        return _synthesize_with_gtts(text, lang="ar")
    # Default gTTS
    return _synthesize_with_gtts(text, lang="ar")


