from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from langserve import add_routes
from app.chain import research_writer_chain

app = FastAPI(
    title="GenieSearch API",
    version="0.10",
    description=("GenieSearch is your AI research assistant that magically compiles "
                 "comprehensive insights from the web, answering queries with depth and precision.")
)


@app.get("/")
async def redirect_root_to_docs():
    return RedirectResponse("/docs")


# Edit this to add the chain you want to add
add_routes(app, research_writer_chain, path="/research-writer")

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
