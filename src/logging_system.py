import json
import os
from datetime import datetime
from typing import List, Dict, Any

class LoggingSystem:
    def __init__(self, log_directory: str, max_log_entries: int = 1000):
        self.log_directory = log_directory
        self.max_log_entries = max_log_entries
        os.makedirs(self.log_directory, exist_ok=True)

        self.conversation_log_path = os.path.join(self.log_directory, "conversation_log.json")
        self.movement_log_path = os.path.join(self.log_directory, "movement_log.json")
        self.stt_log_path = os.path.join(self.log_directory, "stt_log.json")
        self.tts_log_path = os.path.join(self.log_directory, "tts_log.json")
        self.combined_activity_path = os.path.join(self.log_directory, "combined_activity.txt")

    def _write_json_log(self, file_path: str, entry: Dict[str, Any]):
        """Writes a new entry to a JSON log file, handling rotation."""
        log_data = []
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                try:
                    log_data = json.load(f)
                except json.JSONDecodeError:
                    log_data = []
        
        log_data.insert(0, entry)
        
        if len(log_data) > self.max_log_entries:
            log_data = log_data[:self.max_log_entries]
            
        with open(file_path, 'w') as f:
            json.dump(log_data, f, indent=4)

    def _write_text_log(self, message: str):
        """Appends a message to the combined text log."""
        with open(self.combined_activity_path, 'a', encoding='utf-8') as f:
            f.write(f"{datetime.now().isoformat()} - {message}\n")

    def log_conversation(self, user_input: str, ai_response: str, processing_time: float, ai_source: str):
        entry = {
            "timestamp": datetime.now().isoformat(),
            "user_input": user_input,
            "ai_response": ai_response,
            "processing_time": processing_time,
            "ai_source": ai_source
        }
        self._write_json_log(self.conversation_log_path, entry)
        self.log_activity("CONVERSATION", f"User: {user_input}, AI: {ai_response}")

    def log_movement(self, command: str, duration: float, success: bool):
        entry = {
            "timestamp": datetime.now().isoformat(),
            "command": command,
            "duration": duration,
            "success": success
        }
        self._write_json_log(self.movement_log_path, entry)
        self.log_activity("MOVEMENT", f"Command: {command}, Duration: {duration}, Success: {success}")

    def log_stt(self, recognized_text: str, confidence: float):
        entry = {
            "timestamp": datetime.now().isoformat(),
            "recognized_text": recognized_text,
            "confidence": confidence
        }
        self._write_json_log(self.stt_log_path, entry)
        self.log_activity("STT", f"Recognized: '{recognized_text}', Confidence: {confidence:.2f}")

    def log_tts(self, text: str, success: bool):
        entry = {
            "timestamp": datetime.now().isoformat(),
            "text": text,
            "success": success
        }
        self._write_json_log(self.tts_log_path, entry)
        if success:
            self.log_activity("TTS", f"Spoke: '{text}'")
        else:
            self.log_activity("TTS_ERROR", f"Failed to speak: '{text}'")
            
    def log_activity(self, activity_type: str, details: str):
        self._write_text_log(f"[{activity_type}] {details}")

    def _read_json_log(self, file_path: str, limit: int) -> List[Dict[str, Any]]:
        if not os.path.exists(file_path):
            return []
        with open(file_path, 'r') as f:
            try:
                log_data = json.load(f)
                return log_data[:limit]
            except json.JSONDecodeError:
                return []

    def get_conversation_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        return self._read_json_log(self.conversation_log_path, limit)

    def get_movement_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        return self._read_json_log(self.movement_log_path, limit)
