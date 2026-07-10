import requests
import json

PADDLE_API_KEY = "434jt541vmvhrnyv7gykbwvzn4xwpk3jzmsszgrtrsj2pt96hr"
PADDLE_API_BASE = "https://api.sandbox.paddle.com"

headers = {
    "Authorization": f"Bearer {PADDLE_API_KEY}",
    "Content-Type": "application/json"
}

def test_list_prices():
    print("\n=== 1. 获取所有价格列表 ===")
    try:
        r = requests.get(f"{PADDLE_API_BASE}/v3/prices", headers=headers)
        print(f"状态码: {r.status_code}")
        result = r.json()
        print(f"价格数量: {len(result.get('data', []))}")
        for price in result.get("data", []):
            print(f"  - {price.get('id')}: ${price.get('unit_price', {}).get('amount', 0)} {price.get('unit_price', {}).get('currency_code')}")
        return result.get("data", [])
    except Exception as e:
        print(f"错误: {e}")
        return []

def test_create_customer():
    print("\n=== 2. 创建测试客户 ===")
    try:
        data = {
            "email": f"test_customer_{int(time.time())}@example.com",
            "name": "Test Customer"
        }
        r = requests.post(f"{PADDLE_API_BASE}/v3/customers", headers=headers, json=data)
        print(f"状态码: {r.status_code}")
        result = r.json()
        print(f"客户ID: {result.get('data', {}).get('id')}")
        print(f"客户邮箱: {result.get('data', {}).get('email')}")
        return result.get("data", {})
    except Exception as e:
        print(f"错误: {e}")
        return {}

def test_create_subscription(customer_id, price_id):
    print("\n=== 3. 创建订阅 ===")
    try:
        data = {
            "customer_id": customer_id,
            "items": [
                {
                    "price_id": price_id,
                    "quantity": 1
                }
            ]
        }
        r = requests.post(f"{PADDLE_API_BASE}/v3/subscriptions", headers=headers, json=data)
        print(f"状态码: {r.status_code}")
        result = r.json()
        if r.status_code == 200:
            print(f"订阅ID: {result.get('data', {}).get('id')}")
            print(f"状态: {result.get('data', {}).get('status')}")
            print(f"价格: {result.get('data', {}).get('items', [{}])[0].get('price', {}).get('id')}")
            return result.get("data", {})
        else:
            print(f"错误信息: {result}")
            return {}
    except Exception as e:
        print(f"错误: {e}")
        return {}

def test_list_subscriptions():
    print("\n=== 4. 获取订阅列表 ===")
    try:
        r = requests.get(f"{PADDLE_API_BASE}/v3/subscriptions", headers=headers)
        print(f"状态码: {r.status_code}")
        result = r.json()
        print(f"订阅数量: {len(result.get('data', []))}")
        for sub in result.get("data", []):
            print(f"  - {sub.get('id')}: {sub.get('status')}")
        return result.get("data", [])
    except Exception as e:
        print(f"错误: {e}")
        return []

if __name__ == "__main__":
    import time
    
    prices = test_list_prices()
    if prices:
        starter_price = prices[0]["id"] if len(prices) > 0 else None
        print(f"\n使用价格ID: {starter_price}")
        
        customer = test_create_customer()
        if customer:
            subscription = test_create_subscription(customer["id"], starter_price)
            
        test_list_subscriptions()
        
        print("\n✅ 真实订阅创建测试完成！")
        print("现在可以在 Paddle 沙盒后台看到这条订阅记录了。")