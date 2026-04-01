from dataclasses import dataclass

from models.query import QueryAnalysis


@dataclass(frozen=True)
class QueryRoute:
    query_type: str
    retrieval_mode: str
    calculation_mode: str
    use_llm: bool


def route_query(query_analysis: QueryAnalysis) -> QueryRoute:
    if query_analysis.query_type == "numeric":
        return QueryRoute(
            query_type="numeric",
            retrieval_mode="metadata",
            calculation_mode="programmatic",
            use_llm=False,
        )

    if query_analysis.query_type == "semantic":
        return QueryRoute(
            query_type="semantic",
            retrieval_mode="vector",
            calculation_mode="none",
            use_llm=False,
        )

    if query_analysis.query_type == "hybrid":
        return QueryRoute(
            query_type="hybrid",
            retrieval_mode="hybrid",
            calculation_mode="programmatic",
            use_llm=False,
        )

    raise ValueError(f"Unsupported query type: {query_analysis.query_type}")
