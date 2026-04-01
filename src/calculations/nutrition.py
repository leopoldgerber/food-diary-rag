from typing import Any


SUPPORTED_METRICS = {"calories", "protein", "fat", "carbs"}
SUPPORTED_OPERATIONS = {"sum", "average", "min", "max"}


class NutritionCalculationError(Exception):
    """Base exception for nutrition calculation errors."""


def calculate_metric(
    records: list[dict[str, Any]],
    metric: str,
    operation: str,
) -> float:
    if not records:
        raise NutritionCalculationError("No records provided for calculation.")

    if metric not in SUPPORTED_METRICS:
        raise NutritionCalculationError(f"Unsupported metric: {metric}")

    if operation not in SUPPORTED_OPERATIONS:
        raise NutritionCalculationError(f"Unsupported operation: {operation}")

    values = _extract_metric_values(records, metric)

    if operation == "sum":
        return sum_metric(values)

    if operation == "average":
        return average_metric(values)

    if operation == "min":
        return min_metric(values)

    if operation == "max":
        return max_metric(values)

    raise NutritionCalculationError(f"Unsupported operation: {operation}")


def sum_metric(values: list[float]) -> float:
    _validate_values(values)
    return float(sum(values))


def average_metric(values: list[float]) -> float:
    _validate_values(values)
    return float(sum(values) / len(values))


def min_metric(values: list[float]) -> float:
    _validate_values(values)
    return float(min(values))


def max_metric(values: list[float]) -> float:
    _validate_values(values)
    return float(max(values))


def _extract_metric_values(
        records: list[dict[str, Any]],
        metric: str
) -> list[float]:
    values: list[float] = []

    for record in records:
        if metric not in record:
            raise NutritionCalculationError(
                f"Metric '{metric}' is missing in record.")

        value = record[metric]

        if not isinstance(value, (int, float)):
            raise NutritionCalculationError(
                f"Metric '{metric}' must be numeric, got: "
                f"{type(value).__name__}"
            )

        values.append(float(value))

    return values


def _validate_values(values: list[float]) -> None:
    if not values:
        raise NutritionCalculationError("No values provided for calculation.")
