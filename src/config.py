import json
from dataclasses import dataclass, field
from typing import Dict, List, Tuple

@dataclass
class AudioConfig:
    vosk_model_path: str = "models/vosk-model-small-en-in-0.4"
    piper_voice: str = "en_US-amy-medium"
    sample_rate: int = 16000
    chunk_size: int = 4096

@dataclass
class AIConfig:
    openai_api_key: str = "your-openai-api-key-here"
    openai_api_base: str = "http://localhost:5001/v1"
    openai_model_name: str = "gpt-3.5-turbo"
    local_model_path: str = "models/local-model.gguf"
    max_context_length: int = 4096
    temperature: float = 0.7

@dataclass
class HardwareConfig:
    platform: str = "windows"
    motor_pins: Dict[str, List[int]] = field(default_factory=dict)
    sensor_pins: Dict[str, int] = field(default_factory=dict)

@dataclass
class DisplayConfig:
    screen_size: Tuple[int, int] = (800, 600)
    faces_directory: str = "Faces"

@dataclass
class LoggingConfig:
    log_directory: str = "logs"
    max_log_entries: int = 1000

@dataclass
class RobotConfig:
    audio: AudioConfig = field(default_factory=AudioConfig)
    ai: AIConfig = field(default_factory=AIConfig)
    hardware: HardwareConfig = field(default_factory=HardwareConfig)
    display: DisplayConfig = field(default_factory=DisplayConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)

    @classmethod
    def from_json(cls, config_path: str) -> 'RobotConfig':
        try:
            with open(config_path, 'r') as f:
                config_data = json.load(f)
            
            # Handle tuple for screen_size
            display_config = config_data.get("display", {})
            if "screen_size" in display_config:
                display_config["screen_size"] = tuple(display_config["screen_size"])

            return cls(
                audio=AudioConfig(**config_data.get("audio", {})),
                ai=AIConfig(**config_data.get("ai", {})),
                hardware=HardwareConfig(**config_data.get("hardware", {})),
                display=DisplayConfig(**display_config),
                logging=LoggingConfig(**config_data.get("logging", {}))
            )
        except FileNotFoundError:
            print(f"Warning: Configuration file not found at {config_path}. Using default settings.")
            return cls()
        except json.JSONDecodeError:
            print(f"Warning: Could not decode JSON from {config_path}. Using default settings.")
            return cls()


def load_config(config_path: str = "config.json") -> RobotConfig:
    return RobotConfig.from_json(config_path)
