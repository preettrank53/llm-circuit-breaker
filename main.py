import os
import sqlite3
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
import httpx
from dotenv import load_dotenv

load_dotenv()

UPSTREAM_BASE_URL = os.getenv("UPSTREAM_BASE_URL")
UPSTREAM_API_KEY = os.getenv("UPSTREAM_API_KEY")
DB_PATH = "data/budget.db"
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

# Global HTTPX Client
http_client: httpx.AsyncClient = None

def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS budget (
                id INTEGER PRIMARY KEY,
                tokens_used INTEGER,
                limit_tokens INTEGER
            )
        ''')
        cursor.execute('SELECT COUNT(*) FROM budget')
        if cursor.fetchone()[0] == 0:
            cursor.execute('INSERT INTO budget (id, tokens_used, limit_tokens) VALUES (1, 0, 100)')
        conn.commit()

def get_budget():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT tokens_used, limit_tokens FROM budget WHERE id = 1')
        row = cursor.fetchone()
        if row:
            return row[0], row[1]
        return 0, 100

def update_tokens_used(tokens: int):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('UPDATE budget SET tokens_used = tokens_used + ? WHERE id = 1', (tokens,))
        conn.commit()

def reset_tokens_used():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('UPDATE budget SET tokens_used = 0 WHERE id = 1')
        conn.commit()

@asynccontextmanager
async def lifespan(app: FastAPI):
    global http_client
    init_db()
    http_client = httpx.AsyncClient()
    yield
    await http_client.aclose()

app = FastAPI(lifespan=lifespan)

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/v1/budget")
def read_budget():
    tokens_used, limit_tokens = get_budget()
    return {
        "tokens_used": tokens_used,
        "limit_tokens": limit_tokens,
        "remaining": max(0, limit_tokens - tokens_used)
    }

@app.post("/v1/budget/reset")
def reset_budget():
    reset_tokens_used()
    return {"status": "success", "message": "Budget reset to 0"}

@app.post("/v1/chat/completions")
async def proxy_chat_completions(request: Request):
    try:
        payload = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON payload")

    if payload.get("stream") is True or payload.get("stream") == "true":
        raise HTTPException(
            status_code=400, 
            detail="Streaming is not supported in the V1 budget proxy. Please set stream=False in your LLM client configuration."
        )

    tokens_used, limit_tokens = get_budget()
    if tokens_used >= limit_tokens:
        raise HTTPException(status_code=429, detail="Local Token Budget Exceeded")

    upstream_url = f"{UPSTREAM_BASE_URL}/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {UPSTREAM_API_KEY}",
        "Content-Type": request.headers.get("Content-Type", "application/json")
    }

    try:
        response = await http_client.post(
            upstream_url,
            json=payload,
            headers=headers,
            timeout=30.0
        )
        
        try:
            response_json = response.json()
        except Exception:
            return JSONResponse(content=response.text, status_code=response.status_code)

        if response.status_code == 200:
            usage = response_json.get("usage", {})
            total_tokens = usage.get("total_tokens", 0)
            
            if total_tokens > 0:
                update_tokens_used(total_tokens)
                
        return JSONResponse(
            content=response_json,
            status_code=response.status_code
        )
    except httpx.RequestError as exc:
        raise HTTPException(status_code=502, detail=f"Proxy error: {str(exc)}")

def start_server():
    import uvicorn
    # Local CLI runs bind to 127.0.0.1 for security. 
    # Docker users will still map 8000:8000 in their compose file.
    uvicorn.run("main:app", host="127.0.0.1", port=8000)
