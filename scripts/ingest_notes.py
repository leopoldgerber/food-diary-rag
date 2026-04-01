from pathlib import Path

from src.ingestion.file_loader import load_notes_from_directory
from src.ingestion.note_parser import (
    InvalidNoteFilenameError,
    MissingNutritionFieldError,
    NoteParserError,
    ParsedNote,
    parse_note,
)
from src.ingestion.validator import ValidationResult, validate_parsed_note


def main() -> None:
    notes_dir = Path("data/raw")

    parsed_notes: list[ParsedNote] = []
    failed_files: list[tuple[str, str]] = []

    raw_notes = load_notes_from_directory(notes_dir)

    for raw_note in raw_notes:
        try:
            parsed_note = parse_note(raw_note)
            validation_result = validate_parsed_note(parsed_note)

            if validation_result.is_valid:
                parsed_notes.append(parsed_note)
                print(f"[OK] {raw_note.filename} -> {parsed_note.id}")
            else:
                error_message = _format_validation_errors(validation_result)
                failed_files.append((raw_note.filename, error_message))
                print(f"[INVALID] {raw_note.filename} -> {error_message}")

        except (
            InvalidNoteFilenameError,
            MissingNutritionFieldError,
            NoteParserError
        ) as exc:
            failed_files.append((raw_note.filename, str(exc)))
            print(f"[ERROR] {raw_note.filename} -> {exc}")

    print()
    print("Ingestion summary")
    print(f"- Total files: {len(raw_notes)}")
    print(f"- Successfully parsed: {len(parsed_notes)}")
    print(f"- Failed: {len(failed_files)}")

    if failed_files:
        print()
        print("Failed files")
        for filename, error in failed_files:
            print(f"- {filename}: {error}")


def _format_validation_errors(validation_result: ValidationResult) -> str:
    return "; ".join(validation_result.errors)


if __name__ == "__main__":
    main()
