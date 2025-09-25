import time
from .error_handler import MotorError
from .logging_system import LoggingSystem
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .logging_system import LoggingSystem

class MotorController:
    def __init__(self, platform: str, motor_pins: dict, logger: 'LoggingSystem'):
        self.platform = platform
        self.motor_pins = motor_pins
        self.logger = logger
        self.gpio = None

        if self.platform == "raspberry_pi":
            try:
                import RPi.GPIO as GPIO
                self.gpio = GPIO
                self.gpio.setmode(self.gpio.BCM)
                # Setup motor pins
                for motor in self.motor_pins.values():
                    for pin in motor:
                        self.gpio.setup(pin, self.gpio.OUT)
                        self.gpio.output(pin, self.gpio.LOW)
                self.logger.log_activity("MOTOR", "GPIO pins initialized for motors.")
            except (ImportError, RuntimeError) as e:
                self.logger.log_activity("MOTOR_ERROR", f"Failed to initialize GPIO: {e}. Running in simulation mode.")
                self.platform = "windows" # Fallback to simulation
        
        self.logger.log_activity("MOTOR", f"Motor controller initialized in {self.platform} mode.")

    def move_forward(self, duration: float = None):
        self.logger.log_activity("MOTOR_COMMAND", f"move_forward for {duration}s")
        if self.platform == "raspberry_pi":
            # Assuming a simple HIGH/LOW for direction for now.
            # Front Left
            self.gpio.output(self.motor_pins['front_left'][0], self.gpio.HIGH)
            self.gpio.output(self.motor_pins['front_left'][1], self.gpio.LOW)
            # Front Right
            self.gpio.output(self.motor_pins['front_right'][0], self.gpio.HIGH)
            self.gpio.output(self.motor_pins['front_right'][1], self.gpio.LOW)
            # Rear Left
            self.gpio.output(self.motor_pins['rear_left'][0], self.gpio.HIGH)
            self.gpio.output(self.motor_pins['rear_left'][1], self.gpio.LOW)
            # Rear Right
            self.gpio.output(self.motor_pins['rear_right'][0], self.gpio.HIGH)
            self.gpio.output(self.motor_pins['rear_right'][1], self.gpio.LOW)
        else:
            print("SIMULATOR: Moving forward.")

        if duration:
            time.sleep(duration)
            self.stop()
        self.logger.log_movement("forward", duration, True)


    def move_backward(self, duration: float = None):
        self.logger.log_activity("MOTOR_COMMAND", f"move_backward for {duration}s")
        if self.platform == "raspberry_pi":
            # Front Left
            self.gpio.output(self.motor_pins['front_left'][0], self.gpio.LOW)
            self.gpio.output(self.motor_pins['front_left'][1], self.gpio.HIGH)
            # Front Right
            self.gpio.output(self.motor_pins['front_right'][0], self.gpio.LOW)
            self.gpio.output(self.motor_pins['front_right'][1], self.gpio.HIGH)
            # Rear Left
            self.gpio.output(self.motor_pins['rear_left'][0], self.gpio.LOW)
            self.gpio.output(self.motor_pins['rear_left'][1], self.gpio.HIGH)
            # Rear Right
            self.gpio.output(self.motor_pins['rear_right'][0], self.gpio.LOW)
            self.gpio.output(self.motor_pins['rear_right'][1], self.gpio.HIGH)
        else:
            print("SIMULATOR: Moving backward.")

        if duration:
            time.sleep(duration)
            self.stop()
        self.logger.log_movement("backward", duration, True)

    def turn_left(self, angle: float = 90):
        duration = angle / 90.0 # Simple linear relationship, assuming 1s for 90 degrees
        self.logger.log_activity("MOTOR_COMMAND", f"turn_left for {angle} degrees ({duration}s)")
        if self.platform == "raspberry_pi":
            # Left side backward, right side forward
            self.gpio.output(self.motor_pins['front_left'][0], self.gpio.LOW)
            self.gpio.output(self.motor_pins['front_left'][1], self.gpio.HIGH)
            self.gpio.output(self.motor_pins['rear_left'][0], self.gpio.LOW)
            self.gpio.output(self.motor_pins['rear_left'][1], self.gpio.HIGH)
            self.gpio.output(self.motor_pins['front_right'][0], self.gpio.HIGH)
            self.gpio.output(self.motor_pins['front_right'][1], self.gpio.LOW)
            self.gpio.output(self.motor_pins['rear_right'][0], self.gpio.HIGH)
            self.gpio.output(self.motor_pins['rear_right'][1], self.gpio.LOW)
        else:
            print("SIMULATOR: Turning left.")
        
        time.sleep(duration)
        self.stop()
        self.logger.log_movement("left", duration, True)

    def turn_right(self, angle: float = 90):
        duration = angle / 90.0 # Simple linear relationship, assuming 1s for 90 degrees
        self.logger.log_activity("MOTOR_COMMAND", f"turn_right for {angle} degrees ({duration}s)")
        if self.platform == "raspberry_pi":
            # Right side backward, left side forward
            self.gpio.output(self.motor_pins['front_right'][0], self.gpio.LOW)
            self.gpio.output(self.motor_pins['front_right'][1], self.gpio.HIGH)
            self.gpio.output(self.motor_pins['rear_right'][0], self.gpio.LOW)
            self.gpio.output(self.motor_pins['rear_right'][1], self.gpio.HIGH)
            self.gpio.output(self.motor_pins['front_left'][0], self.gpio.HIGH)
            self.gpio.output(self.motor_pins['front_left'][1], self.gpio.LOW)
            self.gpio.output(self.motor_pins['rear_left'][0], self.gpio.HIGH)
            self.gpio.output(self.motor_pins['rear_left'][1], self.gpio.LOW)
        else:
            print("SIMULATOR: Turning right.")

        time.sleep(duration)
        self.stop()
        self.logger.log_movement("right", duration, True)

    def stop(self):
        self.logger.log_activity("MOTOR_COMMAND", "stop")
        if self.platform == "raspberry_pi":
            for motor in self.motor_pins.values():
                for pin in motor:
                    self.gpio.output(pin, self.gpio.LOW)
        else:
            print("SIMULATOR: Stopping motors.")
        self.logger.log_movement("stop", 0, True)

    def cleanup(self):
        if self.platform == "raspberry_pi" and self.gpio:
            self.gpio.cleanup()
            self.logger.log_activity("MOTOR", "GPIO cleanup complete.")
