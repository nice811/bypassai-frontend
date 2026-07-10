import os

PAGES_DIR = "."
HTML_FILES = [
    "bypass-turnitin-ai-detection-free.html",
    "make-chatgpt-text-sound-human.html", 
    "free-ai-rewriter-for-college-essays.html",
    "undetectable-ai-website-for-students.html",
    "convert-chatgpt-to-human-text-online.html",
    "how-to-not-get-caught-using-chatgpt.html",
    "best-ai-humanizer-tool-2026.html",
    "remove-ai-plagiarism-from-essay.html",
    "make-ai-text-untraceable-free.html",
    "bypass-canvas-ai-detector-tips.html"
]

SUBSCRIPTION_SECTION = """
    <div style="margin-top: 40px; text-align: center;">
        <p style="color: #4b5563; margin-bottom: 15px;">Need more conversions? Upgrade to a premium plan!</p>
        <a href="/" style="background: #4f46e5; color: white; padding: 12px 30px; border-radius: 8px; font-weight: 600; text-decoration: none;">View Pricing Plans</a>
    </div>
"""

API_URL = "https://bypassai-api-production.up.railway.app/api/humanize"

for filename in HTML_FILES:
    filepath = os.path.join(PAGES_DIR, filename)
    if not os.path.exists(filepath):
        print(f"跳过: {filename} (不存在)")
        continue
    
    print(f"处理: {filename}")
    
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    
    if SUBSCRIPTION_SECTION.strip() in content:
        print(f"  已包含订阅部分，跳过")
        continue
    
    content = content.replace('    <footer>', SUBSCRIPTION_SECTION + '\n    <footer>')
    
    content = content.replace(
        "const API_URL = 'https://bypassai-api-production.up.railway.app/api/humanize';",
        "const API_URL = '" + API_URL + "';"
    )
    
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    
    print(f"  更新完成")

print("\n所有页面更新完成！")