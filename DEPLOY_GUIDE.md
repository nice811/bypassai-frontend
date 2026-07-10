# 部署指南：将含订阅按钮的版本更新到 `old-leaf-3c49.mr6988990.workers.dev`

## 现状
- 已生成 [worker-inline.js](file:///g:/%E6%A1%8C%E9%9D%A2/%E6%96%87%E6%9C%AC%E5%8E%BB%20AI%20%E6%84%9F/worker-inline.js) (443 KB)
- 包含全部 11 个 HTML 页面 + robots.txt + sitemap.xml（24 条路由）
- 内嵌了三个 Paddle 订阅按钮（Starter/Pro/Advanced）
- Worker 名称: `old-leaf-3c49`，子域: `mr6988990`
- Account ID: `dac1a974161f964da72fde126912a930`

## 三种部署方式

### 方式 1：Cloudflare Dashboard Quick Edit（最简单，无需凭证）

1. 打开 https://dash.cloudflare.com → Workers & Pages → `old-leaf-3c49`
2. 右上角点 **Quick edit** 按钮
3. **全选删除** 默认代码
4. 用记事本打开 `g:\桌面\文本去 AI 感\worker-inline.js`
5. **Ctrl+A** 全选 → **Ctrl+C** 复制
6. 在 Quick Edit 编辑区 **Ctrl+A** → **Ctrl+V** 粘贴
7. 点 **Save and Deploy**（右上角）
8. 等待 5~10 秒，访问 https://old-leaf-3c49.mr6988990.workers.dev/ 验证

> Quick Edit 限制 1MB，worker-inline.js 是 443 KB，在限制内 ✅

### 方式 2：wrangler CLI（需要 wrangler login）

```bash
# 一次性登录
npx wrangler login

# 部署
cd "g:\桌面\文本去 AI 感"
npx wrangler deploy --config wrangler-inline.toml
```

### 方式 3：Cloudflare API（需要 API Token）

提供 Token 后我可以执行：
```bash
curl -X PUT "https://api.cloudflare.com/client/v4/accounts/dac1a974161f964da72fde126912a930/workers/scripts/old-leaf-3c49" \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: multipart/form-data" \
  -F "metadata={\"main_module\":\"worker-inline.js\",\"compatibility_date\":\"2024-01-01\"};type=application/json" \
  -F "worker-inline.js=@worker-inline.js;type=application/javascript+module"
```

## 验证清单
- [ ] 访问根路径 → 看到 3 个 "Start Free Trial" 按钮
- [ ] 点击 Starter ($10) → 弹出 Paddle 沙盒 checkout
- [ ] 点击 Pro ($40) → 弹出 Paddle 沙盒 checkout
- [ ] 点击 Advanced ($120) → 弹出 Paddle 沙盒 checkout
- [ ] 访问 `/sitemap.xml` → 返回 200
- [ ] 访问 `/robots.txt` → 返回 200
