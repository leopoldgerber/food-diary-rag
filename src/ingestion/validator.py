from dataclasses import dataclass

from ingestion.note_parser import ParsedNote


@dataclass(frozen=True)
class ValidationResult:
    is_valid: bool
    errors: list[str]


def validate_parsed_note(note: ParsedNote) -> ValidationResult:
    errors: list[str] = []

    if not note.text.strip():
        errors.append("Text is empty.")

    if note.calories < 0:
        errors.append("Calories cannot be negative.")

    if note.protein < 0:
        errors.append("Protein cannot be negative.")

    if note.fat < 0:
        errors.append("Fat cannot be negative.")

    if note.carbs < 0:
        errors.append("Carbs cannot be negative.")

    return ValidationResult(
        is_valid=len(errors) == 0,
        errors=errors,
    )
