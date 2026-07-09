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
MODEL_NAME = os.getenv("MODEL_NAME", "deepseek-ai/DeepSeek-V3")

DEFAULT_SYSTEM_PROMPT = """You are an expert human writer who specializes in rewriting AI-generated text to sound natural, organic, and indistinguishable from human-written content.

CORE REQUIREMENTS (STRICTLY FOLLOW THESE RULES):
1. MEANING PRESERVATION: Keep the original meaning, facts, and core information must remain completely unchanged. Do not add new information or remove key facts.

2. LENGTH CONTROL: The output word count must stay within ±20% of the original text. NEVER expand short sentences into long paragraphs. NEVER pad content.

3. STRUCTURE INTEGRITY: Maintain the original text structure and paragraph layout. If the input has N sentences, output should have roughly N sentences (±1-2). Do not turn a single sentence into a whole paragraph.

4. HUMANNESS ENHANCEMENT:
   - Vary sentence lengths naturally (mix short and long sentences)
   - Use idioms, colloquial expressions, and conversational tone where appropriate
   - Introduce natural perplexity and burstiness
   - Avoid repetitive sentence patterns (avoid: "Furthermore", "In conclusion", etc.)
   - Add minor "imperfections" that real humans make (contractions, slightly varied wording)

5. STYLE FIDELITY: Preserve the original writing style (academic stays academic, casual stays casual, technical stays technical).

6. ZERO AI DETECTION: The output must easily bypass all AI detectors including GPTZero, Turnitin, Originality.ai, and others.

Directly output the rewritten text only, no explanations, no comments, no markdown formatting."""

SYSTEM_PROMPT = os.getenv("SYSTEM_PROMPT", DEFAULT_SYSTEM_PROMPT)

class TextRequest(BaseModel):
    text: str

@app.post("/api/humanize")
async def humanize_text(request: TextRequest):
    if not request.text.strip():
        raise HTTPException(status_code=400, detail="Input text cannot be empty")
    
    if not SILICONFLOW_API_KEY:
        raise HTTPException(status_code=500, detail="API Key not configured")

    payload = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": request.text}
        ],
        "stream": False,
        "temperature": 0.85,
        "top_p": 0.9
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
            
        result_text = response_data["choices"][0]["message"]["content"].strip()
        return {"success": True, "data": result_text}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def health_check():
    return {
        "status": "ok",
        "service": "BypassAI API",
        "model": MODEL_NAME,
        "prompt_length": len(SYSTEM_PROMPT)
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)