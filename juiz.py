import os

def obter_juiz():
    provider = os.getenv("JUIZ_PROVIDER", "ollama").lower()

    if provider == "gemini":
        from deepeval.models import GeminiModel  # requer: pip install google-genai

        return GeminiModel(
            model=os.getenv("JUIZ_MODEL", "gemini-2.0-flash"),
            api_key=os.getenv("GEMINI_API_KEY"),
        )

    from deepeval.models import OllamaModel  # requer: pip install ollama

    return OllamaModel(
        model=os.getenv("JUIZ_MODEL", "llama3.2:3b"),
        base_url=os.getenv("OLLAMA_URL", "http://localhost:11434"),
    )