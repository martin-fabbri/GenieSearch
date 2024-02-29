from app.ingest import scrape_url

url = "https://blog.langchain.dev/announcing-langsmith/"

content = scrape_url(url)[:10000]
print(content)