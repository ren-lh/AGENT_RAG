from fastapi import FastAPI

app = FastAPI(
    title='AGENT_RAG',
    description="AGENT_RAG",
    version="0.1.0",
)

# 健康检查
@app.get('/health')
async def health():
    return {"status": "ok"}

@app.get("/")
async def root():
    return {"message": "AGENT_RAG API is running"}