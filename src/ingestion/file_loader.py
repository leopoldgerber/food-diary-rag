from dataclasses import dataclass
from pathlib import Path
from typing import List


@dataclass(frozen=True)
class RawNote:
    filename: str
    path: Path
    content: str


class FileLoaderError(Exception):
    """Base exception for file loading errors."""


class NotesDirectoryNotFoundError(FileLoaderError):
    """Raised when the notes directory does not exist."""


class NotesPathIsNotDirectoryError(FileLoaderError):
    """Raised when the provided path is not a directory."""


def load_notes_from_directory(
        directory: str | Path,
        extension: str = ".md"
) -> List[RawNote]:
    """
    Load all note files with the given extension from a directory.

    Args:
        directory: Path to the directory with notes.
        extension: File extension to load. Defaults to ".md".

    Returns:
        A list of RawNote objects sorted by filename.

    Raises:
        NotesDirectoryNotFoundError: If the directory does not exist.
        NotesPathIsNotDirectoryError: If the path is not a directory.
        FileLoaderError: If a file cannot be read.
    """
    notes_dir = Path(directory)

    if not notes_dir.exists():
        raise NotesDirectoryNotFoundError(
            f"Notes directory does not exist: {notes_dir}"
        )

    if not notes_dir.is_dir():
        raise NotesPathIsNotDirectoryError(
            f"Path is not a directory: {notes_dir}"
        )

    if not extension.startswith("."):
        extension = f".{extension}"

    note_files = sorted(
        path for path in notes_dir.iterdir()
        if path.is_file() and path.suffix.lower() == extension.lower()
    )

    notes: List[RawNote] = []

    for file_path in note_files:
        try:
            content = file_path.read_text(encoding="utf-8")
        except OSError as exc:
            raise FileLoaderError(f"Failed to read file: {file_path}") from exc

        notes.append(
            RawNote(
                filename=file_path.name,
                path=file_path.resolve(),
                content=content,
            )
        )

    return notes
