"""Note parsing utilities."""
import re
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Optional

from src.ingestion.file_loader import RawNote


@dataclass(frozen=True)
class ParsedNote:
    id: str
    date: date
    text: str
    calories: float
    protein: float
    fat: float
    carbs: float


class NoteParserError(Exception):
    """Base exception for note parsing errors."""


class InvalidNoteFilenameError(NoteParserError):
    """Raised when the note filename does not contain a valid ISO date."""


class MissingNutritionFieldError(NoteParserError):
    """Raised when one or more nutrition fields are missing."""


def parse_note(raw_note: RawNote) -> ParsedNote:
    """
    Parse a raw note into a structured daily record.

    Rules for the first MVP version:
    - date is extracted from filename: YYYY-MM-DD.md
    - full file content is stored as text
    - calories, protein, fat, carbs are extracted from note text

    Args:
        raw_note: Raw note loaded from disk.

    Returns:
        ParsedNote with extracted structured fields.

    Raises:
        InvalidNoteFilenameError:
            If filename does not match expected date format.
        MissingNutritionFieldError:
            If any nutrition field is missing in the note text.
    """
    note_date = _extract_date_from_filename(raw_note.filename)
    normalized_text = raw_note.content.strip()

    calories = _extract_required_number(normalized_text, field_name="calories")
    protein = _extract_required_number(normalized_text, field_name="protein")
    fat = _extract_required_number(normalized_text, field_name="fat")
    carbs = _extract_required_number(normalized_text, field_name="carbs")

    record_id = _build_record_id(note_date)

    return ParsedNote(
        id=record_id,
        date=note_date,
        text=normalized_text,
        calories=calories,
        protein=protein,
        fat=fat,
        carbs=carbs,
    )


def _extract_date_from_filename(filename: str) -> date:
    stem = Path(filename).stem

    try:
        return date.fromisoformat(stem)
    except ValueError as exc:
        raise InvalidNoteFilenameError(
            f"Filename must be in YYYY-MM-DD format: {filename}"
        ) from exc


def _build_record_id(note_date: date) -> str:
    return note_date.isoformat()


def _extract_required_number(text: str, field_name: str) -> float:
    value = _extract_number(text, field_name)

    if value is None:
        raise MissingNutritionFieldError(
            f"Missing required nutrition field: {field_name}"
        )

    return value


def _extract_number(text: str, field_name: str) -> Optional[float]:
    patterns = _get_patterns_for_field(field_name)

    for pattern in patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            raw_value = match.group(1).replace(",", ".").strip()
            return float(raw_value)

    return None


def _get_patterns_for_field(field_name: str) -> list[str]:
    field_patterns = {
        "calories": [
            r"калории\s*[:=]\s*(\d+(?:[.,]\d+)?)",
            r"ккал\s*[:=]\s*(\d+(?:[.,]\d+)?)",
            r"calories\s*[:=]\s*(\d+(?:[.,]\d+)?)",
        ],
        "protein": [
            r"белки\s*[:=]\s*(\d+(?:[.,]\d+)?)",
            r"белок\s*[:=]\s*(\d+(?:[.,]\d+)?)",
            r"protein\s*[:=]\s*(\d+(?:[.,]\d+)?)",
        ],
        "fat": [
            r"жиры\s*[:=]\s*(\d+(?:[.,]\d+)?)",
            r"жир\s*[:=]\s*(\d+(?:[.,]\d+)?)",
            r"fat\s*[:=]\s*(\d+(?:[.,]\d+)?)",
        ],
        "carbs": [
            r"углеводы\s*[:=]\s*(\d+(?:[.,]\d+)?)",
            r"углеводы\s+(\d+(?:[.,]\d+)?)",
            r"carbs\s*[:=]\s*(\d+(?:[.,]\d+)?)",
        ],
    }

    try:
        return field_patterns[field_name]
    except KeyError as exc:
        raise ValueError(f"Unsupported field name: {field_name}") from exc
