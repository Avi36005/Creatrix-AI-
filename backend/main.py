from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import influencer, content, trends, agent

app = FastAPI(title="ViraNova API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(influencer.router, prefix="/api/v1/influencer")
app.include_router(content.router,    prefix="/api/v1/content")
app.include_router(trends.router,     prefix="/api/v1/trends")
app.include_router(agent.router,      prefix="/api/v1/agent")

@app.get("/health")
def health():
    return {"status": "ViraNova is live 🚀"}
