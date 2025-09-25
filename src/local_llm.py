from llama_cpp import Llama
from .error_handler import AIError
from .logging_system import LoggingSystem
import os

class LocalLLM:
    def __init__(self, model_path: str, max_context_length: int, logger: LoggingSystem):
        self.model_path = model_path
        self.logger = logger
        self.model = None

        if not os.path.exists(self.model_path):
            self.logger.log_activity("LOCAL_LLM_WARNING", f"Local LLM model not found at {self.model_path}")
            raise AIError(f"Local model file not found: {self.model_path}")

        try:
            self.model = Llama(model_path=self.model_path, n_ctx=max_context_length, verbose=False)
            self.logger.log_activity("LOCAL_LLM", f"Successfully loaded local model from {self.model_path}")
        except Exception as e:
            self.model = None # Ensure model is None on failure
            self.logger.log_activity("LOCAL_LLM_ERROR", f"Failed to load local LLM model: {e}")
            raise AIError(f"Failed to load local model: {e}")

    def generate_response(self, prompt: str, context: list = None) -> str:
        """
        Generates a response from the local LLM, trying chat completion first.
        """
        if not self.is_model_loaded():
            raise AIError("Local LLM model is not loaded.")

        messages = (context or []) + [{"role": "user", "content": prompt}]

        try:
            # First, attempt to use the chat completion endpoint
            self.logger.log_activity("LOCAL_LLM", "Attempting chat completion with local model.")
            output = self.model.create_chat_completion(
                messages=messages,
                max_tokens=150,
            )
            if output and output.get('choices') and output['choices'][0].get('message'):
                response = output['choices'][0]['message']['content'].strip()
                self.logger.log_activity("LOCAL_LLM", "Chat completion successful.")
                return response
            else:
                self.logger.log_activity("LOCAL_LLM_WARNING", "Chat completion returned empty or invalid response.")
                raise AIError("Empty response from chat completion.")

        except Exception as e:
            self.logger.log_activity("LOCAL_LLM_WARNING", f"Chat completion failed: {e}. Falling back to simple generation.")
            # If chat completion fails, fall back to simple text generation
            try:
                full_prompt = "\n".join([f"{msg['role']}: {msg['content']}" for msg in messages])
                output = self.model(full_prompt, max_tokens=150, echo=False)
                
                if output and output.get('choices') and output['choices'][0].get('text'):
                    response = output['choices'][0]['text'].strip()
                    self.logger.log_activity("LOCAL_LLM", "Simple generation successful.")
                    return response
                else:
                    self.logger.log_activity("LOCAL_LLM_ERROR", "Simple generation also failed to produce a valid response.")
                    raise AIError("Simple generation failed.")
            except Exception as inner_e:
                self.logger.log_activity("LOCAL_LLM_ERROR", f"Error during simple generation: {inner_e}")
                raise AIError(f"Local LLM generation failed: {inner_e}")

    def is_model_loaded(self) -> bool:
        """
        Checks if the local LLM model is loaded and ready.
        """
        return self.model is not None
