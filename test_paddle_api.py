import requests
import time

API_KEY = "434jt541vmvhrnyv7gykbwvzn4xwpk3jzmsszgrtrsj2pt96hr"

endpoints = [
    "https://api.sandbox.paddle.com/prices",
    "https://api.sandbox.paddle.com/v3/prices",
    "https://sandbox-api.paddle.com/prices",
    "https://sandbox-api.paddle.com/v3/prices",
]

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

for url in endpoints:
    print(f"\n测试: {url}")
    try:
        response = requests.get(url, headers=headers, timeout=15)
        print(f"  状态码: {response.status_code}")
        print(f"  响应前200字符: {response.text[:200]}")
    except Exception as e:
        print(f"  错误: {type(e).__name__}: {str(e)[:100]}")
