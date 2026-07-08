import os

BASE_URL = "https://your-domain.com"
API_BASE_URL = "https://your-api.onrender.com"

seo_keywords = [
    {"slug": "bypass-turnitin-ai-detection-free", "title": "Bypass Turnitin AI Detection Freely - 100% Undetectable", "desc": "Learn how to bypass Turnitin AI detection for free. Convert AI-generated essays to human-readable content instantly."},
    {"slug": "make-chatgpt-text-sound-human", "title": "How to Make ChatGPT Text Sound Human Instantly", "desc": "Transform ChatGPT output into natural, human-sounding text that passes AI detection tools like GPTZero and Turnitin."},
    {"slug": "free-ai-rewriter-for-college-essays", "title": "Free AI Essay Rewriter for College Students (No Detection)", "desc": "Free AI rewriter tool designed for college students. Remove AI tone and make your essays undetectable."},
    {"slug": "undetectable-ai-website-for-students", "title": "The Best Undetectable AI Website for Academic Writing", "desc": "Discover the best undetectable AI website for students. Write essays that pass all AI plagiarism checkers."},
    {"slug": "convert-chatgpt-to-human-text-online", "title": "Convert ChatGPT to Human-Like Text Online", "desc": "Free online tool to convert ChatGPT text to human-like writing. 100% free and undetectable."},
    {"slug": "how-to-not-get-caught-using-chatgpt", "title": "How to Not Get Caught Using ChatGPT for School", "desc": "Complete guide on how to use ChatGPT for school without getting caught. Bypass AI detection easily."},
    {"slug": "best-ai-humanizer-tool-2026", "title": "Best AI Humanizer Tool in 2026 - Bypass GPTZero & Copyleak", "desc": "The best AI humanizer tool of 2026. Bypass GPTZero, Copyleak, and all major AI detectors with ease."},
    {"slug": "remove-ai-plagiarism-from-essay", "title": "Remove AI Plagiarism and AI Tone from Your Essay", "desc": "Remove AI plagiarism and robotic tone from your essays. Make your writing sound naturally human."},
    {"slug": "make-ai-text-untraceable-free", "title": "Make AI Text Completely Untraceable for Free", "desc": "Make AI-generated text completely untraceable with our free tool. Convert to 100% human score content."},
    {"slug": "bypass-canvas-ai-detector-tips", "title": "How to Bypass Canvas and QuillBot AI Detectors", "desc": "Expert tips to bypass Canvas AI detector and QuillBot. Ensure your assignments pass plagiarism checks."}
]

def generate_internal_links(current_slug):
    links = []
    for item in seo_keywords:
        if item['slug'] != current_slug:
            links.append(f'<a href="/{item["slug"]}.html">{item["title"][:50]}...</a>')
    return ' | '.join(links)

html_template = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="theme-color" content="#4f46e5">
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="{page_title} | BypassAI">
    <meta name="twitter:description" content="{page_description}">
    <meta property="og:title" content="{page_title} | BypassAI">
    <meta property="og:description" content="{page_description}">
    <meta property="og:type" content="website">
    <meta property="og:url" content="{page_url}">
    <title>{page_title} | BypassAI</title>
    <meta name="description" content="{page_description}">
    <meta name="keywords" content="ai humanizer, undetectable ai, {page_keyword}, bypass turnitin, bypass gptzero, bypass canvas, chatgpt humanizer, free ai rewriter">
    <link rel="canonical" href="{page_url}">
    <link rel="alternate" href="https://www.bypassai.org/{page_slug}.html" hreflang="en">
    <script type="application/ld+json">
    {{
        "@context": "https://schema.org",
        "@type": "WebApplication",
        "name": "{page_title}",
        "description": "{page_description}",
        "url": "{page_url}",
        "applicationCategory": "ProductivityApplication",
        "operatingSystem": "Web",
        "offers": {{
            "@type": "Offer",
            "price": "0",
            "priceCurrency": "USD"
        }}
    }}
    </script>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background-color: #f9fafb;
            color: #111827;
            margin: 0;
            padding: 40px 20px;
        }}
        .container {{ max-width: 1000px; margin: 0 auto; }}
        header {{ text-align: center; margin-bottom: 40px; }}
        h1 {{ font-size: 2.5rem; margin-bottom: 10px; color: #4f46e5; font-weight: 800; }}
        p {{ color: #4b5563; font-size: 1.1rem; }}
        .workspace {{ display: grid; grid-template-columns: 1fr 1fr; gap: 24px; margin-bottom: 20px; }}
        @media (max-width: 768px) {{ .workspace {{ grid-template-columns: 1fr; }} }}
        
        .box-container {{ background: white; border: 1px solid #e5e7eb; border-radius: 12px; padding: 16px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); position: relative; }}
        textarea {{
            width: 100%; height: 320px; border: none; font-size: 1rem; resize: none; box-sizing: border-box; background-color: #fff; color: #111827; line-height: 1.6;
        }}
        textarea:focus {{ outline: none; }}
        
        .box-footer {{ display: flex; justify-content: space-between; align-items: center; margin-top: 10px; padding-top: 10px; border-top: 1px solid #f3f4f6; color: #6b7280; font-size: 0.85rem; }}
        
        .btn-container {{ text-align: center; margin-top: 20px; margin-bottom: 20px; }}
        .main-btn {{
            background-color: #4f46e5; color: white; padding: 14px 50px; font-size: 1.1rem; font-weight: 600; border: none; border-radius: 8px; cursor: pointer; transition: all 0.2s; box-shadow: 0 4px 6px -1px rgba(79, 70, 229, 0.2);
        }}
        .main-btn:hover {{ background-color: #4338ca; transform: translateY(-1px); }}
        .main-btn:disabled {{ background-color: #9ca3af; cursor: not-allowed; transform: none; box-shadow: none; }}
        
        .copy-btn {{ background: #f3f4f6; color: #374151; border: 1px solid #d1d5db; padding: 6px 12px; border-radius: 6px; font-size: 0.85rem; cursor: pointer; font-weight: 500; }}
        .copy-btn:hover {{ background: #e5e7eb; }}
        
        .loading {{ display: none; color: #4f46e5; font-weight: bold; margin-top: 12px; text-align: center; }}
        footer {{ margin-top: 60px; text-align: center; color: #9ca3af; font-size: 0.9rem; border-top: 1px solid #e5e7eb; padding-top: 20px; }}
        .nav-links {{ margin-top: 30px; padding: 16px; background: #fff; border-radius: 8px; border: 1px solid #e5e7eb; }}
        .nav-links a {{ color: #4f46e5; text-decoration: none; margin: 0 8px; font-size: 0.85rem; }}
        .nav-links a:hover {{ text-decoration: underline; }}
        .feature-list {{ text-align: left; max-width: 600px; margin: 0 auto 30px; padding: 0 20px; }}
        .feature-list li {{ margin-bottom: 10px; color: #4b5563; }}
    </style>
</head>
<body>

<div class="container">
    <header>
        <h1>{page_title}</h1>
        <p>{page_description}</p>
    </header>

    <div class="feature-list">
        <ul>
            <li>🔄 Convert AI-generated text (ChatGPT, Claude, Gemini) to natural human writing</li>
            <li>✅ Pass all major AI detectors: Turnitin, GPTZero, Copyleak, Canvas</li>
            <li>🎯 100% free with no registration required</li>
            <li>⚡ Fast processing with deep learning technology</li>
        </ul>
    </div>

    <div class="workspace">
        <div class="box-container">
            <textarea id="inputText" placeholder="Paste your AI-generated text here (ChatGPT, Claude, Gemini...)" oninput="countWords()"></textarea>
            <div class="box-footer">
                <span id="inputCount">0 words / 0 chars</span>
                <span>Input Text</span>
            </div>
        </div>
        
        <div class="box-container">
            <textarea id="outputText" placeholder="Humanized text will appear here..." readonly></textarea>
            <div class="box-footer">
                <span id="outputCount">0 words</span>
                <button class="copy-btn" id="copyBtn" onclick="copyToClipboard()">Copy Text</button>
            </div>
        </div>
    </div>
    
    <div class="btn-container">
        <button class="main-btn" id="submitBtn" onclick="processText()">Humanize Text</button>
        <div id="loadingText" class="loading">✨ Humanizing your text with deep learning, please wait...</div>
    </div>

    <div class="nav-links">
        <strong>Related Tools:</strong> {internal_links}
    </div>

    <footer>
        <p>© 2026 BypassAI. All rights reserved.</p>
        <p style="margin-top: 10px;"><a href="/">Home</a> | <a href="/sitemap.xml">Sitemap</a></p>
    </footer>
</div>

<script>
    function countWords() {{
        const text = document.getElementById('inputText').value.trim();
        const words = text === "" ? 0 : text.split(/\s+/).length;
        const chars = text.length;
        document.getElementById('inputCount').innerText = `${{words}} words / ${{chars}} chars`;
    }}

    function copyToClipboard() {{
        const outputText = document.getElementById('outputText');
        const text = outputText.value.trim();
        if (!text) {{
            alert('No text to copy. Please humanize some text first.');
            return;
        }}
        if (navigator.clipboard) {{
            navigator.clipboard.writeText(text).then(() => {{
                const copyBtn = document.getElementById('copyBtn');
                copyBtn.innerText = "✓ Copied!";
                setTimeout(() => {{ copyBtn.innerText = "Copy Text"; }}, 2000);
            }});
        }} else {{
            outputText.select();
            document.execCommand('copy');
            alert('Text copied to clipboard!');
        }}
    }}

    async function processText() {{
        const input = document.getElementById('inputText').value;
        const outputField = document.getElementById('outputText');
        const btn = document.getElementById('submitBtn');
        const loading = document.getElementById('loadingText');

        if (!input.trim()) {{
            alert('Please enter some text first.');
            return;
        }}

        btn.disabled = true;
        loading.style.display = 'block';
        outputField.value = '';
        document.getElementById('outputCount').innerText = "0 words";

        try {{
            const response = await fetch('{api_url}/api/humanize', {{
                method: 'POST',
                headers: {{ 'Content-Type': 'application/json' }},
                body: JSON.stringify({{ text: input }})
            }});

            const result = await response.json();
            if (response.ok && result.success) {{
                outputField.value = result.data;
                const outWords = result.data.trim().split(/\s+/).length;
                document.getElementById('outputCount').innerText = `${{outWords}} words`;
            }} else {{
                alert('Error: ' + (result.detail || result.message || 'Failed to process text.'));
            }}
        }} catch (error) {{
            alert('Could not connect to the server. Please try again later.');
        }} finally {{
            btn.disabled = false;
            loading.style.display = 'none';
        }}
    }}

    document.getElementById('inputText').addEventListener('keydown', function(e) {{
        if (e.ctrlKey && e.key === 'Enter') {{
            processText();
        }}
    }});
</script>
</body>
</html>
"""

def generate_sitemap():
    sitemap_entries = []
    sitemap_entries.append(f'  <url><loc>{BASE_URL}/</loc><changefreq>daily</changefreq><priority>1.0</priority></url>')
    for item in seo_keywords:
        sitemap_entries.append(f'  <url><loc>{BASE_URL}/{item["slug"]}.html</loc><changefreq>daily</changefreq><priority>0.8</priority></url>')
    
    sitemap_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{chr(10).join(sitemap_entries)}
</urlset>"""
    return sitemap_content

def generate_robots():
    return f"""User-agent: *
Allow: /
Sitemap: {BASE_URL}/sitemap.xml"""

print("开始全自动批量升级并生成网页矩阵...")

for item in seo_keywords:
    file_name = f"{item['slug']}.html"
    page_content = html_template.format(
        page_title=item['title'],
        page_description=item['desc'],
        page_keyword=item['slug'].replace("-", " "),
        page_url=f"{BASE_URL}/{item['slug']}.html",
        page_slug=item['slug'],
        internal_links=generate_internal_links(item['slug']),
        api_url=API_BASE_URL
    )
    with open(file_name, "w", encoding="utf-8") as f:
        f.write(page_content)
    print(f"高级矩阵页已就位: {file_name}")

index_content = html_template.format(
    page_title="BypassAI - Free Undetectable AI Text Humanizer",
    page_description="Free AI text humanizer tool. Convert ChatGPT, Claude, Gemini text to 100% human score content. Bypass Turnitin, GPTZero, and all AI detectors.",
    page_keyword="bypass ai detection free",
    page_url=f"{BASE_URL}/",
    page_slug="index",
    internal_links=generate_internal_links("index"),
    api_url=API_BASE_URL
)
with open("index.html", "w", encoding="utf-8") as f:
    f.write(index_content)
print("高级主页已就位: index.html")

with open("sitemap.xml", "w", encoding="utf-8") as f:
    f.write(generate_sitemap())
print("Sitemap已生成: sitemap.xml")

with open("robots.txt", "w", encoding="utf-8") as f:
    f.write(generate_robots())
print("Robots.txt已生成: robots.txt")

print("\n🎉 华丽变身！所有网页已无缝升级到大厂级交互体验！")
print(f"\n配置说明:")
print(f"- 前端部署到 Cloudflare Pages，根目录设置为当前目录")
print(f"- 后端部署到 Render，然后更新 API_BASE_URL = '{API_BASE_URL}'")
print(f"- 更新 BASE_URL = '{BASE_URL}' 为你的域名")