"""
Provider-agnostic LLM wrapper supporting Ollama and Google Gemini.
Module 20: LLM Provider Integration
"""

import os
import json
from typing import Optional, Generator
from abc import ABC, abstractmethod
from dotenv import load_dotenv
import google.generativeai as genai
import httpx

load_dotenv()


class LLMProvider(ABC):
    """Base class for LLM providers."""

    @abstractmethod
    def generate(self, prompt: str, **kwargs) -> str:
        """Generate text response."""
        pass

    @abstractmethod
    def stream(self, prompt: str, **kwargs) -> Generator[str, None, None]:
        """Stream text response."""
        pass


class OllamaProvider(LLMProvider):
    """Ollama provider for local LLM inference."""

    def __init__(self, model: str = "mistral", base_url: str = "http://localhost:11434"):
        self.model = model
        self.base_url = base_url
        self.client = httpx.Client(timeout=300.0)

    def generate(self, prompt: str, temperature: float = 0.7, max_tokens: int = 2048) -> str:
        """Generate text using Ollama."""
        try:
            response = self.client.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "temperature": temperature,
                    "num_predict": max_tokens,
                },
            )
            response.raise_for_status()
            return response.json()["response"]
        except Exception as e:
            raise RuntimeError(f"Ollama generation failed: {str(e)}")

    def stream(self, prompt: str, temperature: float = 0.7, max_tokens: int = 2048) -> Generator[str, None, None]:
        """Stream text using Ollama."""
        try:
            with self.client.stream(
                "POST",
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": True,
                    "temperature": temperature,
                    "num_predict": max_tokens,
                },
            ) as response:
                response.raise_for_status()
                for line in response.iter_lines():
                    if line:
                        chunk = json.loads(line)
                        if "response" in chunk:
                            yield chunk["response"]
        except Exception as e:
            raise RuntimeError(f"Ollama streaming failed: {str(e)}")


class GeminiProvider(LLMProvider):
    """Google Gemini provider for cloud-based inference."""

    def __init__(self, api_key: Optional[str] = None, model: str = "gemini-2.5-flash"):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found in environment")
        self.model = model
        genai.configure(api_key=self.api_key)
        self.client = genai.GenerativeModel(self.model)

    def generate(self, prompt: str, temperature: float = 0.7, max_tokens: int = 2048) -> str:
        """Generate text using Gemini."""
        try:
            response = self.client.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=temperature,
                    max_output_tokens=max_tokens,
                ),
                safety_settings=[
                    {"category": genai.types.HarmCategory.HARM_CATEGORY_UNSPECIFIED, "threshold": genai.types.HarmBlockThreshold.BLOCK_NONE},
                ],
            )
            return response.text
        except Exception as e:
            raise RuntimeError(f"Gemini generation failed: {str(e)}")

    def stream(self, prompt: str, temperature: float = 0.7, max_tokens: int = 2048) -> Generator[str, None, None]:
        """Stream text using Gemini."""
        try:
            response = self.client.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=temperature,
                    max_output_tokens=max_tokens,
                ),
                safety_settings=[
                    {"category": genai.types.HarmCategory.HARM_CATEGORY_UNSPECIFIED, "threshold": genai.types.HarmBlockThreshold.BLOCK_NONE},
                ],
                stream=True,
            )
            for chunk in response:
                if chunk.text:
                    yield chunk.text
        except Exception as e:
            raise RuntimeError(f"Gemini streaming failed: {str(e)}")


def get_llm_provider(provider: Optional[str] = None, **kwargs) -> LLMProvider:
    """
    Factory function to get the appropriate LLM provider.

    Args:
        provider: "ollama" or "gemini". If None, uses LLM_PROVIDER env var (default: "ollama")
        **kwargs: Additional config passed to provider

    Returns:
        LLMProvider instance
    """
    provider = provider or os.getenv("LLM_PROVIDER", "ollama").lower()

    if provider == "ollama":
        return OllamaProvider(
            model=kwargs.get("model") or os.getenv("OLLAMA_MODEL", "mistral"),
            base_url=kwargs.get("base_url") or os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
        )
    elif provider == "gemini":
        return GeminiProvider(
            api_key=kwargs.get("api_key") or os.getenv("GEMINI_API_KEY"),
            model=kwargs.get("model") or os.getenv("GEMINI_MODEL", "gemini-2.5-flash"),
        )
    else:
        raise ValueError(f"Unknown provider: {provider}")


# Convenience exports
__all__ = [
    "LLMProvider",
    "OllamaProvider",
    "GeminiProvider",
    "get_llm_provider",
]
