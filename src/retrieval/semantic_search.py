from typing import Any

from embeddings.embedder import create_embedding
from storage.qdrant_store import DEFAULT_COLLECTION_NAME, get_qdrant_client


class SemanticSearchError(Exception):
    """Base exception for semantic search errors."""


def run_semantic_search(
    raw_query: str,
    collection_name: str = DEFAULT_COLLECTION_NAME,
    limit: int = 3,
) -> list[dict[str, Any]]:
    cleaned_query = raw_query.strip()

    if not cleaned_query:
        raise SemanticSearchError("Query is empty.")

    if limit <= 0:
        raise SemanticSearchError("Limit must be greater than zero.")

    query_embedding = create_embedding(cleaned_query)
    client = get_qdrant_client()

    try:
        search_result = client.query_points(
            collection_name=collection_name,
            query=query_embedding,
            limit=limit,
            with_payload=True,
            with_vectors=False,
        )
    except Exception as exc:
        raise SemanticSearchError(
            f"Failed to run semantic search: {exc}") from exc

    return [_point_to_dict(point) for point in search_result.points]


def _point_to_dict(point: Any) -> dict[str, Any]:
    payload = point.payload or {}

    return {
        "id": payload.get("record_id"),
        "date": payload.get("date"),
        "text": payload.get("text"),
        "calories": payload.get("calories"),
        "protein": payload.get("protein"),
        "fat": payload.get("fat"),
        "carbs": payload.get("carbs"),
        "score": point.score,
    }
