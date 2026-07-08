import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests

app = FastAPI()

FRONTEND_ORIGINS = os.getenv("FRONTEND_ORIGINS", "*").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=FRONTEND_ORIGINS,
    allow_credentials=False,
    allow_methods=["POST", "OPTIONS"],
    allow_headers=["Content-Type"],
)

SILICONFLOW_API_KEY = os.getenv("SILICONFLOW_API_KEY", "")
SILICONFLOW_URL = "https://api.siliconflow.cn/v1/chat/completions"

class TextRequest(BaseModel):
    text: str

@app.post("/api/humanize")
async def humanize_text(request: TextRequest):
    if not request.text.strip():
        raise HTTPException(status_code=400, detail="Input text cannot be empty")
    
    if not SILICONFLOW_API_KEY:
        raise HTTPException(status_code=500, detail="API Key not configured")

    system_prompt = (
        "You are an expert human writer. Your task is to rewrite the user's input text "
        "to make it sound completely natural, organic, and human-written. "
        "Strictly avoid common AI patterns, repetitive sentence structures, and overly formal transitions. "
        "Maintain the original meaning and core facts, but vary sentence lengths, use idioms appropriately, "
        "and introduce minor natural perplexity and burstiness. The output must easily bypass AI detectors like GPTZero and Turnitin."
    )

    payload = {
        "model": "deepseek-ai/DeepSeek-V3",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": request.text}
        ],
        "stream": False
    }

    headers = {
        "Authorization": f"Bearer {SILICONFLOW_API_KEY}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(SILICONFLOW_URL, json=payload, headers=headers, timeout=60)
        response_data = response.json()
        
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response_data.get("message", "API request failed"))
            
        result_text = response_data["choices"][0]["message"]["content"]
        return {"success": True, "data": result_text}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def health_check():
    return {"status": "ok", "service": "BypassAI API"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)