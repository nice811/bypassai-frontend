import requests
import os
import json

API_TOKEN = os.environ.get("CLOUDFLARE_API_TOKEN")
ACCOUNT_ID = "dac1a974161f964da72fde126912a930"
PROJECT_NAME = "bypassai-frontend"

if not API_TOKEN:
    print("请设置 CLOUDFLARE_API_TOKEN 环境变量")
    print("获取地址: https://dash.cloudflare.com/profile/api-tokens")
    print("需要的权限: Pages:Edit")
    exit(1)

headers = {
    "Authorization": f"Bearer {API_TOKEN}",
    "Content-Type": "application/json"
}

print("1. 创建 Pages 项目...")
create_url = f"https://api.cloudflare.com/client/v4/accounts/{ACCOUNT_ID}/pages/projects"
create_data = {
    "name": PROJECT_NAME,
    "production_branch": "main",
    "framework": "static"
}
response = requests.post(create_url, headers=headers, json=create_data)
print(f"创建项目状态: {response.status_code}")
if response.status_code == 409:
    print("项目已存在，继续部署...")
elif response.status_code != 200:
    print(f"创建失败: {response.text}")
    exit(1)

print("\n2. 创建部署上传 URL...")
upload_url = f"https://api.cloudflare.com/client/v4/accounts/{ACCOUNT_ID}/pages/projects/{PROJECT_NAME}/deployments"
upload_data = {
    "branch": "main",
    "commit_message": "Deploy frontend static files",
    "commit_hash": "manual-deploy"
}
response = requests.post(upload_url, headers=headers, json=upload_data)
if response.status_code != 200:
    print(f"创建部署失败: {response.text}")
    exit(1)

result = response.json()
upload_url = result["result"]["upload_url"]["url"]
deploy_id = result["result"]["id"]
print(f"上传 URL: {upload_url}")
print(f"部署 ID: {deploy_id}")

print("\n3. 上传文件...")
files = {}
html_files = [f for f in os.listdir(".") if f.endswith(".html")]
other_files = ["robots.txt", "sitemap.xml"]

for filename in html_files + other_files:
    if os.path.exists(filename):
        files[filename] = open(filename, "rb")

response = requests.put(upload_url, files=files)
print(f"上传状态: {response.status_code}")
if response.status_code != 200:
    print(f"上传失败: {response.text}")
    exit(1)

print("\n4. 确认部署...")
confirm_url = f"https://api.cloudflare.com/client/v4/accounts/{ACCOUNT_ID}/pages/projects/{PROJECT_NAME}/deployments/{deploy_id}/uploaded"
response = requests.post(confirm_url, headers=headers)
print(f"确认状态: {response.status_code}")
if response.status_code != 200:
    print(f"确认失败: {response.text}")
    exit(1)

print("\n✅ 部署完成！")
print(f"项目地址: https://{PROJECT_NAME}.pages.dev")
