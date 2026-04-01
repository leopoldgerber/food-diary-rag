from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class QueryAnalysis:
    raw_query: str
    query_type: str
    period: Optional[str] = None
    metric: Optional[str] = None
    operation: Optional[str] = None
