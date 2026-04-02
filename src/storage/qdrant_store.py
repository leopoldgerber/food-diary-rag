import os
from typing import Any

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams
from dotenv import load_dotenv
load_dotenv()


DEFAULT_COLLECTION_NAME = "food_diary_notes"


class QdrantStoreError(Exception):
    """Base exception for Qdrant storage errors."""


class MissingQdrantURLError(QdrantStoreError):
    """Raised when QDRANT_URL is not set."""


def get_qdrant_client() -> QdrantClient:
    qdrant_url = os.getenv("QDRANT_URL")
    qdrant_api_key = os.getenv("QDRANT_API_KEY")

    if not qdrant_url:
        raise MissingQdrantURLError("QDRANT_URL is not set.")

    if qdrant_api_key:
        return QdrantClient(url=qdrant_url, api_key=qdrant_api_key)

    return QdrantClient(url=qdrant_url)


def ensure_collection_exists(
    client: QdrantClient,
    collection_name: str,
    vector_size: int,
) -> None:
    existing_collections = client.get_collections().collections
    existing_names = {collection.name for collection in existing_collections}

    if collection_name in existing_names:
        return

    client.create_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(
            size=vector_size,
            distance=Distance.COSINE,
        ),
    )


def upsert_records(
    client: QdrantClient,
    collection_name: str,
    records: list[dict[str, Any]],
) -> None:
    points = [_record_to_point(record) for record in records]

    client.upsert(
        collection_name=collection_name,
        points=points,
    )


def fetch_all_records(
    client: QdrantClient,
    collection_name: str,
    limit: int = 100,
) -> list[Any]:
    points, _ = client.scroll(
        collection_name=collection_name,
        limit=limit,
        with_payload=True,
        with_vectors=False,
    )
    return points


def _record_to_point(record: dict[str, Any]) -> PointStruct:
    record_id = _convert_record_id_to_qdrant_id(str(record["id"]))
    embedding = record["embedding"]

    payload = {
        "record_id": record["id"],
        "date": record["date"],
        "text": record["text"],
        "calories": record["calories"],
        "protein": record["protein"],
        "fat": record["fat"],
        "carbs": record["carbs"],
    }

    return PointStruct(
        id=record_id,
        vector=embedding,
        payload=payload,
    )


def _convert_record_id_to_qdrant_id(record_id: str) -> int:
    return int(record_id.replace("-", ""))
