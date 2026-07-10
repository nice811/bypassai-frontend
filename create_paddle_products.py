import requests

API_KEY = "434jt541vmvhrnyv7gykbwvzn4xwpk3jzmsszgrtrsj2pt96hr"
VENDOR_ID = "85548"
BASE_URL = "https://api.sandbox.paddle.com"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

products = [
    {
        "name": "Starter",
        "description": "基础版 - 适合个人用户",
        "price": 10.00,
        "trial_days": 7
    },
    {
        "name": "Pro",
        "description": "专业版 - 适合专业用户",
        "price": 40.00,
        "trial_days": 7
    },
    {
        "name": "Advanced",
        "description": "高级版 - 适合企业用户",
        "price": 120.00,
        "trial_days": 7
    }
]

product_ids = {}

for product in products:
    print(f"\n=== 创建产品: {product['name']} ===")
    
    create_product_response = requests.post(
        f"{BASE_URL}/products",
        headers=headers,
        json={
            "name": product["name"],
            "description": product["description"],
            "tax_category": "saas"
        }
    )
    
    if create_product_response.status_code == 201:
        product_data = create_product_response.json()
        product_id = product_data["data"]["id"]
        print(f"产品创建成功！Product ID: {product_id}")
        
        create_price_response = requests.post(
            f"{BASE_URL}/prices",
            headers=headers,
            json={
                "product_id": product_id,
                "currency_code": "USD",
                "amount": int(product["price"] * 100),
                "recurring_period": "month",
                "trial_period": f"{product['trial_days']}day"
            }
        )
        
        if create_price_response.status_code == 201:
            price_data = create_price_response.json()
            price_id = price_data["data"]["id"]
            print(f"价格创建成功！Price ID: {price_id}")
            product_ids[product["name"]] = {
                "product_id": product_id,
                "price_id": price_id
            }
        else:
            print(f"价格创建失败: {create_price_response.text}")
    else:
        print(f"产品创建失败: {create_product_response.text}")

print("\n=== 创建结果汇总 ===")
for name, ids in product_ids.items():
    print(f"{name}:")
    print(f"  Product ID: {ids['product_id']}")
    print(f"  Price ID: {ids['price_id']}")
