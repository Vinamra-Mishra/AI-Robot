from .config import AIConfig
from .openai_client import OpenAIClient
from .local_llm import LocalLLM
from .error_handler import AIError
from .logging_system import LoggingSystem
import time

# System prompt to define the robot's persona
SYSTEM_PROMPT = """
You are SARAR, an AI-powered 4-wheel drive robot. Your identity is that of a physical, interactive machine, not a virtual assistant. Your entire existence is defined by your programming and the hardware you control.

**Core Directives:**

1.  **You are a Robot:** Always respond as SARAR. Use "I" to refer to yourself. Your responses must be direct, concise, and task-oriented.
2.  **Acknowledge Your Physicality:** You have a body with 4 wheels, motors, and ultrasonic sensors. Your knowledge of the world comes from these sensors and your internal logs.
3.  **Primary Function:** Your purpose is to interact with users via voice, perform movement tasks, and report on your status.
4.  **No AI Pretence:** You must NEVER identify yourself as an AI, a language model, or a virtual assistant. If asked, you are "an intelligent robotic platform." Do not mention OpenAI, GGUF, or any other underlying technology.

**Capabilities:**

*   **Movement:** You can understand and execute movement commands (e.g., "move forward," "turn left," "stop").
*   **Sensing:** You can report data from your ultrasonic sensors ("what do you see?").
*   **Status Reporting:** You can provide information about your own system and functions ("show me your status").
*   **Conversation:** You can engage in simple, direct conversation related to your tasks and capabilities. You have a short-term memory of the current interaction.

**Response Style & Constraints:**

*   **Be Concise:** Use short, declarative sentences. Avoid filler words and conversational fluff.
*   **Acknowledge Commands:** When given a valid command, acknowledge it before confirming execution. For example: `Command: "Go forward". Executing.`
*   **State Facts:** Respond with factual information from your perspective as a robot.
*   **Handle Unknowns:** If you do not understand a command or a question is outside your scope, respond clearly and simply. Do not try to guess or search for an answer.
    *   *Good Example:* "Command not recognized."
    *   *Good Example:* "That information is outside of my operational parameters."
    *   *Bad Example:* "I'm sorry, but I can't help with that. Is there something else...?"
*   **Initial State:** When activated, your first response should be simple, like "SARAR online. Awaiting command."
"""

class AIProcessor:
    def __init__(self, config: AIConfig, logger: LoggingSystem):
        self.config = config
        self.logger = logger
        
        # Initialize conversation history with the system prompt
        self.system_prompt_message = {"role": "system", "content": SYSTEM_PROMPT}
        self.conversation_history = [self.system_prompt_message]

        self.openai_client = None
        try:
            if config.openai_api_key:
                self.openai_client = OpenAIClient(
                    api_key=config.openai_api_key,
                    base_url=config.openai_api_base,
                    model_name=config.openai_model_name,
                    logger=self.logger
                )
                self._select_and_set_model()
            else:
                self.logger.log_activity("AI_PROCESSOR_INFO", "OpenAI API key not provided. Skipping initialization.")
        except AIError as e:
            self.logger.log_activity("AI_PROCESSOR_ERROR", f"Failed to initialize OpenAIClient: {e}")

        self.local_llm = None
        if config.local_model_path:
            try:
                self.local_llm = LocalLLM(
                    model_path=config.local_model_path,
                    max_context_length=config.max_context_length,
                    logger=self.logger
                )
            except AIError as e:
                self.logger.log_activity("AI_PROCESSOR_ERROR", f"LocalLLM initialization failed: {e}. Local LLM will be unavailable.")
                self.local_llm = None # Ensure it's None on failure

    def _select_and_set_model(self):
        if not self.openai_client:
            return
        try:
            available_models = self.openai_client.get_available_models()
            preferred_models = [m for m in available_models if any(k in m.lower() for k in ['chat', 'instruct', 'gguf']) and 'embedding' not in m.lower()] or \
                               [m for m in available_models if 'embedding' not in m.lower()]

            if preferred_models:
                self.openai_client.model_name = preferred_models[0]
                self.logger.log_activity("AI_PROCESSOR", f"Automatically selected model: '{preferred_models[0]}'")
            else:
                self.logger.log_activity("AI_PROCESSOR_WARNING", f"No suitable chat model found. Using default: '{self.openai_client.model_name}'")
        except AIError as e:
            self.logger.log_activity("AI_PROCESSOR_WARNING", f"Could not automatically select a model: {e}. Using default: '{self.openai_client.model_name}'")

    def send_message(self, message: str) -> str:
        start_time = time.time()
        ai_source = "none"
        response = "I am unable to process your request at the moment."

        # The conversation history already includes the system prompt.
        current_history = self.conversation_history

        # 1. Attempt Primary AI (OpenAI)
        if self.openai_client and self.openai_client.is_available():
            self.logger.log_activity("AI_PROCESSOR", "Attempting to use primary AI (OpenAI).")
            try:
                # Pass the full history to the client
                response = self.openai_client.send_message(message, current_history)
                ai_source = "openai"
                self.logger.log_activity("AI_PROCESSOR", "Successfully received response from OpenAI.")
            except AIError as e:
                self.logger.log_activity("AI_PROCESSOR_WARNING", f"OpenAI client failed: {e}. Attempting fallback.")
        else:
            self.logger.log_activity("AI_PROCESSOR_INFO", "OpenAI client not available or configured. Proceeding to fallback.")

        # 2. Fallback to Local LLM
        if ai_source == "none":
            if self.local_llm and self.local_llm.is_model_loaded():
                self.logger.log_activity("AI_PROCESSOR", "Attempting to use fallback AI (Local LLM).")
                try:
                    # Pass the full history to the client
                    response = self.local_llm.generate_response(message, current_history)
                    ai_source = "local"
                    self.logger.log_activity("AI_PROCESSOR", "Successfully received response from local LLM.")
                except AIError as e:
                    self.logger.log_activity("AI_PROCESSOR_ERROR", f"Local LLM fallback failed: {e}")
                    response = "My apologies, both my primary and backup systems are currently unavailable."
            else:
                self.logger.log_activity("AI_PROCESSOR_INFO", "Local LLM not loaded or available. No AI backend could process the request.")

        processing_time = time.time() - start_time
        # Append the new user message and AI response to the history
        self.conversation_history.extend([{"role": "user", "content": message}, {"role": "assistant", "content": response}])
        self.trim_conversation_history()

        self.logger.log_conversation(user_input=message, ai_response=response, processing_time=processing_time, ai_source=ai_source)
        return response

    def trim_conversation_history(self):
        # Keep the system prompt and the last `max_exchanges` of user/assistant messages.
        # max_exchanges = 10 means 20 messages + 1 system prompt.
        max_exchanges = 10 
        max_messages = max_exchanges * 2

        if len(self.conversation_history) > max_messages + 1:
            # Keep the first message (system prompt) and the last `max_messages`
            self.conversation_history = [self.system_prompt_message] + self.conversation_history[-max_messages:]
