from langchain.chat_models import ollama
from langchain.prompts import ChatMessagePromptTemplate

url = "https://blog.langchain.dev/announcing-langsmith/"

template = """Sumarize the following question based on the context:
Question: {question}

Context:
{context}"""

prompt