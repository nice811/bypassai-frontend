import requests
import time

API_KEY = "434jt541vmvhrnyv7gykbwvzn4xwpk3jzmsszgrtrsj2pt96hr"
BASE_URL = "https://sandbox-api.paddle.com"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

products = {
    "Starter": {
        "product_id": "pro_01kx4twzvgy988dk6c9hnb6397",
        "price": 10.00
    },
    "Pro": {
        "product_id": "pro_01kx4tz71pk888genwkyrzpt25",
        "price": 40.00
    },
    "Advanced": {
        "product_id": "pro_01kx4v0qq8zxh349qebpw4d37e",
        "price": 120.00
    }
}

price_ids = {}

def create_price_with_retry(name, product_id, price_amount, max_retries=8):
    for attempt in range(1, max_retries + 1):
        print(f"  第 {attempt}/{max_retries} 次尝试...")
        try:
            response = requests.post(
                f"{BASE_URL}/prices",
                headers=headers,
                json={
                    "product_id": product_id,
                    "currency_code": "USD",
                    "amount": int(price_amount * 100),
                    "recurring_period": "month",
                    "trial_period": "7day"
                },
                timeout=30
            )
            
            print(f"  状态码: {response.status_code}")
            if response.status_code in [200, 201]:
                data = response.json()
                price_id = data["data"]["id"]
                print(f"  价格创建成功！Price ID: {price_id}")
                return price_id
            else:
                print(f"  响应: {response.text[:500]}")
                
        except Exception as e:
            print(f"  请求失败: {type(e).__name__}: {str(e)[:100]}")
        
        if attempt < max_retries:
            wait_time = attempt * 2
            print(f"  等待 {wait_time} 秒后重试...")
            time.sleep(wait_time)
    
    return None

for name, info in products.items():
    print(f"\n=== 创建价格: {name} ===")
    print(f"产品ID: {info['product_id']}")
    print(f"价格: ${info['price']}/月")
    print(f"试用期: 7天")
    
    price_id = create_price_with_retry(name, info["product_id"], info["price"])
    if price_id:
        price_ids[name] = price_id
    else:
        print(f"  {name} 价格创建失败，已用尽重试次数")

print("\n" + "="*50)
print("创建结果汇总")
print("="*50)
print("\n产品ID (pro_开头):")
for name, info in products.items():
    print(f"  {name}: {info['product_id']}")
    
print("\n价格ID (pri_开头):")
for name in products.keys():
    if name in price_ids:
        print(f"  {name}: {price_ids[name]}")
    else:
        print(f"  {name}: 创建失败")
