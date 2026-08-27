import os

def obter_juiz():
    provider = os.getenv("JUIZ_PROVIDER", "ollama").lower()

    if provider == "gemini":
        from deepeval.models import GeminiModel  # requer: pip install google-genai

        return GeminiModel(
            model=os.getenv("JUIZ_MODEL", "gemini-3.6-flash"),
            api_key="AQ.Ab8RN6LZdOLMk6tpNAWgqOVUjQMKQXrGRMYtmshl6ohzCmr9Zw"
        )

    from deepeval.models import OllamaModel  # requer: pip install ollama

    return OllamaModel(
        model=os.getenv("JUIZ_MODEL", "llama3.1:latest"),
        base_url=os.getenv("OLLAMA_URL", "http://localhost:11434"),
    )