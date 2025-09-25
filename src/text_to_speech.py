
import os
import subprocess
import tempfile
import time
from typing import TYPE_CHECKING

import pygame

from .config import AudioConfig
from .error_handler import TTSError
from .logging_system import LoggingSystem

if TYPE_CHECKING:
    pass

class TextToSpeech:
    """
    A robust Text-to-Speech engine that uses the Piper command-line interface (CLI)
    to prevent Python library conflicts. It generates a unique temporary file for each
    speech request to completely avoid file-locking issues.
    """
    def __init__(self, config: AudioConfig, logger: 'LoggingSystem'):
        self.config = config
        self.logger = logger

        # --- Get the absolute path to the voice model ---
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.model_path = os.path.join(base_dir, 'voices', f"{self.config.piper_voice}.onnx")

        if not os.path.exists(self.model_path):
            raise TTSError(f"Voice model file not found at: {self.model_path}")

        try:
            # --- Initialize Pygame Mixer for playback ---
            pygame.mixer.init()
            self.logger.log_activity("TTS", "Pygame mixer initialized for audio playback.")
        except Exception as e:
            self.logger.log_activity("TTS_ERROR", f"CRITICAL: Failed to initialize pygame mixer: {e}")

    def speak(self, text: str):
        if not pygame.mixer.get_init():
            self.logger.log_activity("TTS_ERROR", "Pygame mixer not initialized. Cannot speak.")
            return

        temp_wav_path = None
        try:
            # 1. Create a unique temporary file for this specific speech request
            # This completely avoids file locking/re-use issues.
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
                temp_wav_path = tmp_file.name
            
            # 2. Construct the command for the Piper CLI
            command = f'piper --model "{self.model_path}" --output_file "{temp_wav_path}" "{text}"'
            self.logger.log_activity("TTS_DEBUG", f"Running CLI command: {command}")

            # 3. Run the synthesis in a separate, isolated process
            subprocess.run(command, capture_output=True, text=True, check=True, shell=True)
            self.logger.log_activity("TTS_DEBUG", "Piper CLI synthesis completed successfully.")

            # 4. Play the generated WAV file
            self.logger.log_activity("TTS", f"Speaking: '{text[:50]}...'")
            pygame.mixer.music.load(temp_wav_path)
            pygame.mixer.music.play()

            # 5. Wait for playback to finish
            while pygame.mixer.music.get_busy():
                time.sleep(0.1)
            
            self.logger.log_tts(text, True)

        except subprocess.CalledProcessError as e:
            self.logger.log_tts(text, False)
            self.logger.log_activity("TTS_ERROR", f"Piper CLI synthesis failed with exit code {e.returncode}.")
            self.logger.log_activity("TTS_ERROR", f"Stderr from piper: {e.stderr.strip()}")
        except Exception as e:
            self.logger.log_tts(text, False)
            self.logger.log_activity("TTS_ERROR", f"Failed during CLI synthesis or playback: {e}")
        finally:
            # 6. Clean up the unique temporary file robustly
            if pygame.mixer.get_init():
                pygame.mixer.music.stop()
                pygame.mixer.music.unload()
            
            if temp_wav_path and os.path.exists(temp_wav_path):
                try:
                    os.remove(temp_wav_path)
                except OSError as e:
                    self.logger.log_activity("TTS_WARN", f"Could not remove temp file: {e}")

    def cleanup(self):
        if pygame.mixer.get_init():
            pygame.mixer.quit()
            self.logger.log_activity("TTS", "Pygame mixer shut down.")
