import os
import time
import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, field_validator
import requests

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("bypassai")

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
MAX_INPUT_CHARS = int(os.getenv("MAX_INPUT_CHARS", "10000"))
MAX_RETRIES = int(os.getenv("MAX_RETRIES", "2"))

DEFAULT_SYSTEM_PROMPT = """You are an expert human writer who specializes in rewriting AI-generated text to sound natural, organic, and indistinguishable from human-written content.

CORE REQUIREMENTS (STRICTLY FOLLOW THESE RULES):
1. MEANING PRESERVATION: Keep the original meaning, facts, and core information completely unchanged. Do not add new information or remove key facts.

2. LENGTH CONTROL: The output word count must stay within ±20% of the original text. NEVER expand short sentences into long paragraphs. NEVER pad content. If the input is a single sentence, output a single sentence of similar length.

3. STRUCTURE INTEGRITY: Maintain the original text structure and paragraph layout. If the input has N sentences, output should have roughly N sentences (±1). Do not turn a single sentence into a whole paragraph.

4. HUMANNESS ENHANCEMENT:
   - Vary sentence lengths naturally (mix short and long sentences)
   - Use idioms, colloquial expressions, and conversational tone where appropriate
   - Introduce natural perplexity and burstiness
   - Avoid repetitive sentence patterns (avoid: "Furthermore", "In conclusion", "However", etc.)
   - Add minor "imperfections" that real humans make (contractions, slightly varied wording)

5. STYLE FIDELITY: Preserve the original writing style (academic stays academic, casual stays casual, technical stays technical).

6. ZERO AI DETECTION: The output must easily bypass all AI detectors including GPTZero, Turnitin, Originality.ai, and others.

Directly output the rewritten text only, no explanations, no comments, no markdown formatting."""

SHORT_TEXT_PROMPT_SUFFIX = """

CRITICAL OVERRIDE FOR SHORT TEXT: The input is very short (under 30 words). You MUST output approximately the same number of words (within ±30%). Do NOT add context, examples, or elaboration. Rewrite the single sentence as a single sentence. No padding."""

SYSTEM_PROMPT = os.getenv("SYSTEM_PROMPT", DEFAULT_SYSTEM_PROMPT)

class TextRequest(BaseModel):
    text: str

    @field_validator("text")
    @classmethod
    def validate_text(cls, v):
        v = v.strip()
        if not v:
            raise ValueError("Input text cannot be empty")
        if len(v) > MAX_INPUT_CHARS:
            raise ValueError(f"Input exceeds maximum length of {MAX_INPUT_CHARS} characters")
        return v


def count_words(text: str) -> int:
    return len(text.split())


def is_short_text(text: str) -> bool:
    return count_words(text) < 30


def call_llm(text: str, use_short_prompt: bool) -> str:
    prompt = SYSTEM_PROMPT
    if use_short_prompt:
        prompt = SYSTEM_PROMPT + SHORT_TEXT_PROMPT_SUFFIX

    payload = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": prompt},
            {"role": "user", "content": text}
        ],
        "stream": False,
        "temperature": 0.85,
        "top_p": 0.9,
        "max_tokens": min(count_words(text) * 3, 2048)
    }

    headers = {
        "Authorization": f"Bearer {SILICONFLOW_API_KEY}",
        "Content-Type": "application/json"
    }

    response = requests.post(SILICONFLOW_URL, json=payload, headers=headers, timeout=90)
    response_data = response.json()

    if response.status_code != 200:
        error_msg = response_data.get("message", "API request failed")
        logger.error(f"LLM API error: {response.status_code} - {error_msg}")
        raise HTTPException(status_code=response.status_code, detail=error_msg)

    return response_data["choices"][0]["message"]["content"].strip()


def humanize_with_retry(text: str) -> str:
    short = is_short_text(text)
    input_words = count_words(text)
    logger.info(f"Processing: {input_words} words, short_text={short}")

    for attempt in range(MAX_RETRIES + 1):
        try:
            result = call_llm(text, use_short_prompt=short)
            output_words = count_words(result)

            if input_words > 0:
                ratio = output_words / input_words
                max_ratio = 1.8 if short else 1.5
                min_ratio = 0.5

                if ratio > max_ratio or ratio < min_ratio:
                    logger.warning(
                        f"Attempt {attempt+1}: length ratio {ratio:.2f} out of range "
                        f"[{min_ratio}, {max_ratio}] (in={input_words}, out={output_words})"
                    )
                    if attempt < MAX_RETRIES:
                        time.sleep(0.5)
                        continue

                logger.info(f"Success: ratio={ratio:.2f} (in={input_words}, out={output_words})")
            return result

        except HTTPException:
            raise
        except requests.exceptions.Timeout:
            logger.error(f"Attempt {attempt+1}: timeout")
            if attempt < MAX_RETRIES:
                time.sleep(1)
                continue
            raise HTTPException(status_code=504, detail="Request timed out. Please try with shorter text.")
        except requests.exceptions.ConnectionError:
            logger.error(f"Attempt {attempt+1}: connection error")
            if attempt < MAX_RETRIES:
                time.sleep(1)
                continue
            raise HTTPException(status_code=503, detail="Cannot connect to AI service. Please try again later.")
        except Exception as e:
            logger.error(f"Attempt {attempt+1}: {str(e)}")
            if attempt < MAX_RETRIES:
                time.sleep(0.5)
                continue
            raise HTTPException(status_code=500, detail=str(e))

    return result


@app.post("/api/humanize")
async def humanize_text(request: TextRequest):
    if not SILICONFLOW_API_KEY:
        raise HTTPException(status_code=500, detail="API Key not configured")

    result_text = humanize_with_retry(request.text)
    return {"success": True, "data": result_text}


@app.get("/")
async def health_check():
    return {
        "status": "ok",
        "service": "BypassAI API",
        "model": MODEL_NAME,
        "prompt_length": len(SYSTEM_PROMPT),
        "max_input_chars": MAX_INPUT_CHARS
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
