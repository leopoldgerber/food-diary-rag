import json
from pathlib import Path
from typing import Any

from calculations.nutrition import calculate_metric
from query_processing.date_resolver import filter_records_by_period
from query_processing.query_classifier import classify_query


class NumericQueryServiceError(Exception):
    """Base exception for numeric query service errors."""


def run_numeric_query(
    raw_query: str,
    records_path: str | Path,
) -> dict[str, Any]:
    query_analysis = classify_query(raw_query)

    if query_analysis.query_type != "numeric":
        raise NumericQueryServiceError(
            f"Query is not numeric: {query_analysis.query_type}"
        )

    if not query_analysis.metric:
        raise NumericQueryServiceError(
            "Metric could not be determined from query.")

    if not query_analysis.operation:
        raise NumericQueryServiceError(
            "Operation could not be determined from query.")

    records = _load_records(records_path)
    filtered_records = filter_records_by_period(records, query_analysis.period)

    result_value = calculate_metric(
        records=filtered_records,
        metric=query_analysis.metric,
        operation=query_analysis.operation,
    )

    used_dates = [record["date"] for record in filtered_records]

    return {
        "query": raw_query,
        "query_type": query_analysis.query_type,
        "metric": query_analysis.metric,
        "operation": query_analysis.operation,
        "period": query_analysis.period,
        "value": result_value,
        "used_dates": used_dates,
        "records_count": len(filtered_records),
    }


def _load_records(records_path: str | Path) -> list[dict[str, Any]]:
    path = Path(records_path)

    if not path.exists():
        raise FileNotFoundError(f"Records file does not exist: {path}")

    return json.loads(path.read_text(encoding="utf-8"))
