from typing import Any, Dict, List

from src.infrastructure.ai.openrouter_client import OpenRouterClient

RELEVANT_INDICES_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "properties": {
        "relevant_indices": {
            "type": "array",
            "items": {"type": "integer"},
            "description": "Índices (1-based) de los elementos relevantes de la lista recibida.",
        }
    },
    "required": ["relevant_indices"],
    "additionalProperties": False,
}


def format_indexed(items: List[str]) -> str:
    """Formatea items como 'indice|valor' (uno por línea) para minimizar tokens."""
    return "\n".join(f"{i}|{item}" for i, item in enumerate(items, start=1))


async def classify_indexed(
    client: OpenRouterClient,
    items: List[str],
    system_prompt: str,
    schema_name: str,
) -> List[str]:
    """Envía una lista indexada al modelo y retorna el subconjunto marcado como relevante.
    Falla de forma segura (lista vacía) ante cualquier error de red, parseo o índices inválidos."""
    if not items:
        return []

    user_prompt = f"Lista (formato indice|valor, uno por línea):\n{format_indexed(items)}"

    result = await client.classify_json(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        schema_name=schema_name,
        json_schema=RELEVANT_INDICES_SCHEMA,
    )

    if not result:
        return []

    indices = result.get("relevant_indices", [])
    relevant: List[str] = []
    seen = set()
    for idx in indices:
        if isinstance(idx, int) and 1 <= idx <= len(items) and idx not in seen:
            seen.add(idx)
            relevant.append(items[idx - 1])

    return relevant
