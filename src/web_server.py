
from flask import Flask, jsonify, request, send_from_directory
import os

class WebServer:
    def __init__(self, robot_controller):
        # The root for our web content is the 'src' directory, where this script lives.
        self.web_content_dir = os.path.dirname(os.path.abspath(__file__))

        # The static folder is a sub-directory of our web content dir.
        static_folder = os.path.join(self.web_content_dir, 'static')

        # We no longer use a template folder, files are served directly.
        self.app = Flask(__name__, static_folder=static_folder)
        self.robot_controller = robot_controller
        self.configure_routes()

    def configure_routes(self):
        # Serve the main index.html
        @self.app.route('/')
        def index():
            return send_from_directory(self.web_content_dir, 'index.html')

        # Serve any other .html file by name (e.g., /control.html)
        @self.app.route('/<path:filename>.html')
        def serve_html(filename):
            return send_from_directory(self.web_content_dir, f"{filename}.html")

        @self.app.route('/move/<direction>', methods=['POST'])
        def move(direction):
            if not self.robot_controller.motor_controller:
                return jsonify({"status": "error", "message": "Motor controller not initialized"}), 500

            duration = 0.5  # seconds
            if direction == 'forward':
                self.robot_controller.motor_controller.move_forward(duration)
            elif direction == 'backward':
                self.robot_controller.motor_controller.move_backward(duration)
            elif direction == 'left':
                self.robot_controller.motor_controller.turn_left()
            elif direction == 'right':
                self.robot_controller.motor_controller.turn_right()
            elif direction == 'stop':
                self.robot_controller.motor_controller.stop()
            else:
                return jsonify({"status": "error", "message": "Invalid direction"}), 400
            
            return jsonify({"status": "success", "message": f"Moved {direction}"})

        @self.app.route('/api/send_text', methods=['POST'])
        def send_text():
            data = request.get_json()
            if not data or 'text' not in data:
                return jsonify({"status": "error", "message": "No text provided"}), 400

            text_input = data['text']
            
            if not self.robot_controller.command_processor:
                return jsonify({"status": "error", "message": "Command processor not initialized"}), 500

            response_text = self.robot_controller.command_processor.process_text_input(text_input)
            
            return jsonify({"status": "success", "response": response_text})

    def run(self, host='0.0.0.0', port=5000):
        self.app.run(host=host, port=port, debug=False)
