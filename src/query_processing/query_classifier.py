import re

from models.query import QueryAnalysis


NUMERIC_KEYWORDS = {
    "среднее",
    "средние",
    "средний",
    "среднюю",
    "сумма",
    "сумму",
    "суммарно",
    "всего",
    "максимум",
    "максимальные",
    "максимальный",
    "минимум",
    "минимальные",
    "минимальный",
    "average",
    "sum",
    "total",
    "max",
    "min",
}

METRIC_KEYWORDS = {
    "калории": "calories",
    "калорий": "calories",
    "ккал": "calories",
    "белки": "protein",
    "белка": "protein",
    "белков": "protein",
    "белок": "protein",
    "жиры": "fat",
    "жира": "fat",
    "жиров": "fat",
    "жир": "fat",
    "углеводы": "carbs",
    "углеводов": "carbs",
    "углеводами": "carbs",
    "угли": "carbs",
    "calories": "calories",
    "protein": "protein",
    "fat": "fat",
    "carbs": "carbs",
}

OPERATION_KEYWORDS = {
    "среднее": "average",
    "средние": "average",
    "средний": "average",
    "среднюю": "average",
    "сумма": "sum",
    "сумму": "sum",
    "суммарно": "sum",
    "всего": "sum",
    "максимум": "max",
    "максимальные": "max",
    "максимальный": "max",
    "минимум": "min",
    "минимальные": "min",
    "минимальный": "min",
    "average": "average",
    "sum": "sum",
    "total": "sum",
    "max": "max",
    "min": "min",
}

PERIOD_PATTERNS = [
    r"за неделю",
    r"за 7 дней",
    r"за 3 дня",
    r"за день",
    r"вчера",
    r"сегодня",
]


def classify_query(raw_query: str) -> QueryAnalysis:
    normalized_query = raw_query.strip().lower()

    query_type = _detect_query_type(normalized_query)
    period = _extract_period(normalized_query)
    metric = _extract_metric(normalized_query)
    operation = _extract_operation(normalized_query)

    return QueryAnalysis(
        raw_query=raw_query,
        query_type=query_type,
        period=period,
        metric=metric,
        operation=operation,
    )


def _detect_query_type(query: str) -> str:
    has_numeric_signal = _has_numeric_signal(query)
    has_semantic_signal = _has_semantic_signal(query)

    if has_numeric_signal and has_semantic_signal:
        return "hybrid"

    if has_numeric_signal:
        return "numeric"

    return "semantic"


def _has_numeric_signal(query: str) -> bool:
    has_operation = any(keyword in query for keyword in NUMERIC_KEYWORDS)
    has_metric = any(keyword in query for keyword in METRIC_KEYWORDS)
    return has_operation or has_metric


def _has_semantic_signal(query: str) -> bool:
    semantic_markers = [
        "когда",
        "в какие дни",
        "что ел",
        "ел ли",
        "было ли",
        "найди",
        "покажи",
        "when",
        "find",
        "show",
    ]
    return any(marker in query for marker in semantic_markers)


def _extract_period(query: str) -> str | None:
    for pattern in PERIOD_PATTERNS:
        match = re.search(pattern, query)
        if match:
            return match.group(0)

    return None


def _extract_metric(query: str) -> str | None:
    for keyword, metric in METRIC_KEYWORDS.items():
        if keyword in query:
            return metric

    return None


def _extract_operation(query: str) -> str | None:
    for keyword, operation in OPERATION_KEYWORDS.items():
        if keyword in query:
            return operation

    return None
