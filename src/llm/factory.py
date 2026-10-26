from langchain_core.language_models.chat_models import BaseChatModel
from langchain_ollama import ChatOllama
from src.core.config import get_setting,LLMSettings

def create_llm(config:LLMSettings|None=None)->BaseChatModel:
    if config is None:
        config = get_setting().llm

    provider = config.provider.lower()

    if provider == 'ollama':
        return ChatOllama(
            model=config.model_name,
            temperature=config.temperature,
        )

    raise ValueError(f"Unsupported LLM provider: {config.provider}")