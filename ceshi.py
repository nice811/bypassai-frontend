import requests

# 你的测试模式 API 密钥
API_KEY = "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJhdWQiOiI5NGQ1OWNlZi1kYmI4LTRlYTUtYjE3OC1kMjU0MGZjZDY5MTkiLCJqdGkiOiIyZGRhMGQ1ZTUxNTRjMDY2ODAyNGRhZGIxMDQxNGE2NjNhZTM1YjA1NTJhZjQ3NWY0MTIxYTE0ZTlhMDU1NDM5MmEwNmZjNGJjYTVhMGRiNCIsImlhdCI6MTc4MzU5NDc0My41Nzk3MDYsIm5iZiI6MTc4MzU5NDc0My41Nzk3MDksImV4cCI6MTc5OTQ1MjgwMC4wNjIxODQsInN1YiI6Ijc1NTE5MDEiLCJzY29wZXMiOltdfQ.pshVokqI4r7WeqkgvBJ_6jCAzWVz6cc1U4yWr6KdkAADzHmxNlHqBzLGkXtbNBoqGNOkM249zrMcwFDYaIA3Xu_15VcDhAm4uVuldpRytJEohB4awPBrkuXwdR5-SX5VJrsfTOEr-kuouSPrQLHTNFMX-r7zvaPV68vy9U2EVk65xvveH7hAUGBuHd-MBYheG1jHIVkqRKDBN8U5NNsrTtK8DMZljzMQRkHDw7jsMBV66pC2oD_DbV82tkzmc3n9jmnIqWOufYRRqHQAoDHOQpDm0D24FPPeQfLMBAD7PLEL30MWM7D4Otm6hRWcRZc6hDQVCsW8l-eiIGwwGEzoftPxPS60n5WAIz7Cnb6jSJCavqNFDRY7YnLjTGJzjbgx_k7IYOoy919RQHeMsNQjyiwLKLywZg9q3apnt9Fha4_L0MI_dMiTScQT0h6-3KG9_6RhuNmKnA6CPFL4yoBZ-W7F-fJTOl04BzNN3H5ey_AAguFR7j2v8S8Y5XkQHJUg5MIhaqs6_xp-spNWlq5i51mHrU9PyWTHVZs6sm8JZ6iiWKtKOsTqzcSBTEzFjOrF7V3cc7HuzwiGOxoMpJRDf9x_sjkJlPexOZ_yohM0SvwT9kLHuAFoIMmeYInOnWQSgmTiT4QoS8_MENE1UM1PZLLbNafXp-GsgMDSF5Jk7DU"

headers = {
    "Accept": "application/vnd.api+json",
    "Content-Type": "application/vnd.api+json",
    "Authorization": f"Bearer {API_KEY}"
}

# 1. 先用 API 获取你的商店 ID (Store ID)
print("正在获取您的商店信息...")
store_url = "https://api.lemonsqueezy.com/v1/stores"
store_response = requests.get(store_url, headers=headers)

if store_response.status_code != 200:
    print(f"❌ 获取商店失败，错误码: {store_response.status_code}")
    print(store_response.text)
    exit()

stores_data = store_response.json().get("data", [])
if not stores_data:
    print("❌ 未找到任何商店信息，请确认密钥是否正确。")
    exit()

store_id = stores_data[0]["id"]
store_name = stores_data[0]["attributes"]["name"]
print(f"🟢 成功连接商店: {store_name} (ID: {store_id})")

# 2. 强行创建产品
print("\n正在通过 API 强行创建测试产品...")
product_url = "https://api.lemonsqueezy.com/v1/products"
product_payload = {
    "data": {
        "type": "products",
        "attributes": {
            "name": "BypassAI 积分充值 (测试)",
            "description": "用于测试海外支付流自动挂机的产品",
            "price": 1000,  # 10.00 美元 (单位是分)
            "price_type": "one_time"
        },
        "relationships": {
            "store": {
                "data": {
                    "type": "stores",
                    "id": str(store_id)
                }
            }
        }
    }
}

product_response = requests.post(product_url, headers=headers, json=product_payload)

if product_response.status_code in [200, 201]:
    print("🎉 奇迹出现！产品强行创建成功！")
    product_data = product_response.json()["data"]
    print(f"产品名称: {product_data['attributes']['name']}")
    print(f"产品 ID: {product_data['id']}")
    print("\n请回到网页端刷新‘产品 (Products)’页面看看是不是已经冒出来了！")
else:
    print(f"❌ 强行创建产品失败，错误码: {product_response.status_code}")
    print("看看服务器吐出了什么错误：")
    print(product_response.text)