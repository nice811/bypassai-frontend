import os
import logging
import re
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, field_validator
import httpx
import json

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("bypassai")

app = FastAPI()

FRONTEND_ORIGINS = os.getenv("FRONTEND_ORIGINS", "*").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=FRONTEND_ORIGINS,
    allow_credentials=False,
    allow_methods=["POST", "OPTIONS", "GET"],
    allow_headers=["Content-Type"],
)

SILICONFLOW_API_KEY = os.getenv("SILICONFLOW_API_KEY", "")
SILICONFLOW_URL = "https://api.siliconflow.cn/v1/chat/completions"
MODEL_NAME = os.getenv("MODEL_NAME", "deepseek-ai/DeepSeek-V3")
MAX_INPUT_CHARS = int(os.getenv("MAX_INPUT_CHARS", "10000"))

DEFAULT_SYSTEM_PROMPT = """You are an expert human writer specializing in making AI-generated text sound natural, organic, and indistinguishable from human-written content.

CORE RULES (MUST FOLLOW STRICTLY):
1. MEANING PRESERVATION: Keep the original meaning, facts, and core information COMPLETELY unchanged. Never add new information or remove key facts.

2. LANGUAGE CONSERVATION: OUTPUT MUST BE IN THE SAME LANGUAGE AS THE INPUT. If the input is in English, output in English. If the input is in Chinese, output in Chinese. Do NOT translate!

3. LENGTH CONTROL: The output word count must stay within ±30% of the original text. NEVER expand short sentences into long paragraphs. NEVER excessively condense professional content.

4. STRUCTURE INTEGRITY: Maintain the original text structure and paragraph layout. If the input has N sentences, output should have roughly N sentences (±2).

5. HUMANNESS ENHANCEMENT:
   - Vary sentence lengths naturally (mix short and long sentences)
   - Avoid repetitive sentence patterns
   - Use natural transitions instead of mechanical ones like "Furthermore", "In conclusion"
   - Add minor natural variations that real humans make

6. STYLE FIDELITY: Preserve the original writing style (academic stays academic, casual stays casual, technical stays technical).

7. ZERO AI DETECTION: The output must easily bypass all AI detectors including GPTZero, Turnitin, and Originality.ai.

Output ONLY the rewritten text. No explanations, no comments, no markdown."""

SHORT_TEXT_PROMPT_SUFFIX = """

CRITICAL OVERRIDE FOR SHORT TEXT: The input is very short. YOU MUST output approximately the same number of words (within ±20%). If the input is a single sentence, output a single sentence. Do NOT expand, add context, or elaborate."""

SYSTEM_PROMPT = os.getenv("SYSTEM_PROMPT", DEFAULT_SYSTEM_PROMPT)

class TextRequest(BaseModel):
    text: str
    stream: bool = True

    @field_validator("text")
    @classmethod
    def validate_text(cls, v):
        v = v.strip()
        if not v:
            raise ValueError("输入文本不能为空")
        if len(v) > MAX_INPUT_CHARS:
            raise ValueError(f"输入文本超过最大长度限制：{MAX_INPUT_CHARS} 字")
        return v

def count_length(text: str) -> int:
    clean_text = "".join(text.split())
    zh_chars = len(re.findall(r'[\u4e00-\u9fa5]', clean_text))
    if zh_chars > len(clean_text) * 0.3:
        return len(clean_text)
    return len(text.split())

def is_short_text(text: str) -> bool:
    clean_text = "".join(text.split())
    zh_chars = len(re.findall(r'[\u4e00-\u9fa5]', clean_text))
    if zh_chars > len(clean_text) * 0.3:
        return len(clean_text) < 40
    return len(text.split()) < 20

async def llm_stream_generator(text: str, use_short_prompt: bool):
    prompt = SYSTEM_PROMPT
    if use_short_prompt:
        prompt = SYSTEM_PROMPT + SHORT_TEXT_PROMPT_SUFFIX

    base_len = count_length(text)
    max_tokens = min(max(base_len * 3, 150), 4096)

    payload = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": prompt},
            {"role": "user", "content": text}
        ],
        "stream": True,
        "temperature": 0.8,
        "top_p": 0.85,
        "max_tokens": max_tokens
    }

    headers = {
        "Authorization": f"Bearer {SILICONFLOW_API_KEY}",
        "Content-Type": "application/json"
    }

    async with httpx.AsyncClient(timeout=90.0) as client:
        try:
            async with client.stream("POST", SILICONFLOW_URL, json=payload, headers=headers) as response:
                if response.status_code != 200:
                    error_text = await response.aread()
                    logger.error(f"API error: {response.status_code} - {error_text.decode('utf-8', errors='ignore')}")
                    yield f"data: {json.dumps({'error': '模型后端响应错误'})}\n\n"
                    return

                async for line in response.aiter_lines():
                    if not line.strip():
                        continue
                    if line.startswith("data:"):
                        data_content = line[5:].strip()
                        if data_content == "[DONE]":
                            break

                        try:
                            res_json = json.loads(data_content)
                            delta = res_json["choices"][0]["delta"].get("content", "")
                            if delta:
                                yield f"data: {json.dumps({'chunk': delta}, ensure_ascii=False)}\n\n"
                        except Exception:
                            continue
        except Exception as e:
            logger.error(f"Stream error: {str(e)}")
            yield f"data: {json.dumps({'error': str(e)})}\n\n"


@app.post("/api/humanize")
async def humanize_text(request: TextRequest):
    if not SILICONFLOW_API_KEY:
        raise HTTPException(status_code=500, detail="未配置后端 SILICONFLOW_API_KEY 环境变量")

    short = is_short_text(request.text)
    logger.info(f"Request: length={count_length(request.text)}, short={short}, stream={request.stream}")

    if request.stream:
        return StreamingResponse(
            llm_stream_generator(request.text, use_short_prompt=short),
            media_type="text/event-stream"
        )
    else:
        full_text = ""
        async for chunk_msg in llm_stream_generator(request.text, use_short_prompt=short):
            if "chunk" in chunk_msg:
                try:
                    line_data = json.loads(chunk_msg.replace("data: ", "").strip())
                    full_text += line_data.get("chunk", "")
                except:
                    pass
        return {"success": True, "data": full_text.strip()}


@app.get("/")
async def health_check():
    return {
        "status": "ok",
        "service": "BypassAI Advanced API",
        "model": MODEL_NAME,
        "config": {
            "max_input_chars": MAX_INPUT_CHARS,
            "api_key_configured": bool(SILICONFLOW_API_KEY)
        }
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
