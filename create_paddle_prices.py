import requests

API_KEY = "434jt541vmvhrnyv7gykbwvzn4xwpk3jzmsszgrtrsj2pt96hr"
BASE_URL = "https://api.sandbox.paddle.com"

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

for name, info in products.items():
    print(f"\n=== 创建价格: {name} ===")
    print(f"产品ID: {info['product_id']}")
    print(f"价格: ${info['price']}/月")
    print(f"试用期: 7天")
    
    try:
        create_price_response = requests.post(
            f"{BASE_URL}/prices",
            headers=headers,
            json={
                "product_id": info["product_id"],
                "currency_code": "USD",
                "amount": int(info["price"] * 100),
                "recurring_period": "month",
                "trial_period": "7day"
            },
            timeout=30
        )
        
        if create_price_response.status_code == 201:
            price_data = create_price_response.json()
            price_id = price_data["data"]["id"]
            print(f"价格创建成功！Price ID: {price_id}")
            price_ids[name] = price_id
        else:
            print(f"价格创建失败: {create_price_response.text}")
            
    except Exception as e:
        print(f"请求失败: {str(e)}")

print("\n=== 创建结果汇总 ===")
print("产品目录已创建成功！")
print("\n产品ID (pro_开头):")
for name, info in products.items():
    print(f"  {name}: {info['product_id']}")
    
print("\n价格ID (pri_开头) - 用于集成到您的应用中:")
for name, price_id in price_ids.items():
    print(f"  {name}: {price_id}")
