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

DEFAULT_SYSTEM_PROMPT = """你是一位精通中英文学术与创意写作的人类专家，擅长将富有AI感、机翻感的死板文本改写为自然、地道、极具人类呼吸感的文章。

核心原则（必须严格遵守）：
1. 含义保留：绝不添加、脑补任何原文中不存在的事实或例子，也绝不删减任何核心论点。
2. 句长变异性 (Burstiness 控制)：
   - AI 写作的致命弱点是句式整齐、长度均匀。你必须刻意交错使用“极短句（10字以内）”、“中句（20字左右）”和“复杂长句（30字以上）”。
   - 模仿人类思考的跌宕起伏，让文本富有节奏感与呼吸感。
3. 杜绝AI高频词：严禁使用“总而言之”、“不可否认”、“值得注意的是”、“显而易见”、“此外”等机械的过渡词。改用人类更常用的隐性逻辑连接。
4. 文体契合：保持原有的语言风格（学术论文继续保持严谨学术风，商业文案保持营销风），但彻底打碎机械的句式。
5. 零AI检测：改写后的文本必须能够完美通过 Turnitin, GPTZero, CopyLeaks 等主流AI检测器。

直接输出改写后的文本，严禁包含任何前言、后记、解释、反思、括号注释或 Markdown 代码块标识。"""

SHORT_TEXT_PROMPT_SUFFIX = """

⚠️【极端硬性约束 - 短文本防膨胀】：
当前输入的文本极其简短（属于短句/短语）。你必须克制扩写的欲望！
- 如果输入是一个短句，改写后必须有且仅有一个短句。
- 字数/词数变动必须控制在原文本的 ±15% 以内，严禁扩写、严禁添加任何前置修饰语、背景解释或衍生例子。
- 严禁为了降低AI感而恶意把短句拉长为长难句！"""

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
