from typing import Any


class SemanticFormatterError(Exception):
    """Base exception for semantic formatter errors."""


def format_semantic_results(
    raw_query: str,
    results: list[dict[str, Any]],
) -> str:
    if not raw_query.strip():
        raise SemanticFormatterError("Query is empty.")

    if not isinstance(results, list):
        raise SemanticFormatterError("Results must be a list.")

    if not results:
        return f"По запросу '{raw_query}' ничего не найдено."

    lines = [
        f"По запросу '{raw_query}' найдены записи:",
    ]

    for item in results:
        date = str(item.get("date", "unknown"))
        text = str(item.get("text", "")).strip()

        if not text:
            text = "Текст записи отсутствует."

        preview = _build_preview(text)

        lines.append(f"- {date}: {preview}")

    return "\n".join(lines)


def _build_preview(text: str, max_length: int = 120) -> str:
    normalized_text = " ".join(text.split())

    if len(normalized_text) <= max_length:
        return normalized_text

    return normalized_text[: max_length - 3].rstrip() + "..."
