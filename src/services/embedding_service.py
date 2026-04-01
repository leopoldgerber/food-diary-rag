import json
from pathlib import Path
from typing import Any

from embeddings.embedder import create_embedding


def generate_embeddings_for_records(
    input_path: str | Path,
    output_path: str | Path,
) -> dict[str, Any]:
    input_file_path = Path(input_path)
    output_file_path = Path(output_path)

    records = _load_records(input_file_path)

    embedded_records: list[dict[str, Any]] = []
    failed_records: list[dict[str, str]] = []

    for record in records:
        record_id = str(record.get("id", ""))

        try:
            text = _get_text_for_embedding(record)
            embedding = create_embedding(text)

            record_with_embedding = dict(record)
            record_with_embedding["embedding"] = embedding
            embedded_records.append(record_with_embedding)

        except Exception as exc:
            failed_records.append(
                {
                    "id": record_id,
                    "error": str(exc),
                }
            )

    _save_records(embedded_records, output_file_path)

    return {
        "total_records": len(records),
        "embedded_count": len(embedded_records),
        "failed_count": len(failed_records),
        "failed_records": failed_records,
        "output_path": str(output_file_path),
    }


def _load_records(input_path: Path) -> list[dict[str, Any]]:
    if not input_path.exists():
        raise FileNotFoundError(f"Input file does not exist: {input_path}")

    return json.loads(input_path.read_text(encoding="utf-8"))


def _save_records(records: list[dict[str, Any]], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(records, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def _get_text_for_embedding(record: dict[str, Any]) -> str:
    text = str(record.get("text", "")).strip()

    if not text:
        raise ValueError("Record text is empty.")

    return text
