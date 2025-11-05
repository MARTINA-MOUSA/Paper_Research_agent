import tempfile
import os
from typing import List, Dict
from loguru import logger

os.environ["IMAGEMAGICK_BINARY"] = r"C:\Program Files\ImageMagick-7.1.2-Q16-HDRI\magick.exe"
os.environ["IMAGE_MAGICK_CONVERT"] = os.environ["IMAGEMAGICK_BINARY"]

from moviepy.editor import TextClip, concatenate_videoclips, CompositeVideoClip, AudioFileClip, ColorClip
from gtts import gTTS

def _estimate_duration(text: str) -> float:
    # Rough estimate: 140 wpm => ~2.33 wps => seconds = words / 2.33
    words = max(1, len(text.split()))
    return max(3.0, words / 2.3)

def make_video_from_scenes(scenes: List[Dict[str, str]], output_path: str = "output_video.mp4") -> str:
    """
    Create video from scenes with Arabic narration and text overlays
    """
    clips = []
    temp_dir = tempfile.mkdtemp(prefix="p2v_")
    
    try:
        logger.info(f"Creating video with {len(scenes)} scenes")
        
        for idx, scene in enumerate(scenes):
            overlay = (scene.get("overlay") or "").strip()
            narration = (scene.get("narration") or overlay).strip()
            
            if not narration:
                logger.warning(f"Skipping empty scene {idx}")
                continue
            
            duration = _estimate_duration(narration)

            # TTS audio
            audio_path = os.path.join(temp_dir, f"scene_{idx}.mp3")
            try:
                tts = gTTS(text=narration, lang='ar', slow=False)
                tts.save(audio_path)
                audio = AudioFileClip(audio_path)
                actual_duration = max(duration, audio.duration)
            except Exception as e:
                logger.error(f"TTS error for scene {idx}: {e}")
                # Fallback: create silent clip
                audio = None
                actual_duration = duration

            # Background
            bg = ColorClip(size=(1280, 720), color=(0, 0, 0), duration=actual_duration)
            
            # Visual overlay text
            if overlay:
                text_clip = TextClip(
                    overlay,
                    fontsize=48,
                    color='white',
                    size=(1200, None),
                    method='caption',
                    align='center',
                    font='Arial-Bold'
                ).set_duration(actual_duration).set_position('center')
            else:
                text_clip = None

            # Combine clips
            if text_clip:
                composite = CompositeVideoClip([bg, text_clip])
            else:
                composite = bg
            
            if audio:
                composite = composite.set_audio(audio)
            
            composite = composite.set_duration(actual_duration)
            clips.append(composite)

        if not clips:
            raise ValueError("No valid scenes to render")

        logger.info("Concatenating video clips...")
        video = concatenate_videoclips(clips, method="compose")
        
        logger.info(f"Writing video to {output_path}...")
        video.write_videofile(
            output_path,
            fps=24,
            codec='libx264',
            audio_codec='aac',
            temp_audiofile=os.path.join(temp_dir, "temp_audio.m4a"),
            remove_temp=True,
            verbose=False,
            logger=None
        )
        
        # Close clips to free memory
        video.close()
        for clip in clips:
            clip.close()
        
        logger.info(f"Video created successfully: {output_path}")
        return output_path
        
    except Exception as e:
        logger.error(f"Error creating video: {e}", exc_info=True)
        raise
    finally:
        # Cleanup temp audio files
        try:
            for f in os.listdir(temp_dir):
                try:
                    os.remove(os.path.join(temp_dir, f))
                except Exception:
                    pass
            os.rmdir(temp_dir)
        except Exception as e:
            logger.warning(f"Could not cleanup temp directory: {e}")

