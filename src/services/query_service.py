from calculations.nutrition import calculate_metric, NutritionCalculationError
from query_processing.query_classifier import classify_query
from query_processing.router import route_query
from response_generation.numeric_formatter import format_numeric_result
from response_generation.semantic_formatter import format_semantic_results
from retrieval.semantic_search import run_semantic_search
from services.numeric_query_service import run_numeric_query


class QueryServiceError(Exception):
    """Base exception for query service errors."""


def run_query(raw_query: str) -> str:
    if not raw_query.strip():
        raise QueryServiceError("Query is empty.")

    query_analysis = classify_query(raw_query)
    query_route = route_query(query_analysis)

    if query_route.query_type == "numeric":
        return _handle_numeric_query(raw_query)

    if query_route.query_type == "semantic":
        return _handle_semantic_query(raw_query)

    if query_route.query_type == "hybrid":
        return _handle_hybrid_query(raw_query, query_analysis.metric)

    raise QueryServiceError(
        f"Unsupported query type: {query_route.query_type}")


def _handle_numeric_query(raw_query: str) -> str:
    result = run_numeric_query(
        raw_query=raw_query,
        records_path="data/processed/parsed_records.json",
    )
    return format_numeric_result(result)


def _handle_semantic_query(raw_query: str) -> str:
    results = run_semantic_search(raw_query, limit=3)
    return format_semantic_results(raw_query, results)


def _handle_hybrid_query(raw_query: str, metric: str | None) -> str:
    results = run_semantic_search(raw_query, limit=3)

    if not results:
        return f"По запросу '{raw_query}' ничего не найдено."

    semantic_text = format_semantic_results(raw_query, results)

    if not metric:
        return semantic_text

    try:
        metric_value = calculate_metric(
            records=results,
            metric=metric,
            operation="min",
        )
    except NutritionCalculationError:
        return semantic_text

    metric_label = _get_metric_label(metric)

    hybrid_summary = [
        semantic_text,
        "",
        f"Дополнительно: минимальное значение по метрике '{metric_label}' "
        f"среди найденных записей: {_format_number(metric_value)}.",
    ]

    return "\n".join(hybrid_summary)


def _get_metric_label(metric: str) -> str:
    metric_labels = {
        "calories": "калории",
        "protein": "белки",
        "fat": "жиры",
        "carbs": "углеводы",
    }
    return metric_labels.get(metric, metric)


def _format_number(value: float) -> str:
    if value.is_integer():
        return str(int(value))

    return f"{value:.2f}".rstrip("0").rstrip(".")
