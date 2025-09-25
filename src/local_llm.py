from llama_cpp import Llama
from .error_handler import AIError
import os

class LocalLLM:
    def __init__(self, model_path: str, max_context_length: int):
        self.model_path = model_path
        self.model = None
        if os.path.exists(self.model_path):
            try:
                self.model = Llama(model_path=self.model_path, n_ctx=max_context_length)
            except Exception as e:
                # Don't raise an error, just log a warning. The AI processor will handle the fallback.
                print(f"Warning: Failed to load local LLM model: {e}")
        else:
            # Don't raise an error, just log a warning. The AI processor will handle the fallback.
            print(f"Warning: Local LLM model not found at {self.model_path}")


    def generate_response(self, prompt: str, context: list = None) -> str:
        """
        Generates a response from the local LLM.
        """
        if not self.is_model_loaded():
            raise AIError("Local LLM model is not loaded.")

        # Create a chat-like prompt structure
        if context:
            messages = context + [{"role": "user", "content": prompt}]
        else:
            messages = [{"role": "user", "content": prompt}]

        try:
            # Use the chat completion endpoint for GGUF models that support it
            output = self.model.create_chat_completion(
                messages=messages,
                max_tokens=150,
            )
            if output and 'choices' in output and output['choices']:
                return output['choices'][0]['message']['content'].strip()
            else:
                return "I am not sure how to respond to that."
        except Exception as e:
            # Fallback to simple generation if chat completion fails
            try:
                full_prompt = "\n".join([f"{msg['role']}: {msg['content']}" for msg in messages])
                output = self.model(full_prompt, max_tokens=150, echo=False)
                if output and 'choices' in output and output['choices']:
                    return output['choices'][0]['text'].strip()
                else:
                    return "I am not sure how to respond to that."
            except Exception as inner_e:
                raise AIError(f"Error during local LLM generation: {inner_e}")

    def is_model_loaded(self) -> bool:
        """
        Checks if the local LLM model is loaded.
        """
        return self.model is not None
