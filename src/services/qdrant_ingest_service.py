import json
from pathlib import Path
from typing import Any

from storage.qdrant_store import (
    DEFAULT_COLLECTION_NAME,
    ensure_collection_exists,
    fetch_all_records,
    get_qdrant_client,
    upsert_records,
)


def load_records_into_qdrant(
    input_path: str | Path,
    collection_name: str = DEFAULT_COLLECTION_NAME,
) -> dict[str, Any]:
    input_file_path = Path(input_path)
    records = _load_records(input_file_path)

    if not records:
        raise ValueError("No records found for Qdrant upload.")

    vector_size = _get_vector_size(records)

    client = get_qdrant_client()
    ensure_collection_exists(
        client=client,
        collection_name=collection_name,
        vector_size=vector_size,
    )

    upsert_records(
        client=client,
        collection_name=collection_name,
        records=records,
    )

    stored_points = fetch_all_records(
        client=client,
        collection_name=collection_name,
        limit=100,
    )

    print(f"Stored points fetched right after upsert: {len(stored_points)}")
    for point in stored_points[:3]:
        print(point)

    return {
        "collection_name": collection_name,
        "input_records": len(records),
        "stored_points": len(stored_points),
        "vector_size": vector_size,
    }


def _load_records(input_path: Path) -> list[dict[str, Any]]:
    if not input_path.exists():
        raise FileNotFoundError(f"Input file does not exist: {input_path}")

    return json.loads(input_path.read_text(encoding="utf-8"))


def _get_vector_size(records: list[dict[str, Any]]) -> int:
    first_embedding = records[0].get("embedding")

    if not isinstance(first_embedding, list) or not first_embedding:
        raise ValueError("First record does not contain a valid embedding.")

    return len(first_embedding)
