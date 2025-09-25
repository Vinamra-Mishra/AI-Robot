import pygame
import os
import time
import threading
import queue
from typing import Tuple, Dict, TYPE_CHECKING

if TYPE_CHECKING:
    from .logging_system import LoggingSystem

class FaceDisplay(threading.Thread):
    def __init__(self, screen_size: Tuple[int, int], faces_directory: str, logger: 'LoggingSystem'):
        super().__init__(daemon=True)
        self.name = "FaceDisplayThread"
        self.screen_size = screen_size
        self.faces_directory = faces_directory
        self.logger = logger
        
        self.faces: Dict[str, pygame.Surface] = {}
        self.screen = None
        self.initialized = False
        self.running = False
        self.command_queue = queue.Queue()
        self.current_face = "neutral"  # Instance variable for current face

    def _initialize_display(self):
        """Initializes the pygame display and loads face images."""
        try:
            pygame.init()
            pygame.display.init()
            self.screen = pygame.display.set_mode(self.screen_size)
            pygame.display.set_caption("Robot Face")
            self.logger.log_activity("DISPLAY", "Pygame display initialized.")
            self._load_faces()
            self.initialized = True
        except Exception as e:
            self.logger.log_activity("DISPLAY_ERROR", f"Failed to initialize Pygame display: {e}")
            self.initialized = False

    def _load_faces(self):
        """Loads all face images from the specified directory."""
        try:
            for filename in os.listdir(self.faces_directory):
                if filename.endswith(".png"):
                    name = os.path.splitext(filename)[0]
                    path = os.path.join(self.faces_directory, filename)
                    try:
                        image = pygame.image.load(path).convert_alpha()
                        self.faces[name] = pygame.transform.scale(image, self.screen_size)
                    except pygame.error as e:
                        self.logger.log_activity("DISPLAY_ERROR", f"Failed to load image '{path}': {e}")
            if not self.faces:
                self.logger.log_activity("DISPLAY_WARNING", "No face images were loaded.")
            else:
                self.logger.log_activity("DISPLAY", f"Loaded face images: {list(self.faces.keys())}")
        except Exception as e:
            self.logger.log_activity("DISPLAY_ERROR", f"Failed to read faces directory: {e}")

    def run(self):
        """The main loop of the display thread."""
        self._initialize_display()
        if not self.initialized:
            return

        self.running = True

        while self.running:
            try:
                # Check for commands without blocking
                try:
                    new_face = self.command_queue.get_nowait()
                    if new_face in self.faces:
                        self.current_face = new_face
                    elif new_face == "_shutdown":
                        self.running = False
                        continue
                except queue.Empty:
                    pass

                # Draw the current face
                if self.current_face in self.faces:
                    self.screen.blit(self.faces[self.current_face], (0, 0))
                    pygame.display.flip()
                
                # Handle pygame events
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.running = False

                time.sleep(0.05) # Reduce CPU usage

            except Exception as e:
                self.logger.log_activity("DISPLAY_ERROR", f"Error in display loop: {e}")
                self.running = False
        
        self._cleanup()

    def _cleanup(self):
        """Shuts down the pygame display."""
        self.logger.log_activity("DISPLAY", "Pygame display shutting down.")
        pygame.quit()

    def set_face(self, face_name: str):
        """Thread-safe method to change the displayed face."""
        if self.is_alive():
            self.command_queue.put(face_name)

    def get_current_face(self) -> str:
        """Thread-safe method to get the current face name."""
        return self.current_face

    def stop(self):
        """Stops the display thread."""
        if self.is_alive():
            self.command_queue.put("_shutdown")
            self.join(timeout=2) # Wait for the thread to finish
            if self.is_alive():
                self.logger.log_activity("DISPLAY_WARNING", "Display thread did not shut down gracefully.")