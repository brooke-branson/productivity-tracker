from dataclasses import dataclass
from sqlalchemy.orm import Session

from pydantic_ai import Agent, RunContext
from app.schemas.historical_search_schema import HistoricalSearchResponse
from app.schemas.weekly_summary_schema import WeeklySummaryResponse
from app.services.weekly_summary_service import get_ranked_weekly_summaries

@dataclass
class HistoricalSearchDeps:
    db: Session

historical_search_agent = Agent(
    "google:gemini-flash-latest",
    deps_type=HistoricalSearchDeps,
    output_type=HistoricalSearchResponse,
    instructions="""
        You are a historical productivity analysis assistant.

        For any question about past productivity, tasks, workload, focus, categories,
        time spent, or patterns, you MUST call search_productivity_history before answering.

        Base your answer only on data returned by that tool.
        Do not invent historical activity.
        Mention relevant week ranges when useful.
        Only include matched_summary_ids that came from the tool results.
        """
        )

@historical_search_agent.tool
def search_productivity_history(
    ctx: RunContext[HistoricalSearchDeps],
    query: str,
    n_results: int = 3,
    ) -> list[WeeklySummaryResponse]:

    summaries = get_ranked_weekly_summaries(ctx.deps.db, query, n_results)

    return [
        WeeklySummaryResponse.model_validate(summary) for summary in summaries
    ]

def answer_historical_search(
    db: Session,
    query:str
) -> HistoricalSearchResponse:
    response = historical_search_agent.run_sync(
        query,
        deps=HistoricalSearchDeps(db=db),
    )
    return response.output