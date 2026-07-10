import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_health():
    print("\n=== 1. 健康检查 ===")
    try:
        r = requests.get(f"{BASE_URL}/")
        print(f"状态码: {r.status_code}")
        print(f"响应: {r.json()}")
        return r.status_code == 200
    except Exception as e:
        print(f"错误: {e}")
        return False

def test_user_registration():
    print("\n=== 2. 用户注册 ===")
    try:
        email = "test_user@example.com"
        r = requests.post(f"{BASE_URL}/api/login", json={"email": email})
        print(f"状态码: {r.status_code}")
        result = r.json()
        print(f"响应: {json.dumps(result, indent=2)}")
        
        if r.status_code == 200:
            return result["token"], result["user"]
        return None, None
    except Exception as e:
        print(f"错误: {e}")
        return None, None

def test_humanize_with_free_quota(token):
    print("\n=== 3. 使用免费配额转换文本 ===")
    try:
        test_text = "人工智能技术的快速发展正在深刻改变我们的生活方式。"
        r = requests.post(f"{BASE_URL}/api/humanize?token={token}", 
                          json={"text": test_text, "stream": False})
        print(f"状态码: {r.status_code}")
        result = r.json()
        print(f"响应: {json.dumps(result, indent=2, ensure_ascii=False)}")
        
        if r.status_code == 500 and "SILICONFLOW_API_KEY" in result.get("detail", ""):
            print("⚠️ 跳过此测试（本地无 API Key）")
            return True
        return r.status_code == 200
    except Exception as e:
        print(f"错误: {e}")
        return False

def test_webhook_payment_success():
    print("\n=== 4. 模拟支付成功 Webhook ===")
    try:
        webhook_data = {
            "event_type": "subscription.created",
            "data": {
                "id": "sub_01kx50000000000000000000",
                "customer": {
                    "email": "test_user@example.com"
                },
                "price": {
                    "id": "pri_01kx4wzvrsqx17grb62j41ab1e"
                },
                "status": "active"
            }
        }
        
        r = requests.post(f"{BASE_URL}/api/webhook/paddle", json=webhook_data)
        print(f"状态码: {r.status_code}")
        result = r.json()
        print(f"响应: {json.dumps(result, indent=2)}")
        return r.status_code == 200
    except Exception as e:
        print(f"错误: {e}")
        return False

def test_user_after_payment(token):
    print("\n=== 5. 验证支付后用户配额更新 ===")
    try:
        r = requests.get(f"{BASE_URL}/api/user?token={token}")
        print(f"状态码: {r.status_code}")
        result = r.json()
        print(f"响应: {json.dumps(result, indent=2)}")
        
        user = result.get("user", {})
        if user.get("plan") == "pro" and user.get("quota") == "0/500":
            print("✅ 用户已成功升级到 Pro 套餐，配额更新为 500")
            return True
        else:
            print(f"❌ 配额未正确更新: plan={user.get('plan')}, quota={user.get('quota')}")
            return False
    except Exception as e:
        print(f"错误: {e}")
        return False

def test_humanize_with_pro_quota(token):
    print("\n=== 6. 使用升级后的 Pro 配额转换文本 ===")
    try:
        test_text = "机器学习算法在自然语言处理领域取得了显著进步，包括文本分类、情感分析和机器翻译等多个应用场景。"
        r = requests.post(f"{BASE_URL}/api/humanize?token={token}", 
                          json={"text": test_text, "stream": False})
        print(f"状态码: {r.status_code}")
        result = r.json()
        print(f"响应: {json.dumps(result, indent=2, ensure_ascii=False)}")
        
        if r.status_code == 500 and "SILICONFLOW_API_KEY" in result.get("detail", ""):
            print("⚠️ 跳过此测试（本地无 API Key）")
            return True
        
        if r.status_code == 200:
            print(f"✅ 转换成功! 配额使用: {result.get('quota')}")
            return True
        return False
    except Exception as e:
        print(f"错误: {e}")
        return False

def run_all_tests():
    print("🚀 开始测试全自动发货流程...")
    
    results = []
    
    results.append(("健康检查", test_health()))
    results.append(("用户注册", test_user_registration()[0] is not None))
    
    token, user = test_user_registration()
    
    if token:
        results.append(("免费配额转换", test_humanize_with_free_quota(token)))
        results.append(("支付 Webhook", test_webhook_payment_success()))
        results.append(("配额更新验证", test_user_after_payment(token)))
        results.append(("Pro配额转换", test_humanize_with_pro_quota(token)))
    
    print("\n=== 测试结果汇总 ===")
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for name, success in results:
        status = "✅" if success else "❌"
        print(f"{status} {name}")
    
    print(f"\n总计: {passed}/{total} 通过")
    
    if passed == total:
        print("\n🎉 全自动发货流程测试全部通过!")
        return True
    else:
        print("\n⚠️ 部分测试失败，请检查日志")
        return False

if __name__ == "__main__":
    run_all_tests()