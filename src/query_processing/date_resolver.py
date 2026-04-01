from typing import Any


class DateResolutionError(Exception):
    """Base exception for date resolution errors."""


def filter_records_by_period(
    records: list[dict[str, Any]],
    period: str | None,
) -> list[dict[str, Any]]:
    if not records:
        raise DateResolutionError("No records available for period filtering.")

    sorted_records = sorted(records, key=lambda record: record["date"])

    if period is None:
        return sorted_records

    normalized_period = period.strip().lower()

    if normalized_period in {"за неделю", "за 7 дней"}:
        return sorted_records[-7:]

    if normalized_period == "за 3 дня":
        return sorted_records[-3:]

    if normalized_period in {"за день", "сегодня"}:
        return sorted_records[-1:]

    if normalized_period == "вчера":
        if len(sorted_records) < 2:
            raise DateResolutionError("Not enough records to resolve 'вчера'.")
        return [sorted_records[-2]]

    raise DateResolutionError(f"Unsupported period: {period}")
