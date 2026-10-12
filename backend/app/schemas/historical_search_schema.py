from pydantic import BaseModel

class HistoricalSearchResponse(BaseModel):
    answer: str
    matched_summary_ids: list[int]