import os
import logging
import re
import uuid
import hashlib
from datetime import datetime, timedelta
from fastapi import FastAPI, HTTPException, Request
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
    allow_credentials=True,
    allow_methods=["POST", "OPTIONS", "GET"],
    allow_headers=["Content-Type", "Authorization"],
)

SILICONFLOW_API_KEY = os.getenv("SILICONFLOW_API_KEY", "")
SILICONFLOW_URL = "https://api.siliconflow.cn/v1/chat/completions"
MODEL_NAME = os.getenv("MODEL_NAME", "deepseek-ai/DeepSeek-V3")
MAX_INPUT_CHARS = int(os.getenv("MAX_INPUT_CHARS", "10000"))

PADDLE_API_KEY = os.getenv("PADDLE_API_KEY", "")
PADDLE_CLIENT_TOKEN = os.getenv("PADDLE_CLIENT_TOKEN", "")
PADDLE_WEBHOOK_SECRET = os.getenv("PADDLE_WEBHOOK_SECRET", "")
PADDLE_API_BASE = "https://api.sandbox.paddle.com"

PRICING_PLAN = {
    "starter": {
        "id": "pri_01kx4wv5dhnyt6agz60yaq745b",
        "name": "Starter",
        "price": 10,
        "currency": "USD",
        "description": "基础版 - 适合个人用户",
        "features": ["每月 50 次转换", "标准处理速度", "基础支持"],
        "monthly_limit": 50
    },
    "pro": {
        "id": "pri_01kx4wzvrsqx17grb62j41ab1e",
        "name": "Pro",
        "price": 40,
        "currency": "USD",
        "description": "专业版 - 适合学生和专业人士",
        "features": ["每月 500 次转换", "快速处理速度", "优先支持", "历史记录"],
        "monthly_limit": 500
    },
    "advanced": {
        "id": "pri_01kx4x4me2tgcbprgrm604g0kk",
        "name": "Advanced",
        "price": 120,
        "currency": "USD",
        "description": "高级版 - 适合团队和企业",
        "features": ["无限转换", "极速处理", "专属支持", "API 访问", "团队协作"],
        "monthly_limit": None
    }
}

USER_STORAGE = {}
SESSION_STORAGE = {}

def generate_session_token(user_id):
    token = str(uuid.uuid4())
    SESSION_STORAGE[token] = {
        "user_id": user_id,
        "created_at": datetime.now(),
        "expires_at": datetime.now() + timedelta(days=7)
    }
    return token

def get_user_by_session(token):
    if token not in SESSION_STORAGE:
        return None
    session = SESSION_STORAGE[token]
    if datetime.now() > session["expires_at"]:
        del SESSION_STORAGE[token]
        return None
    return USER_STORAGE.get(session["user_id"])

def create_or_update_user(email, plan_key=None):
    user_id = hashlib.md5(email.encode()).hexdigest()
    if user_id not in USER_STORAGE:
        USER_STORAGE[user_id] = {
            "id": user_id,
            "email": email,
            "plan": plan_key or "free",
            "monthly_limit": PRICING_PLAN.get(plan_key, {}).get("monthly_limit", 5),
            "used_this_month": 0,
            "last_reset": datetime.now(),
            "created_at": datetime.now(),
            "subscription_id": None,
            "trial_used": False
        }
    elif plan_key and plan_key != USER_STORAGE[user_id]["plan"]:
        USER_STORAGE[user_id]["plan"] = plan_key
        USER_STORAGE[user_id]["monthly_limit"] = PRICING_PLAN.get(plan_key, {}).get("monthly_limit", 5)
        USER_STORAGE[user_id]["used_this_month"] = 0
    return USER_STORAGE[user_id]

def reset_monthly_quota(user):
    now = datetime.now()
    if now.month != user["last_reset"].month or now.year != user["last_reset"].year:
        user["used_this_month"] = 0
        user["last_reset"] = now
    return user

def check_quota(user):
    user = reset_monthly_quota(user)
    if user["monthly_limit"] is None:
        return True, "unlimited"
    if user["used_this_month"] < user["monthly_limit"]:
        return True, f"{user['used_this_month']}/{user['monthly_limit']}"
    return False, f"{user['used_this_month']}/{user['monthly_limit']}"

def consume_quota(user):
    user = reset_monthly_quota(user)
    if user["monthly_limit"] is not None:
        user["used_this_month"] += 1
    return user

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
    stream: bool = False

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
async def humanize_text(request: TextRequest, token: str = None):
    if not SILICONFLOW_API_KEY:
        raise HTTPException(status_code=500, detail="未配置后端 SILICONFLOW_API_KEY 环境变量")

    user = None
    if token:
        user = get_user_by_session(token)
        if not user:
            raise HTTPException(status_code=401, detail="Invalid or expired session token")

    if user:
        allowed, quota_info = check_quota(user)
        if not allowed:
            raise HTTPException(status_code=429, detail=f"配额已用完！当前使用: {quota_info}")
    else:
        user = create_or_update_user("anonymous@example.com")
        allowed, quota_info = check_quota(user)
        if not allowed:
            raise HTTPException(status_code=429, detail=f"免费配额已用完！请升级订阅。当前使用: {quota_info}")

    short = is_short_text(request.text)
    logger.info(f"Request: user={user['email']}, plan={user['plan']}, quota={quota_info}, length={count_length(request.text)}, short={short}, stream={request.stream}")

    if request.stream:
        async def stream_with_quota():
            async for chunk_msg in llm_stream_generator(request.text, use_short_prompt=short):
                yield chunk_msg
            consume_quota(user)
            logger.info(f"Quota consumed: {user['used_this_month']}/{user['monthly_limit']}")
        return StreamingResponse(stream_with_quota(), media_type="text/event-stream")
    else:
        full_text = ""
        async for chunk_msg in llm_stream_generator(request.text, use_short_prompt=short):
            if "chunk" in chunk_msg:
                try:
                    line_data = json.loads(chunk_msg.replace("data: ", "").strip())
                    full_text += line_data.get("chunk", "")
                except:
                    pass
        consume_quota(user)
        logger.info(f"Quota consumed: {user['used_this_month']}/{user['monthly_limit']}")
        return {"success": True, "data": full_text.strip(), "quota": quota_info}


class LoginRequest(BaseModel):
    email: str

@app.post("/api/login")
async def login(request: LoginRequest):
    user = create_or_update_user(request.email)
    token = generate_session_token(user["id"])
    return {
        "success": True,
        "token": token,
        "user": {
            "email": user["email"],
            "plan": user["plan"],
            "quota": f"{user['used_this_month']}/{user['monthly_limit']}" if user["monthly_limit"] else "unlimited"
        }
    }

@app.get("/api/user")
async def get_user(token: str):
    user = get_user_by_session(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return {
        "success": True,
        "user": {
            "email": user["email"],
            "plan": user["plan"],
            "quota": f"{user['used_this_month']}/{user['monthly_limit']}" if user["monthly_limit"] else "unlimited"
        }
    }

@app.get("/api/plans")
async def get_plans():
    return {
        "success": True,
        "data": PRICING_PLAN,
        "paddle_client_token": PADDLE_CLIENT_TOKEN
    }


@app.post("/api/webhook/paddle")
async def paddle_webhook(request: Request):
    try:
        raw_body = await request.body()
        signature = request.headers.get("paddle-signature", "")
        
        logger.info(f"Paddle webhook received: {signature[:20]}...")
        
        try:
            webhook_data = json.loads(raw_body.decode("utf-8"))
            event_type = webhook_data.get("event_type", "")
            
            logger.info(f"Webhook event type: {event_type}")
            
            if event_type in ["subscription.created", "subscription.updated"]:
                data = webhook_data.get("data", {})
                customer_email = data.get("customer", {}).get("email", "")
                price_id = data.get("price", {}).get("id", "")
                
                logger.info(f"Payment success - email: {customer_email}, price_id: {price_id}")
                
                plan_key = None
                for key, plan in PRICING_PLAN.items():
                    if plan["id"] == price_id:
                        plan_key = key
                        break
                
                if plan_key and customer_email:
                    user = create_or_update_user(customer_email, plan_key)
                    user["subscription_id"] = data.get("id", "")
                    user["trial_used"] = True
                    logger.info(f"User upgraded: {customer_email} -> {plan_key} ({user['monthly_limit']} credits)")
                    
                    return {"success": True, "message": f"User {customer_email} upgraded to {plan_key}"}
                else:
                    logger.warning(f"Could not find plan for price_id: {price_id}")
                    return {"success": True, "message": "Plan not found"}
            else:
                logger.info(f"Ignoring event type: {event_type}")
                return {"success": True, "message": f"Ignored: {event_type}"}
        
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {str(e)}")
            logger.info(f"Raw body: {raw_body[:500]}")
        
        return {"success": True}
    except Exception as e:
        logger.error(f"Webhook error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/")
async def health_check():
    return {
        "status": "ok",
        "service": "BypassAI Advanced API",
        "model": MODEL_NAME,
        "config": {
            "max_input_chars": MAX_INPUT_CHARS,
            "api_key_configured": bool(SILICONFLOW_API_KEY),
            "payment_configured": bool(PADDLE_CLIENT_TOKEN)
        }
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
