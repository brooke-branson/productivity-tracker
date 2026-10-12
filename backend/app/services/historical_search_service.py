from google import genai
from google.genai import types
from app.services.weekly_summary_service import get_ranked_weekly_summaries
from app.schemas.weekly_summary_schema import WeeklySummaryResponse
from app.schemas.historical_search_schema import HistoricalSearchResponse
from dotenv import load_dotenv
import os
import json
load_dotenv()

def answer_historical_search(db,query: str , n_results: int = 3) -> HistoricalSearchResponse:
    results = get_ranked_weekly_summaries(db, query, n_results)

    summary_context = [
        WeeklySummaryResponse.model_validate(summary).model_dump(
            mode="json",
            exclude={"created_at", "updated_at"},
        ) for summary in results
    ]

    client = genai.Client(api_key=os.getenv("GENAI_API_KEY"))


    prompt = """
        Answer the user's historical productivity question using only the
        retrieved weekly summaries.

        Rules:
        - Use only the provided weekly summaries.
        - Do not invent activity or trends that are not supported by the data.
        - Treat the summaries as ranked by semantic relevance, with the first
        summary being the strongest match.
        - Mention relevant week date ranges when useful.
        - If the retrieved summaries do not support the question, say so.
        - matched_summary_ids must only contain ids from the provided weekly summaries.
        """

    contents = [
        types.Part.from_text(text=prompt),
        types.Part.from_text(text=json.dumps(summary_context, default=str)),
        types.Part.from_text(text=f"User question: {query}"),
    ]

    response = client.models.generate_content(
        model="gemini-flash-latest",
        contents=contents,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=HistoricalSearchResponse,
        ),
    )

    historical_search_response = HistoricalSearchResponse.model_validate_json(response.text)

    return historical_search_response