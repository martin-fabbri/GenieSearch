import asyncio
from langchain.llms import Ollama
from langchain_community.chat_models import ChatOllama
from langchain.schema.output_parser import StrOutputParser
from langchain.schema.runnable import RunnablePassthrough, RunnableLambda
from langchain_core.prompts import ChatPromptTemplate
from app.ingest import scrape_url
from app.ingest import collapse_list_of_lists
from app.search import web_search

LLM_MODEL = "mixtral:instruct"  # ("gemma:7b-instruct" | "mistral:instruct")
TEMPERATURE = 0.9

### Single Question Prompt
template = """{text}
-----------
Using the above text, answer in short the following question:
> {question}
-----------
if the question cannot be answered using the text, imply summarize the text. Include all
factual information, numbers, stats etc if available.
"""

SINGLE_QUESTION_PROMPT = ChatPromptTemplate.from_template(template)

# Setup Chat Chain
scrape_and_summarize_chain = (
    RunnablePassthrough.assign(text=lambda x: scrape_url(x["url"])[:10000])
    | SINGLE_QUESTION_PROMPT
    | ChatOllama(model=LLM_MODEL)
    | StrOutputParser()
)

web_search_chain = (
    RunnablePassthrough.assign(urls=lambda x: asyncio.run(web_search(x["question"])))
    | (lambda x: [{"question": x["question"], "url": u} for u in x["urls"]])
    | scrape_and_summarize_chain.map()
)


# Expanded(Multi Query?) Web Reseach
questions_generation = (
    "Write 3 google search queries to search online that form an objective "
    "opinion from the following question: {question}\n "
    "Return a python list in the following format: "
    "['query 1', 'query 2', 'query 3']\n "
    "Do not include anything else after the list."
)

SEARCH_PROMPT = ChatPromptTemplate.from_messages([("user", questions_generation)])

search_qanda_chain = (
    SEARCH_PROMPT
    | ChatOllama(model=LLM_MODEL)
    | StrOutputParser()
    | eval
    | (lambda l: [{"question": q} for q in l])
)

full_research_chain = search_qanda_chain | web_search_chain.map()


# Reseach Report Writer
WRITER_SYSTEM_PROMPT = (
    "You are an AI critical thinker research assistant. Your sole purpose "
    "is to write well written, critically acclaimed, objective and structured "
    "reports on given text."
)

RESEARCH_REPORT_TEMPLATE = """Information:
--------
{research_summary}
--------
Using the above information, answer the following question or topic: "{question}" 
in a detailed reseach report format. The report should focus on the answer to the question, 
should be well structured, informative,
in depth, with facts and numbers if available and a minimum of 1,200 words.
You should strive to write the report as long as you can using all relevant 
and necessary information provided.
You must write the report with markdown syntax.
You MUST determine your own concrete and valid opinion based on the given 
information. Do NOT deter to general and meaningless conclusions.
Write all used source urls at the end of the report, and make sure to not 
add duplicated sources, but only one reference for each.
You must write the report in apa format.
Please do your best, this is very important to my career."""

research_writer_prompt = ChatPromptTemplate.from_messages(
    [("system", WRITER_SYSTEM_PROMPT), ("user", RESEARCH_REPORT_TEMPLATE)]
)

research_writer_chain = (
    RunnablePassthrough.assign(
        research_summary=full_research_chain | collapse_list_of_lists
    )
    | research_writer_prompt
    | ChatOllama(model=LLM_MODEL)
    | StrOutputParser()
)
