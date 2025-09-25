# AI Robot 4WD - Intelligent Voice-Controlled Robot

An AI-powered 4-wheel drive Raspberry Pi robot with voice interaction, autonomous navigation, and visual feedback through facial expressions. The robot integrates multiple sensors, motors, and AI services to provide an interactive and intelligent robotic platform.

## 🤖 Features

- **Voice Interaction**: Natural language processing with speech-to-text and text-to-speech
- **AI Integration**: OpenAI API with local GGUF model fallback
- **Autonomous Navigation**: Obstacle avoidance using ultrasonic sensors
- **Visual Feedback**: Facial expressions displayed on screen
- **Cross-Platform**: Development on Windows, deployment on Raspberry Pi
- **Comprehensive Logging**: Activity tracking and conversation memory
- **Modular Architecture**: Clean separation of concerns for easy maintenance

## 📋 Table of Contents

- [Quick Start](#quick-start)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Voice Commands](#voice-commands)
- [Hardware Setup](#hardware-setup)
- [Development](#development)
- [API Documentation](#api-documentation)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Virtual environment (recommended)
- For Raspberry Pi: GPIO access and connected hardware

### Basic Installation

```bash
# Clone the repository
git clone <repository-url>
cd ai-robot-4wd

# Create virtual environment
python -m venv myvenv

# Activate virtual environment
# Windows:
myvenv\Scripts\activate
# Linux/Mac:
source myvenv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the robot (simulation mode on Windows)
python main.py
```

## 📦 Installation

### System Requirements

- **Operating System**: Windows 10+ (development), Raspberry Pi OS (production)
- **Python**: 3.8 or higher
- **Memory**: 2GB RAM minimum, 4GB recommended
- **Storage**: 2GB free space for models and logs

For detailed installation instructions, see [docs/INSTALLATION.md](docs/INSTALLATION.md).

### Detailed Installation Steps

#### 1. Environment Setup

```bash
# Create and activate virtual environment
python -m venv myvenv

# Windows activation
myvenv\Scripts\activate

# Linux/Mac activation
source myvenv/bin/activate
```

#### 2. Install Dependencies

```bash
# Install all dependencies
pip install -r requirements.txt

# For development (includes testing tools)
pip install -r requirements.txt pytest pytest-mock pytest-cov
```

#### 3. Download AI Models

```bash
# Create models directory
mkdir models

# Download Vosk speech recognition model
# Visit: https://alphacephei.com/vosk/models
# Download vosk-model-small-en-in-0.4.zip
# Extract to models/vosk-model-small-en-in-0.4/

# For local LLM (optional)
# Download a GGUF model file to models/local-model.gguf
```

#### 4. Configure the Robot

```bash
# Copy and edit configuration
cp config.json config.json.backup
# Edit config.json with your settings (see Configuration section)
```

#### 5. Test Installation

```bash
# Test basic functionality (no STT dependencies required)
python test_main_without_stt.py

# Test with full functionality (requires all dependencies)
python test_main_demo.py

# Run comprehensive test suite
python run_tests.py
```

## ⚙️ Configuration

The robot is configured through `config.json`. Here are the key sections:

### Audio Configuration

```json
{
  "audio": {
    "vosk_model_path": "models/vosk-model-small-en-in-0.4",
    "piper_voice": "en_US-amy-medium",
    "sample_rate": 16000,
    "chunk_size": 4096
  }
}
```

### AI Configuration

```json
{
  "ai": {
    "openai_api_key": "your-openai-api-key-here",
    "local_model_path": "models/local-model.gguf",
    "max_context_length": 4096,
    "temperature": 0.7
  }
}
```

### Hardware Configuration

```json
{
  "hardware": {
    "platform": "windows",  // or "raspberry_pi"
    "motor_pins": {
      "front_left": [18, 19],
      "front_right": [20, 21],
      "rear_left": [22, 23],
      "rear_right": [24, 25]
    },
    "sensor_pins": {
      "front_trigger": 2,
      "front_echo": 3,
      "left_trigger": 4,
      "left_echo": 5,
      "right_trigger": 6,
      "right_echo": 7
    }
  }
}
```

For detailed configuration options, see [docs/CONFIGURATION.md](docs/CONFIGURATION.md).

## 🎯 Usage

### Starting the Robot

```bash
# Activate virtual environment
source myvenv/bin/activate  # Linux/Mac
# or
myvenv\Scripts\activate     # Windows

# Start the robot
python main.py
```

### Voice Commands

The robot responds to natural language commands:

#### Movement Commands
- "Go forward" / "Move forward"
- "Go backward" / "Move backward" 
- "Turn left"
- "Turn right"
- "Stop"

#### Conversation Commands
- "Hello" / "Hi"
- "What can you do?"
- "Trace your steps back"
- "Remember our conversation"

#### System Commands
- "Show me your status"
- "What do you see?" (sensor readings)

### Programmatic Usage

```python
from main import RobotController

# Create robot instance
robot = RobotController()

# Initialize all components
if robot.initialize_components():
    # Send direct command
    robot.handle_voice_command("go forward")
    
    # Get system status
    status = robot.get_status()
    print(f"Robot status: {status}")
    
    # Graceful shutdown
    robot.shutdown()
```

## 🔧 Hardware Setup

### Raspberry Pi Wiring

#### Motor Connections (4WD)
- **Front Left Motor**: GPIO 18 (PWM), GPIO 19 (Direction)
- **Front Right Motor**: GPIO 20 (PWM), GPIO 21 (Direction)
- **Rear Left Motor**: GPIO 22 (PWM), GPIO 23 (Direction)
- **Rear Right Motor**: GPIO 24 (PWM), GPIO 25 (Direction)

#### Sensor Connections (Ultrasonic)
- **Front Sensor**: Trigger GPIO 2, Echo GPIO 3
- **Left Sensor**: Trigger GPIO 4, Echo GPIO 5
- **Right Sensor**: Trigger GPIO 6, Echo GPIO 7

#### Audio Setup
- **Microphone**: USB microphone or Pi camera module
- **Speaker**: 3.5mm jack or USB speaker
- **Display**: HDMI monitor or touchscreen

For detailed wiring diagrams, see [docs/HARDWARE_SETUP.md](docs/HARDWARE_SETUP.md).

## 👨‍💻 Development

### Project Structure

```
ai-robot-4wd/
├── src/                    # Core modules
│   ├── ai_processor.py     # AI coordination
│   ├── command_processor.py # Command parsing
│   ├── config.py          # Configuration management
│   ├── error_handler.py   # Error handling
│   ├── face_display.py    # Visual feedback
│   ├── local_llm.py       # Local AI model
│   ├── logging_system.py  # Activity logging
│   ├── motor_controller.py # Movement control
│   ├── openai_client.py   # OpenAI integration
│   ├── sensors.py         # Sensor management
│   ├── speech_to_text.py  # Voice input
│   └── text_to_speech.py  # Voice output
├── tests/                 # Test suite
├── Faces/                 # Facial expression images
├── logs/                  # Activity logs
├── models/                # AI models
├── main.py               # Main controller
├── config.json           # Configuration
└── requirements.txt      # Dependencies
```

### Running Tests

```bash
# Run all tests
python run_tests.py

# Run specific test categories
python -m pytest tests/test_integration_voice_to_action.py
python -m pytest tests/test_platform_compatibility.py
python -m pytest tests/test_performance.py

# Run with coverage
python -m pytest --cov=src tests/
```

### Adding New Features

1. **Create Module**: Add new module in `src/`
2. **Update Main Controller**: Add initialization in `main.py`
3. **Add Tests**: Create corresponding test file
4. **Update Documentation**: Add to relevant docs
5. **Update Configuration**: Add config options if needed

For detailed development guidelines, see [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md).

## 📚 API Documentation

### Core Classes

- **RobotController**: Main orchestrator
- **SpeechToText**: Voice input processing
- **TextToSpeech**: Voice output generation
- **AIProcessor**: AI response coordination
- **MotorController**: Movement control
- **SensorManager**: Obstacle detection
- **FaceDisplay**: Visual feedback

For complete API documentation, see [docs/API.md](docs/API.md).

## 🔍 Troubleshooting

### Common Issues

#### No Voice Recognition
```bash
# Check microphone access
python -c "import pyaudio; print('PyAudio OK')"

# Test Vosk model
python test_stt_demo.py
```

#### No AI Response
```bash
# Check OpenAI API key
python test_ai_demo.py

# Test local model fallback
python -c "from src.local_llm import LocalLLM; llm = LocalLLM('models/local-model.gguf')"
```

#### Motor Control Issues
```bash
# Test motor simulation
python test_motor_demo.py

# Check GPIO permissions (Raspberry Pi)
sudo usermod -a -G gpio $USER
```

For comprehensive troubleshooting, see [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md).

## 📊 Logging and Monitoring

The robot maintains comprehensive logs in the `logs/` directory:

- **conversation_log.json**: All AI conversations
- **movement_log.json**: Motor commands and actions
- **stt_log.json**: Speech recognition results
- **tts_log.json**: Text-to-speech outputs
- **combined_activity.txt**: Human-readable activity log

### Viewing Logs

```bash
# View recent conversations
python -c "from src.logging_system import LoggingSystem; ls = LoggingSystem('logs'); print(ls.get_conversation_history(5))"

# View movement history
python -c "from src.logging_system import LoggingSystem; ls = LoggingSystem('logs'); print(ls.get_movement_history(5))"
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for new functionality
5. Run the test suite (`python run_tests.py`)
6. Commit your changes (`git commit -m 'Add amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Vosk](https://alphacephei.com/vosk/) for speech recognition
- [OpenAI](https://openai.com/) for AI processing
- [Piper TTS](https://github.com/rhasspy/piper) for text-to-speech
- [Pygame](https://www.pygame.org/) for display management
- [llama.cpp](https://github.com/ggerganov/llama.cpp) for local AI models

## 📞 Support

- **Documentation**: Check the `docs/` directory
- **Issues**: Open an issue on GitHub
- **Discussions**: Use GitHub Discussions for questions

---

**Happy Robotics! 🤖**