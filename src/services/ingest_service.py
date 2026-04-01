import json
from dataclasses import asdict
from pathlib import Path
from typing import Any

from ingestion.file_loader import load_notes_from_directory
from ingestion.note_parser import (
    InvalidNoteFilenameError,
    MissingNutritionFieldError,
    NoteParserError,
    ParsedNote,
    parse_note,
)
from ingestion.validator import ValidationResult, validate_parsed_note


def run_ingestion(
        notes_dir: str | Path,
        output_path: str | Path
) -> dict[str, Any]:
    notes_dir_path = Path(notes_dir)
    output_file_path = Path(output_path)

    parsed_notes: list[ParsedNote] = []
    failed_files: list[dict[str, str]] = []

    raw_notes = load_notes_from_directory(notes_dir_path)

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
                        "error": _format_validation_errors(validation_result),
                    }
                )

        except (
            InvalidNoteFilenameError,
            MissingNutritionFieldError,
            NoteParserError
        ) as exc:
            failed_files.append(
                {
                    "filename": raw_note.filename,
                    "error": str(exc),
                }
            )

    _save_parsed_notes(parsed_notes, output_file_path)

    return {
        "total_files": len(raw_notes),
        "parsed_count": len(parsed_notes),
        "failed_count": len(failed_files),
        "failed_files": failed_files,
        "output_path": str(output_file_path),
    }


def _save_parsed_notes(
        parsed_notes: list[ParsedNote],
        output_path: Path
) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)

    serializable_notes = [
        _serialize_parsed_note(note) for note in parsed_notes
    ]

    output_path.write_text(
        json.dumps(serializable_notes, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def _serialize_parsed_note(note: ParsedNote) -> dict[str, Any]:
    note_dict = asdict(note)
    note_dict["date"] = note.date.isoformat()
    return note_dict


def _format_validation_errors(validation_result: ValidationResult) -> str:
    return "; ".join(validation_result.errors)
