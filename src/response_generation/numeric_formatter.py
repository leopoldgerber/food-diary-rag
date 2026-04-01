from typing import Any


METRIC_LABELS = {
    "calories": "калории",
    "protein": "белки",
    "fat": "жиры",
    "carbs": "углеводы",
}

OPERATION_LABELS = {
    "sum": "Сумма",
    "average": "Среднее",
    "min": "Минимум",
    "max": "Максимум",
}


class NumericFormatterError(Exception):
    """Base exception for numeric formatter errors."""


def format_numeric_result(result: dict[str, Any]) -> str:
    metric = result.get("metric")
    operation = result.get("operation")
    period = result.get("period")
    value = result.get("value")
    used_dates = result.get("used_dates", [])
    records_count = result.get("records_count")

    if metric not in METRIC_LABELS:
        raise NumericFormatterError(f"Unsupported metric: {metric}")

    if operation not in OPERATION_LABELS:
        raise NumericFormatterError(f"Unsupported operation: {operation}")

    if not isinstance(value, (int, float)):
        raise NumericFormatterError("Result value must be numeric.")

    if not isinstance(used_dates, list):
        raise NumericFormatterError("used_dates must be a list.")

    if not isinstance(records_count, int):
        raise NumericFormatterError("records_count must be an integer.")

    operation_label = OPERATION_LABELS[operation]
    metric_label = METRIC_LABELS[metric]
    formatted_value = _format_number(float(value))
    period_label = period if period else "за выбранный период"

    lines = [
        f"{operation_label} {metric_label} {period_label}: {formatted_value}.",
        f"Найдено дней: {records_count}.",
    ]

    if used_dates:
        lines.append(f"Использованные даты: {', '.join(used_dates)}.")

    return "\n".join(lines)


def _format_number(value: float) -> str:
    if value.is_integer():
        return str(int(value))

    return f"{value:.2f}".rstrip("0").rstrip(".")
