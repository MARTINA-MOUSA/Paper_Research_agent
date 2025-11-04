from moviepy.editor import TextClip, concatenate_videoclips, CompositeVideoClip, AudioFileClip
from gtts import gTTS
import tempfile
import os
from typing import List, Dict

def _estimate_duration(text: str) -> float:
    # Rough estimate: 140 wpm => ~2.33 wps => seconds = words / 2.33
    words = max(1, len(text.split()))
    return max(3.0, words / 2.3)

def make_video_from_scenes(scenes: List[Dict[str, str]], output_path: str = "output_video.mp4") -> str:
    clips = []
    temp_dir = tempfile.mkdtemp(prefix="p2v_")
    try:
        for idx, scene in enumerate(scenes):
            overlay = (scene.get("overlay") or "").strip()
            narration = (scene.get("narration") or overlay).strip()
            duration = _estimate_duration(narration)

            # TTS audio
            audio_path = os.path.join(temp_dir, f"scene_{idx}.mp3")
            tts = gTTS(text=narration, lang='ar')
            tts.save(audio_path)
            audio = AudioFileClip(audio_path)

            # Visual overlay
            text_clip = TextClip(overlay or "", fontsize=48, color='white', size=(1280, 720))
            text_clip = text_clip.set_duration(max(duration, audio.duration))

            # Combine and set audio
            composite = CompositeVideoClip([text_clip])
            composite = composite.set_audio(audio)
            composite = composite.set_duration(max(duration, audio.duration))
            clips.append(composite)

        if not clips:
            raise ValueError("No scenes to render")

        video = concatenate_videoclips(clips)
        video.write_videofile(output_path, fps=24)
        return output_path
    finally:
        # Cleanup temp audio files
        try:
            for f in os.listdir(temp_dir):
                os.remove(os.path.join(temp_dir, f))
            os.rmdir(temp_dir)
        except Exception:
            pass

