from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .logging_system import LoggingSystem

class RobotError(Exception):
    """Base exception class for the robot."""
    pass

class AIError(RobotError):
    """Exception raised for errors in the AI processing."""
    pass

class STTError(RobotError):
    """Exception raised for errors in the Speech-to-Text processing."""
    pass

class TTSError(RobotError):
    """Exception raised for errors in the Text-to-Speech processing."""
    pass

class MotorError(RobotError):
    """Exception raised for errors in the motor control."""
    pass

class SensorError(RobotError):
    """Exception raised for errors in the sensor reading."""
    pass

class ConfigError(RobotError):
    """Exception raised for errors in the configuration."""
    pass

def handle_error(error: Exception, logger: 'LoggingSystem' = None):
    """A simple, centralized error handler."""
    error_message = f"{error.__class__.__name__}: {error}"
    print(f"An error occurred: {error_message}")
    if logger:
        logger.log_activity("ERROR", error_message)
