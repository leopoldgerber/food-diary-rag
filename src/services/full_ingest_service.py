import json
from pathlib import Path
from typing import Any

from embeddings.embedder import create_embedding
from ingestion.file_loader import load_notes_from_directory
from ingestion.note_parser import (
    InvalidNoteFilenameError,
    MissingNutritionFieldError,
    NoteParserError,
    ParsedNote,
    parse_note,
)
from ingestion.validator import ValidationResult, validate_parsed_note
from storage.qdrant_store import (
    DEFAULT_COLLECTION_NAME,
    ensure_collection_exists,
    get_qdrant_client,
    upsert_records,
)


def run_full_ingestion_to_qdrant(
    notes_dir: str | Path,
    parsed_output_path: str | Path,
    embedded_output_path: str | Path,
    collection_name: str = DEFAULT_COLLECTION_NAME,
) -> dict[str, Any]:
    notes_dir_path = Path(notes_dir)
    parsed_output_file_path = Path(parsed_output_path)
    embedded_output_file_path = Path(embedded_output_path)

    raw_notes = load_notes_from_directory(notes_dir_path)

    parsed_notes: list[ParsedNote] = []
    failed_files: list[dict[str, str]] = []

    for raw_note in raw_notes:
        try:
            parsed_note = parse_note(raw_note)
            validation_result = validate_parsed_note(parsed_note)

            if validation_result.is_valid:
                parsed_notes.append(parsed_note)
            else:
                failed_files.append(
                    {
                        "filename": raw_note.filename,
                        "stage": "validation",
                        "error": _format_validation_errors(validation_result),
                    }
                )

        except (InvalidNoteFilenameError, MissingNutritionFieldError, NoteParserError) as exc:
            failed_files.append(
                {
                    "filename": raw_note.filename,
                    "stage": "parsing",
                    "error": str(exc),
                }
            )

    _save_parsed_notes(parsed_notes, parsed_output_file_path)

    embedded_records: list[dict[str, Any]] = []
    embedding_failed_records: list[dict[str, str]] = []

    for note in parsed_notes:
        try:
            record = _parsed_note_to_dict(note)
            record["embedding"] = create_embedding(note.text)
            embedded_records.append(record)
        except Exception as exc:
            embedding_failed_records.append(
                {
                    "id": note.id,
                    "stage": "embedding",
                    "error": str(exc),
                }
            )

    _save_embedded_records(embedded_records, embedded_output_file_path)

    uploaded_to_qdrant = 0
    vector_size = 0

    if embedded_records:
        vector_size = len(embedded_records[0]["embedding"])

        client = get_qdrant_client()
        ensure_collection_exists(
            client=client,
            collection_name=collection_name,
            vector_size=vector_size,
        )
        upsert_records(
            client=client,
            collection_name=collection_name,
            records=embedded_records,
        )
        uploaded_to_qdrant = len(embedded_records)

    all_failed_items = failed_files + embedding_failed_records

    return {
        "total_files": len(raw_notes),
        "parsed_count": len(parsed_notes),
        "embedded_count": len(embedded_records),
        "uploaded_to_qdrant": uploaded_to_qdrant,
        "failed_count": len(all_failed_items),
        "failed_items": all_failed_items,
        "collection_name": collection_name,
        "vector_size": vector_size,
        "parsed_output_path": str(parsed_output_file_path),
        "embedded_output_path": str(embedded_output_file_path),
    }


def _parsed_note_to_dict(note: ParsedNote) -> dict[str, Any]:
    return {
        "id": note.id,
        "date": note.date.isoformat(),
        "text": note.text,
        "calories": note.calories,
        "protein": note.protein,
        "fat": note.fat,
        "carbs": note.carbs,
    }


def _save_parsed_notes(parsed_notes: list[ParsedNote], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)

    records = [_parsed_note_to_dict(note) for note in parsed_notes]

    output_path.write_text(
        json.dumps(records, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def _save_embedded_records(records: list[dict[str, Any]], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(records, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def _format_validation_errors(validation_result: ValidationResult) -> str:
    return "; ".join(validation_result.errors)
