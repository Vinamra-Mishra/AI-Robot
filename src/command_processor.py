from .motor_controller import MotorController
from .ai_processor import AIProcessor
from .sensors import SensorManager
from .face_display import FaceDisplay
from .text_to_speech import TextToSpeech
from typing import TYPE_CHECKING
import time

if TYPE_CHECKING:
    from .logging_system import LoggingSystem

class CommandProcessor:
    def __init__(self, motor_controller: MotorController, ai_processor: AIProcessor, sensor_manager: SensorManager, face_display: FaceDisplay, tts: TextToSpeech, logger: 'LoggingSystem'):
        self.motor_controller = motor_controller
        self.ai_processor = ai_processor
        self.sensor_manager = sensor_manager
        self.face_display = face_display
        self.tts = tts
        self.logger = logger

    def speak_and_wait(self, text: str):
        """Change face to speaking, say the text, and revert to neutral."""
        if text:
            self.face_display.set_face("speaking")
            self.tts.speak(text)
            self.face_display.set_face("neutral")

    def _query_ai(self, text: str) -> str:
        """Sets thinking face, queries AI, and handles response, returning the text."""
        self.logger.log_activity("COMMAND_PROCESSOR", f"Querying AI with: '{text}'")
        self.face_display.set_face("thinking")
        time.sleep(0.5)  # Make sure the thinking face is visible

        response_text = self.ai_processor.send_message(text)

        is_failure = not response_text or \
                     "unable to process" in response_text.lower() or \
                     "my apologies" in response_text.lower()

        if is_failure:
            self.logger.log_activity("COMMAND_PROCESSOR", "AI response indicates failure.")
            self.face_display.set_face("confused")
            time.sleep(0.5)
            return "I'm sorry, I had trouble with that request."
        
        self.logger.log_activity("COMMAND_PROCESSOR", f"AI responded: '{response_text}'")
        return response_text

    def process_text_input(self, text: str) -> str:
        """Processes direct text input from the web UI."""
        if not text:
            return ""
        
        response_text = self._query_ai(text)
        self.speak_and_wait(response_text)
        return response_text

    def process_command(self, command_text: str):
        if not command_text:
            return
            
        command_text = command_text.lower().strip()
        self.logger.log_activity("COMMAND_PROCESSOR", f"Processing command: '{command_text}'")

        response_text = None

        # Movement Commands
        if any(cmd in command_text for cmd in ["go forward", "move forward"]):
            self.face_display.set_face("thinking")
            if self.sensor_manager.is_path_clear("forward"):
                self.face_display.set_face("happy")
                self.motor_controller.move_forward(duration=2)
            else:
                self.face_display.set_face("confused")
                response_text = "I can't move forward, there is an obstacle in my way."
        elif any(cmd in command_text for cmd in ["go backward", "move backward"]):
            self.face_display.set_face("happy")
            self.motor_controller.move_backward(duration=2)
        elif "turn left" in command_text:
            self.face_display.set_face("thinking")
            if self.sensor_manager.is_path_clear("left"):
                self.face_display.set_face("happy")
                self.motor_controller.turn_left(angle=90)
            else:
                self.face_display.set_face("confused")
                response_text = "I can't turn left, there is something in the way."
        elif "turn right" in command_text:
            self.face_display.set_face("thinking")
            if self.sensor_manager.is_path_clear("right"):
                self.face_display.set_face("happy")
                self.motor_controller.turn_right(angle=90)
            else:
                self.face_display.set_face("confused")
                response_text = "I can't turn right, there is something in the way."
        elif "stop" in command_text:
            self.motor_controller.stop()
            self.face_display.set_face("neutral")
        
        # System Commands
        elif "status" in command_text:
            self.face_display.set_face("thinking")
            distances = self.sensor_manager.get_all_distances()
            response_text = f"My sensors detect the following distances: Front {distances['front']:.1f} cm, Left {distances['left']:.1f} cm, and Right {distances['right']:.1f} cm."
        
        # Fallback to AI
        else:
            response_text = self._query_ai(command_text)

        if response_text:
            self.speak_and_wait(response_text)
