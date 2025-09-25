import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from flask import Flask, request, jsonify
from flask_cors import CORS
from main import RobotController
import threading

# Create the Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Initialize robot components
print("Initializing robot components...")
try:
    # Initialize the robot controller
    controller = RobotController()
    if not controller.initialize_components():
        print("Failed to initialize robot components. Exiting.")
        sys.exit(1)
    print("Robot components initialized successfully.")
except Exception as e:
    print(f"Error initializing robot components: {str(e)}")
    sys.exit(1)

# --- API Endpoints ---

@app.route('/move', methods=['POST'])
def move():
    data = request.get_json()
    direction = data.get('direction')
    if not direction:
        return jsonify({'error': 'Missing direction'}), 400

    if direction == 'forward':
        controller.motor_controller.move_forward()
    elif direction == 'backward':
        controller.motor_controller.move_backward()
    elif direction == 'left':
        controller.motor_controller.turn_left()
    elif direction == 'right':
        controller.motor_controller.turn_right()
    elif direction == 'stop':
        controller.motor_controller.stop()
    else:
        return jsonify({'error': 'Invalid direction'}), 400

    return jsonify({'status': f'moving {direction}'})

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    message = data.get('message')
    if not message:
        return jsonify({'error': 'Missing message'}), 400

    # Let the AI process the message
    controller.face_display.set_face("thinking")
    ai_reply = controller.ai_processor.process(message)
    
    # Let the robot speak the reply
    controller.tts.speak(ai_reply)
    controller.face_display.set_face("neutral")

    return jsonify({'reply': ai_reply, 'face': controller.face_display.get_current_face()})

@app.route('/face', methods=['GET'])
def get_face():
    return jsonify({'face': controller.face_display.get_current_face()})

# --- Main ---

def run_api_server():
    try:
        print("Starting Flask API server on http://localhost:5000")
        app.run(host='0.0.0.0', port=5000, debug=True)
    except Exception as e:
        print(f"Error starting API server: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    run_api_server()
