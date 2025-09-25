import vosk
import pyaudio
import json
import os
import time
from .error_handler import STTError
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .logging_system import LoggingSystem

class SpeechToText:
    def __init__(self, model_path: str, sample_rate: int, chunk_size: int, logger: 'LoggingSystem'):
        self.model_path = model_path
        self.sample_rate = sample_rate
        self.chunk_size = chunk_size
        self.logger = logger
        self.model = None
        self.recognizer = None
        self.audio_stream = None
        self.pyaudio_instance = None

        try:
            self.initialize_model()
        except STTError as e:
            self.logger.log_activity("STT_ERROR", f"Failed to initialize STT: {e}")
            
    def initialize_model(self):
        if not os.path.exists(self.model_path):
            raise STTError(f"Vosk model path not found: {self.model_path}")
        try:
            self.model = vosk.Model(self.model_path)
            self.recognizer = vosk.KaldiRecognizer(self.model, self.sample_rate)
            self.pyaudio_instance = pyaudio.PyAudio()
            self.logger.log_activity("STT", "Vosk model and PyAudio initialized.")
        except Exception as e:
            raise STTError(f"Could not initialize Vosk model or PyAudio: {e}")

    def listen_for_speech(self, timeout=7) -> str:
        if not self.recognizer or not self.pyaudio_instance:
            self.logger.log_activity("STT_ERROR", "STT system not initialized, cannot listen.")
            return ""

        try:
            self.audio_stream = self.pyaudio_instance.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=self.sample_rate,
                input=True,
                frames_per_buffer=self.chunk_size
            )
            self.logger.log_activity("STT", "Listening for speech...")
            
            start_time = time.time()
            while True:
                # Timeout check
                if time.time() - start_time > timeout:
                    self.logger.log_activity("STT", "Listening timed out due to silence.")
                    break

                data = self.audio_stream.read(self.chunk_size, exception_on_overflow=False)
                if self.recognizer.AcceptWaveform(data):
                    result = json.loads(self.recognizer.Result())
                    text = result.get("text", "")
                    if text:
                        self.logger.log_stt(text, result.get("confidence", 1.0))
                        return text
                else:
                    # Check for partial result to detect voice activity
                    partial_result = json.loads(self.recognizer.PartialResult())
                    if partial_result.get("partial"):
                        # Reset timeout if user is speaking
                        start_time = time.time()

        except Exception as e:
            self.logger.log_activity("STT_ERROR", f"Error during speech recognition: {e}")
            return ""
        finally:
            self.stop_listening()
        return ""

    def stop_listening(self):
        if self.audio_stream and self.audio_stream.is_active():
            self.audio_stream.stop_stream()
            self.audio_stream.close()
            self.audio_stream = None
            self.logger.log_activity("STT", "Stopped listening.")

    def cleanup(self):
        if self.pyaudio_instance:
            self.pyaudio_instance.terminate()
            self.logger.log_activity("STT", "PyAudio terminated.")
