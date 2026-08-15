import os
import json
import logging
from typing import Any, Dict, List, Optional

import httpx
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

env_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(env_path)

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

PRIMARY_MODEL = "openai/gpt-oss-20b"
FALLBACK_MODELS = ["cohere/north-mini-code:free"]


class OpenRouterClient:
    """
    Cliente HTTP delgado para llamadas de clasificación vía OpenRouter, con modelo
    principal y de respaldo automático (fallback) y salida forzada a JSON estructurado.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        primary_model: str = PRIMARY_MODEL,
        fallback_models: Optional[List[str]] = None,
        timeout: float = 20.0,
    ):
        self.api_key = api_key or OPENROUTER_API_KEY
        self.primary_model = primary_model
        self.fallback_models = fallback_models if fallback_models is not None else FALLBACK_MODELS
        self.timeout = timeout

    async def classify_json(
        self,
        system_prompt: str,
        user_prompt: str,
        schema_name: str,
        json_schema: Dict[str, Any],
    ) -> Optional[Dict[str, Any]]:
        """Envía un prompt y exige una respuesta validada contra json_schema.
        Retorna None si la llamada falla o la respuesta no es JSON válido."""
        if not self.api_key:
            logger.error("OpenRouterClient: OPENROUTER_API_KEY no está configurada.")
            return None

        payload = {
            "model": self.primary_model,
            "models": self.fallback_models,
            "temperature": 0,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "response_format": {
                "type": "json_schema",
                "json_schema": {
                    "name": schema_name,
                    "strict": True,
                    "schema": json_schema,
                },
            },
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(OPENROUTER_URL, headers=headers, json=payload)
                response.raise_for_status()
                data = response.json()
        except httpx.HTTPError as e:
            logger.error(f"OpenRouterClient: error HTTP llamando a OpenRouter - {e}")
            return None
        except Exception as e:
            logger.error(f"OpenRouterClient: error inesperado llamando a OpenRouter - {e}")
            return None

        try:
            content = data["choices"][0]["message"]["content"]
            return json.loads(content)
        except (KeyError, IndexError, TypeError, json.JSONDecodeError) as e:
            logger.error(f"OpenRouterClient: respuesta inesperada o JSON inválido - {e}")
            return None
