
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))
import time
import subprocess
import threading
from src.config import load_config
from src.logging_system import LoggingSystem
from src.error_handler import handle_error, RobotError
from src.ai_processor import AIProcessor
from src.motor_controller import MotorController
from src.sensors import SensorManager
from src.face_display import FaceDisplay
from src.speech_to_text import SpeechToText
from src.text_to_speech import TextToSpeech
from src.command_processor import CommandProcessor
from src.web_server import WebServer

class RobotController:
    def __init__(self):
        self.config = load_config("config.json")
        self.logger = None
        self.ai_processor = None
        self.motor_controller = None
        self.sensor_manager = None
        self.face_display = None
        self.stt = None
        self.tts = None
        self.command_processor = None
        self.web_server = None
        self.running = False
        self.log_processes = []

    def launch_log_viewers(self):
        log_dir = os.path.abspath(self.config.logging.log_directory)
        conversation_log = os.path.join(log_dir, "conversation_log.json")
        activity_log = os.path.join(log_dir, "combined_activity.txt")
        log_viewer_script = os.path.abspath("log_viewer.py")

        # Ensure log files exist
        for log_file in [conversation_log, activity_log]:
            if not os.path.exists(log_file):
                os.makedirs(os.path.dirname(log_file), exist_ok=True)
                with open(log_file, 'w') as f:
                    pass # Create empty file

        self.logger.log_activity("SYSTEM", "Launching real-time log viewers...")
        try:
            python_exe = sys.executable
            flags = 0
            if sys.platform == "win32":
                flags = subprocess.CREATE_NEW_CONSOLE

            self.log_processes.append(subprocess.Popen(
                [python_exe, log_viewer_script, conversation_log],
                creationflags=flags
            ))
            self.log_processes.append(subprocess.Popen(
                [python_exe, log_viewer_script, activity_log],
                creationflags=flags
            ))

            self.logger.log_activity("SYSTEM", "Log viewers launched.")
        except Exception as e:
            self.logger.log_activity("SYSTEM_ERROR", f"Failed to launch log viewers: {e}")

    def initialize_components(self) -> bool:
        try:
            self.logger = LoggingSystem(self.config.logging.log_directory, self.config.logging.max_log_entries)
            self.logger.log_activity("SYSTEM", "Initializing components...")

            self.tts = TextToSpeech(self.config.audio, self.logger)
            self.launch_log_viewers()

            self.face_display = FaceDisplay(self.config.display.screen_size, self.config.display.faces_directory, self.logger)
            self.face_display.start()
            
            self.ai_processor = AIProcessor(self.config.ai, self.logger)
            self.motor_controller = MotorController(self.config.hardware.platform, self.config.hardware.motor_pins, self.logger)
            self.sensor_manager = SensorManager(self.config.hardware.platform, self.config.hardware.sensor_pins, self.logger)
            self.stt = SpeechToText(self.config.audio.vosk_model_path, self.config.audio.sample_rate, self.config.audio.chunk_size, self.logger)

            self.command_processor = CommandProcessor(
                motor_controller=self.motor_controller,
                ai_processor=self.ai_processor,
                sensor_manager=self.sensor_manager,
                face_display=self.face_display,
                tts=self.tts,
                logger=self.logger
            )
            
            # --- Web Server Integration ---
            self.logger.log_activity("SYSTEM", "Initializing web server...")
            self.web_server = WebServer(robot_controller=self)
            
            web_thread = threading.Thread(target=self.web_server.run, daemon=True)
            web_thread.start()
            self.logger.log_activity("SYSTEM", "Web server started on http://0.0.0.0:5000")
            # --- End Web Server Integration ---

            self.logger.log_activity("SYSTEM", "All components initialized successfully.")
            return True
        except RobotError as e:
            handle_error(e, self.logger)
            if self.face_display:
                self.face_display.set_face("crashed")
            return False

    def run_main_loop(self):
        self.running = True
        self.logger.log_activity("SYSTEM", "Starting main loop.")
        self.face_display.set_face("neutral")
        self.tts.speak("Hello, I am online and ready.")

        while self.running:
            try:
                self.face_display.set_face("hearing")
                voice_command = self.stt.listen_for_speech()
                if voice_command:
                    self.command_processor.process_command(voice_command)
                if self.running:
                    self.face_display.set_face("neutral")
            except KeyboardInterrupt:
                self.shutdown()
            except RobotError as e:
                handle_error(e, self.logger)
                self.face_display.set_face("confused")
                time.sleep(2)
                self.face_display.set_face("neutral")

    def shutdown(self):
        if not self.running:
            return
        self.running = False
        self.logger.log_activity("SYSTEM", "Shutting down...")

        for p in self.log_processes:
            try:
                p.terminate()
            except Exception as e:
                self.logger.log_activity("SYSTEM_ERROR", f"Failed to terminate log viewer process: {e}")

        if self.motor_controller:
            self.motor_controller.stop()
        if self.face_display:
            self.face_display.set_face("crashed")
            time.sleep(1)
            self.face_display.stop()
        if self.stt:
            self.stt.cleanup()
        if self.tts:
            self.tts.cleanup()
        
        if self.config.hardware.platform == "raspberry_pi":
            try:
                import RPi.GPIO as GPIO
                GPIO.cleanup()
                self.logger.log_activity("SYSTEM", "Global GPIO cleanup complete.")
            except (ImportError, RuntimeError):
                pass

        self.logger.log_activity("SYSTEM", "Shutdown complete.")
        sys.exit(0)

if __name__ == "__main__":
    controller = RobotController()
    if controller.initialize_components():
        try:
            controller.run_main_loop()
        except KeyboardInterrupt:
            pass
        except Exception as e:
            handle_error(e, controller.logger)
        finally:
            controller.shutdown()
