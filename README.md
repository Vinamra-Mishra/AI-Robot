# SARAR - Intelligent Voice-Controlled 4WD Robot

An AI-powered 4-wheel drive robot with voice interaction, a web-based control dashboard, autonomous navigation, and visual feedback through facial expressions. The robot integrates multiple sensors, motors, and AI services to provide an interactive and intelligent robotic platform.

## 🤖 Core Features

- **Voice Interaction**: Natural language processing with Vosk for speech-to-text and Piper for text-to-speech.
- **Web Control Dashboard**: A full-featured web interface for manual control, text-based communication, and real-time status monitoring.
- **Defined AI Persona**: The AI is configured with a specific system prompt to act as SARAR, a physical robot, not a generic virtual assistant.
- **Dual AI Integration**: Uses the OpenAI API by default, with a local GGUF model (via LLaMA.cpp) as a seamless fallback.
- **Autonomous Navigation**: Avoids obstacles using three ultrasonic sensors (front, left, and right).
- **Visual Feedback**: A Pygame-based display shows facial expressions (happy, thinking, hearing, etc.) to communicate the robot's state.
- **Cross-Platform**: Designed for development and simulation on Windows and for deployment on a Raspberry Pi.
- **Comprehensive Logging**: Logs all conversations, movements, and system activity for easy debugging.

## 📋 Table of Contents

- [Quick Start](#-quick-start)
- [Web Interface](#-web-interface)
- [Project Structure](#-project-structure)
- [AI Persona](#-ai-persona)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Usage](#-usage)
- [Hardware Setup](#-hardware-setup)
- [Troubleshooting](#-troubleshooting)

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- A virtual environment (recommended)
- For Raspberry Pi: GPIO access and connected hardware

### Basic Installation & Launch

```bash
# 1. Clone the repository
git clone <repository-url>
cd ai-robot-4wd

# 2. Create and activate a Python virtual environment
# On Windows:
python -m venv myvenv
myvenv\Scripts\activate

# On Linux/macOS:
python3 -m venv myvenv
source myvenv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure the robot (see Configuration section below)
#    - Rename `config.example.json` to `config.json`
#    - Add your OpenAI API key and set the correct platform.

# 5. Run the main application
python main.py
```

Once the robot is running, you can interact with it via voice or the web interface.

## 🌐 Web Interface

After starting the robot, you can access the web control dashboard in your browser.

- **URL**: `http://<your-robot-ip-address>:5000`
- If running on your local machine, use `http://localhost:5000` or `http://127.0.0.1:5000`.

**The dashboard provides:**
- **Movement Controls**: Buttons to move the robot forward, backward, left, and right, with a stop button.
- **Text Communication**: A chat interface to send text commands or messages to the robot and see its response.
- **Real-time Status**: Live updates on the robot's facial expression, sensor readings, and conversation history.

## 👨‍💻 Project Structure

The project has been refactored to place all core application logic and web files within the `src/` directory for better organization.

```
ai-robot-4wd/
├── src/                    # All core Python modules and web files
│   ├── static/             # Static web assets
│   │   ├── css/            # Stylesheets for the web interface
│   │   ├── js/             # JavaScript for the web interface
│   │   └── images/         # Images used in the web interface
│   ├── ai_processor.py     # Manages AI persona and client switching
│   ├── command_processor.py# Handles voice and text command logic
│   ├── local_llm.py       # Local GGUF model client
│   ├── motor_controller.py # Controls the robot's movement
│   ├── openai_client.py   # OpenAI API client
│   ├── web_server.py      # Flask web server for the control dashboard
│   ├── index.html          # Main informational webpage
│   └── control.html        # Robot control dashboard page
│
├── Faces/                 # Images for the robot's facial expressions
├── logs/                  # All activity and conversation logs
├── models/                # AI models (Vosk and GGUF)
├── main.py                # Main application entry point
├── config.json            # Your local configuration
└── requirements.txt       # Python dependencies
```

## 🤖 AI Persona

To ensure a consistent and immersive user experience, the AI is given a specific persona via a system prompt at the start of every conversation. This prevents it from acting like a generic AI assistant.

**Core Directives of the Persona:**
- **Identity**: It is SARAR, a physical, 4-wheeled robot. It is not a virtual assistant or a language model.
- **Perspective**: Its knowledge is based on its sensors and internal logs. It exists to perform movement tasks and report its status.
- **Behavior**: It is concise, task-oriented, and never breaks character. It will state when it does not understand a command rather than guessing.

This makes interaction feel more like communicating with a real robot.

## 📦 Installation

Follow the [Quick Start](#-quick-start) instructions for basic setup. For a complete setup, you will also need to download the required AI models.

### AI Models

1.  **Create a `models` directory** in the project root.
2.  **Vosk (Speech-to-Text)**: Download a model from the [Vosk website](https://alphacephei.com/vosk/models) (e.g., `vosk-model-small-en-us-0.15`) and extract it into the `models/` directory.
3.  **Local LLM (Fallback AI)**: Download a GGUF-format model (e.g., from Hugging Face) and place it in the `models/` directory.

Update `config.json` with the correct paths to these models.

## ⚙️ Configuration

The robot is configured using `config.json`. Create this file by copying `config.example.json`.

- **`ai`**: Set your `openai_api_key` and the path to your local fallback model.
- **`audio`**: Set the path to your downloaded Vosk model.
- **`hardware`**: Set the `platform` to `windows` for simulation or `raspberry_pi` for deployment. For Raspberry Pi, verify the GPIO `motor_pins` and `sensor_pins` match your wiring.

## 🎯 Usage

1.  **Activate the virtual environment**:
    ```bash
    # Windows
    myvenv\Scripts\activate
    # Linux/macOS
    source myvenv/bin/activate
    ```
2.  **Start the robot**:
    ```bash
    python main.py
    ```
3.  **Interact**:
    - **Voice**: Speak commands clearly to the microphone.
    - **Web**: Open `http://<robot-ip>:5000` in a browser.

### Voice Commands

- **Movement**: "Go forward", "Turn left", "Stop".
- **Conversation**: "Hello", "What can you do?"
- **System**: "Show me your status", "What do you see?"

## 🔧 Hardware Setup (Raspberry Pi)

- **Motor Controller**: Connect your motor driver to the GPIO pins defined in `config.json`.
- **Ultrasonic Sensors**: Connect the trigger and echo pins for the front, left, and right sensors.
- **Audio**: Connect a USB microphone and a speaker via the 3.5mm jack or USB.
- **Display**: Connect a monitor via HDMI to see the robot's facial expressions.

## 🔍 Troubleshooting

- **No AI Response**: Verify your `openai_api_key` in `config.json` is correct. Check that the local model path is also correct.
- **No Voice Recognition**: Ensure your microphone is working and that the `vosk_model_path` in `config.json` is correct.
- **Web Interface Not Loading**: Make sure you are on the same network as the robot and are using the correct IP address and port (`:5000`).

---

**Happy Robotics!**
