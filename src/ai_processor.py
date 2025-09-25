from .config import AIConfig
from .openai_client import OpenAIClient
from .local_llm import LocalLLM
from .error_handler import AIError
from .logging_system import LoggingSystem
import time

class AIProcessor:
    def __init__(self, config: AIConfig, logger: LoggingSystem):
        self.config = config
        self.logger = logger
        self.conversation_history = []

        self.openai_client = None
        try:
            self.openai_client = OpenAIClient(
                api_key=config.openai_api_key,
                base_url=config.openai_api_base,
                model_name=config.openai_model_name, # Default model
                logger=self.logger
            )
            self._select_and_set_model()
        except AIError as e:
            self.logger.log_activity("AI_PROCESSOR_ERROR", f"Failed to initialize OpenAIClient: {e}")

        self.local_llm = None
        if config.local_model_path:
            self.local_llm = LocalLLM(
                model_path=config.local_model_path,
                max_context_length=config.max_context_length
            )

    def _select_and_set_model(self):
        """Automatically selects and configures the best available chat model."""
        if not self.openai_client:
            return

        try:
            available_models = self.openai_client.get_available_models()
            
            # --- Model Selection Logic ---
            preferred_models = []
            # 1. Look for chat/instruct models first
            for model in available_models:
                if any(kw in model.lower() for kw in ['chat', 'instruct', 'gguf']):
                    if 'embedding' not in model.lower():
                        preferred_models.append(model)
            
            # 2. If none found, take any non-embedding model
            if not preferred_models:
                for model in available_models:
                    if 'embedding' not in model.lower():
                        preferred_models.append(model)

            if preferred_models:
                # Pick the first preferred model found
                chosen_model = preferred_models[0]
                self.openai_client.model_name = chosen_model
                self.logger.log_activity("AI_PROCESSOR", f"Automatically selected model: '{chosen_model}'")
            else:
                # Fallback to the default model from config
                self.logger.log_activity("AI_PROCESSOR_WARNING", f"No suitable chat model found. Using default: '{self.openai_client.model_name}'")

        except AIError as e:
            self.logger.log_activity("AI_PROCESSOR_WARNING", f"Could not automatically select a model: {e}. Using default: '{self.openai_client.model_name}'")

    def send_message(self, message: str) -> str:
        """
        Processes a message using the primary AI service with a fallback to the local one.
        """
        start_time = time.time()
        ai_source = "none"
        response = "I am unable to process your request at the moment."

        try:
            # Primary: OpenAI Compatible API
            if self.openai_client and self.openai_client.is_available():
                try:
                    response = self.openai_client.send_message(message, self.conversation_history)
                    ai_source = "openai"
                    self.logger.log_activity("AI_PROCESSOR", "Successfully used OpenAI client.")
                except AIError as e:
                    self.logger.log_activity("AI_PROCESSOR_ERROR", f"OpenAI client failed: {e}. Falling back to local LLM.")
                    raise e # Re-raise to trigger fallback
            else:
                raise AIError("OpenAI client not available or not configured.")

        except AIError:
            # Fallback: Local LLM
            if self.local_llm and self.local_llm.is_model_loaded():
                try:
                    response = self.local_llm.generate_response(message, self.conversation_history)
                    ai_source = "local"
                    self.logger.log_activity("AI_PROCESSOR", "Successfully used local LLM.")
                except AIError as e:
                    self.logger.log_activity("AI_PROCESSOR_ERROR", f"Local LLM failed: {e}. No AI services available.")
            else:
                self.logger.log_activity("AI_PROCESSOR_ERROR", "No AI services available.")

        processing_time = time.time() - start_time
        
        # Update conversation history
        self.conversation_history.append({"role": "user", "content": message})
        self.conversation_history.append({"role": "assistant", "content": response})
        
        # Trim history
        self.trim_conversation_history()

        self.logger.log_conversation(
            user_input=message,
            ai_response=response,
            processing_time=processing_time,
            ai_source=ai_source
        )
        
        return response

    def trim_conversation_history(self):
        """
        Keeps the conversation history within a reasonable limit.
        """
        max_messages = 20 
        if len(self.conversation_history) > max_messages:
            self.conversation_history = self.conversation_history[-max_messages:]
