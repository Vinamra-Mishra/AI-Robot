import time
import random
from .error_handler import SensorError
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .logging_system import LoggingSystem

class SensorManager:
    def __init__(self, platform: str, sensor_pins: dict, logger: 'LoggingSystem'):
        self.platform = platform
        self.sensor_pins = sensor_pins
        self.logger = logger
        self.gpio = None

        if self.platform == "raspberry_pi":
            try:
                import RPi.GPIO as GPIO
                self.gpio = GPIO
                self.gpio.setmode(self.gpio.BCM)
                # Setup sensor pins
                for trigger_pin_key, echo_pin_key in [("front_trigger", "front_echo"), ("left_trigger", "left_echo"), ("right_trigger", "right_echo")]:
                    if trigger_pin_key in self.sensor_pins and echo_pin_key in self.sensor_pins:
                        self.gpio.setup(self.sensor_pins[trigger_pin_key], self.gpio.OUT)
                        self.gpio.setup(self.sensor_pins[echo_pin_key], self.gpio.IN)
                self.logger.log_activity("SENSOR", "GPIO pins initialized for sensors.")
            except (ImportError, RuntimeError) as e:
                self.logger.log_activity("SENSOR_ERROR", f"Failed to initialize GPIO for sensors: {e}. Running in simulation mode.")
                self.platform = "windows" # Fallback to simulation
        
        self.logger.log_activity("SENSOR", f"Sensor manager initialized in {self.platform} mode.")

    def _get_distance(self, trigger_pin_key: str, echo_pin_key: str) -> float:
        if self.platform == "raspberry_pi":
            if trigger_pin_key not in self.sensor_pins or echo_pin_key not in self.sensor_pins:
                self.logger.log_activity("SENSOR_ERROR", f"Sensor pins {trigger_pin_key} or {echo_pin_key} not configured.")
                return float('inf')

            trigger_pin = self.sensor_pins[trigger_pin_key]
            echo_pin = self.sensor_pins[echo_pin_key]
            
            self.gpio.output(trigger_pin, True)
            time.sleep(0.00001)
            self.gpio.output(trigger_pin, False)

            start_time = time.time()
            stop_time = time.time()

            # Wait for the echo pin to go high
            timeout = time.time() + 0.1 # 100ms timeout
            while self.gpio.input(echo_pin) == 0 and time.time() < timeout:
                start_time = time.time()

            # Wait for the echo pin to go low
            timeout = time.time() + 0.1 # 100ms timeout
            while self.gpio.input(echo_pin) == 1 and time.time() < timeout:
                stop_time = time.time()

            time_elapsed = stop_time - start_time
            # sonic speed = 34300 cm/s
            distance = (time_elapsed * 34300) / 2
            return distance
        else:
            # Simulate sensor reading
            return random.uniform(10, 300)

    def read_front_sensor(self) -> float:
        return self._get_distance("front_trigger", "front_echo")

    def read_left_sensor(self) -> float:
        return self._get_distance("left_trigger", "left_echo")

    def read_right_sensor(self) -> float:
        return self._get_distance("right_trigger", "right_echo")

    def get_all_distances(self) -> dict:
        distances = {
            "front": self.read_front_sensor(),
            "left": self.read_left_sensor(),
            "right": self.read_right_sensor(),
        }
        self.logger.log_activity("SENSOR_READING", f"{distances}")
        return distances

    def check_obstacles(self) -> dict:
        distances = self.get_all_distances()
        obstacles = {
            "front": distances["front"] < 20,
            "left": distances["left"] < 15,
            "right": distances["right"] < 15,
        }
        return obstacles

    def is_path_clear(self, direction: str) -> bool:
        obstacles = self.check_obstacles()
        if direction == "forward":
            return not obstacles["front"]
        elif direction == "left":
            return not obstacles["left"]
        elif direction == "right":
            return not obstacles["right"]
        return True
        
    def cleanup(self):
        # GPIO cleanup is handled globally in main.py to avoid conflicts
        pass
