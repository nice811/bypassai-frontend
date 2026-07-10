import requests

API_KEY = "434jt541vmvhrnyv7gykbwvzn4xwpk3jzmsszgrtrsj2pt96hr"
BASE_URL = "https://sandbox-api.paddle.com"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

print("=== 测试获取产品列表 ===")
try:
    response = requests.get(f"{BASE_URL}/products", headers=headers, timeout=30)
    print(f"状态码: {response.status_code}")
    print(f"响应: {response.text[:1000]}")
except Exception as e:
    print(f"错误: {e}")

print("\n=== 测试获取价格列表 ===")
try:
    response = requests.get(f"{BASE_URL}/prices", headers=headers, timeout=30)
    print(f"状态码: {response.status_code}")
    print(f"响应: {response.text[:1000]}")
except Exception as e:
    print(f"错误: {e}")
