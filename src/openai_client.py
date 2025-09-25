import openai
from .error_handler import AIError
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from .logging_system import LoggingSystem

class OpenAIClient:
    def __init__(self, api_key: str, base_url: str, model_name: str, logger: 'LoggingSystem'):
        self.logger = logger
        if not api_key or api_key == "your-openai-api-key-here":
            self.logger.log_activity("OPENAI_CLIENT", "No API key provided. Assuming local server doesn't need one.")
        
        self.logger.log_activity("OPENAI_CLIENT", f"Initializing OpenAI client with base_url: {base_url}")
        self.client = openai.OpenAI(api_key=api_key, base_url=base_url)
        self.model_name = model_name

    def get_available_models(self) -> List[str]:
        """Fetches the list of available model IDs from the API."""
        try:
            self.logger.log_activity("OPENAI_CLIENT", "Fetching available models...")
            models = self.client.models.list()
            model_ids = [model.id for model in models.data]
            self.logger.log_activity("OPENAI_CLIENT", f"Found models: {model_ids}")
            return model_ids
        except openai.APIError as e:
            self.logger.log_activity("OPENAI_CLIENT_ERROR", f"Failed to fetch models: {e}")
            raise AIError(f"Failed to fetch models: {e}")

    def send_message(self, message: str, context: list = None) -> str:
        """
        Sends a message to the OpenAI API and gets a response.
        """
        if context is None:
            context = []

        messages = context + [{"role": "user", "content": message}]
        
        try:
            self.logger.log_activity("OPENAI_CLIENT", f"Sending message to model: {self.model_name}")
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
            )
            self.logger.log_activity("OPENAI_CLIENT", f"Received response: {response}")
            if response.choices:
                return response.choices[0].message.content
            else:
                raise AIError("No response choices received from the API.")
        except openai.APIError as e:
            self.logger.log_activity("OPENAI_CLIENT_ERROR", f"OpenAI API error: {e}")
            raise AIError(f"OpenAI API error: {e}")

    def is_available(self) -> bool:
        """
        Checks if the OpenAI API is available.
        """
        try:
            self.logger.log_activity("OPENAI_CLIENT", "Checking API availability...")
            self.client.models.list()
            self.logger.log_activity("OPENAI_CLIENT", "API is available.")
            return True
        except openai.APIError as e:
            self.logger.log_activity("OPENAI_CLIENT_ERROR", f"API availability check failed: {e}")
            return False
