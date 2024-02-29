# Web Search Agent
from langchain.utilities import DuckDuckGoSearchAPIWrapper

NUM_RESULTS_PER_QUESTION = 3
ddg_search = DuckDuckGoSearchAPIWrapper()

async def web_search(query: str, num_results: int = NUM_RESULTS_PER_QUESTION):
    web_query_results = ddg_search.results(query, num_results)
    return [r["link"] for r in web_query_results]

