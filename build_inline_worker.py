#!/usr/bin/env python3
"""
将所有静态资源内嵌到一个 worker.js 中，方便 Cloudflare Workers Quick Edit 部署。
"""
import os
import re
from pathlib import Path

ROOT = Path(r"g:\桌面\文本去 AI 感")

# 收集所有要内嵌的文件（按路由路径组织）
ASSETS = {}
html_files = [
    "index.html",
    "best-ai-humanizer-tool-2026.html",
    "bypass-canvas-ai-detector-tips.html",
    "bypass-turnitin-ai-detection-free.html",
    "convert-chatgpt-to-human-text-online.html",
    "free-ai-rewriter-for-college-essays.html",
    "how-to-not-get-caught-using-chatgpt.html",
    "make-ai-text-untraceable-free.html",
    "make-chatgpt-text-sound-human.html",
    "remove-ai-plagiarism-from-essay.html",
    "undetectable-ai-website-for-students.html",
]
other_files = ["robots.txt", "sitemap.xml"]

for fn in html_files + other_files:
    p = ROOT / fn
    if p.exists():
        ASSETS["/" + fn] = p.read_text(encoding="utf-8")

# 同时为 SEO 页面提供无 .html 后缀的路径（去掉尾缀 .html）
route_map = {}
for k, v in ASSETS.items():
    route_map[k] = v
    if k.endswith(".html"):
        route_map[k[:-5]] = v  # /foo.html -> /foo

# 构造 worker.js 模板
def js_str(s):
    # 使用 JSON.stringify 以安全转义
    import json
    return json.dumps(s, ensure_ascii=False)

assets_obj_parts = []
for path, content in route_map.items():
    if path.endswith(".html"):
        ct = "text/html; charset=utf-8"
    elif path.endswith(".xml"):
        ct = "application/xml; charset=utf-8"
    elif path.endswith(".txt"):
        ct = "text/plain; charset=utf-8"
    else:
        ct = "application/octet-stream"
    assets_obj_parts.append(f"  {js_str(path)}: {{ content: {js_str(content)}, type: {js_str(ct)} }}")

assets_obj = "{\n" + ",\n".join(assets_obj_parts) + "\n}"

worker_js = f"""// BypassAI Frontend - Cloudflare Workers (Inline Assets)
// 自动生成：包含全部 11 个 HTML 页面 + robots.txt + sitemap.xml
// 部署：将本文件整体粘贴到 Cloudflare Dashboard → Workers → Quick Edit

const ASSETS = {assets_obj};

function resolveAsset(pathname) {{
  if (ASSETS[pathname]) return ASSETS[pathname];
  // 去掉尾部斜杠
  if (pathname !== "/" && pathname.endsWith("/")) {{
    const p2 = pathname.slice(0, -1);
    if (ASSETS[p2]) return ASSETS[p2];
  }}
  // 尝试添加 .html
  if (!pathname.includes(".")) {{
    const p3 = pathname + ".html";
    if (ASSETS[p3]) return ASSETS[p3];
    if (pathname === "/" && ASSETS["/index.html"]) return ASSETS["/index.html"];
  }}
  return null;
}}

export default {{
  async fetch(request) {{
    const url = new URL(request.url);
    const path = url.pathname;
    const asset = resolveAsset(path);
    if (asset) {{
      return new Response(asset.content, {{
        status: 200,
        headers: {{
          "Content-Type": asset.type,
          "Cache-Control": "public, max-age=300",
          "X-Worker-Inline": "bypassai-v2"
        }}
      }});
    }}
    return new Response("Not Found", {{ status: 404 }});
  }}
}};
"""

out_path = ROOT / "worker-inline.js"
out_path.write_text(worker_js, encoding="utf-8")
print(f"已生成: {out_path}")
print(f"大小: {out_path.stat().st_size/1024:.1f} KB")
print(f"文件数: {len(route_map)}")
print(f"路由列表:")
for p in sorted(route_map.keys()):
    print(f"  {p}")
