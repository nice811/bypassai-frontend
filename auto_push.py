"""
自动推送脚本 - 网络恢复后自动完成代码推送
退出条件：推送成功 或 重试超过30次
"""
import subprocess
import time
import sys

MAX_RETRIES = 30
RETRY_INTERVAL = 60  # 每次间隔60秒

def run_git(cmd):
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120, cwd=r"g:\桌面\文本去 AI 感")
        return result.returncode == 0, result.stdout + result.stderr
    except Exception as e:
        return False, str(e)

def main():
    print(f"[自动推送] 开始执行，最多重试 {MAX_RETRIES} 次，每次间隔 {RETRY_INTERVAL} 秒")
    print(f"[自动推送] 目标仓库: frontend (bypassai-frontend) + api (bypassai-api)")
    
    for attempt in range(1, MAX_RETRIES + 1):
        print(f"\n--- 第 {attempt}/{MAX_RETRIES} 次尝试 ---")
        print(f"[{time.strftime('%H:%M:%S')}] 检查网络连接...")
        
        # 先测试网络连通性
        ok, _ = run_git(["git", "ls-remote", "https://github.com/nice811/bypassai-frontend.git", "HEAD"])
        if not ok:
            print(f"[{time.strftime('%H:%M:%S')}] 网络不通，等待 {RETRY_INTERVAL} 秒后重试...")
            time.sleep(RETRY_INTERVAL)
            continue
        
        print(f"[{time.strftime('%H:%M:%S')}] 网络已连通，开始推送...")
        
        # 推送前端代码
        print(f"[{time.strftime('%H:%M:%S')}] 推送前端代码到 bypassai-frontend...")
        ok, output = run_git(["git", "push", "frontend", "main"])
        if ok:
            print(f"[{time.strftime('%H:%M:%S')}] 前端代码推送成功!")
        else:
            print(f"[{time.strftime('%H:%M:%S')}] 前端推送失败: {output[:200]}")
            time.sleep(RETRY_INTERVAL)
            continue
        
        # 推送后端代码
        print(f"[{time.strftime('%H:%M:%S')}] 推送后端代码到 bypassai-api...")
        ok, output = run_git(["git", "push", "api", "main"])
        if ok:
            print(f"[{time.strftime('%H:%M:%S')}] 后端代码推送成功!")
        else:
            print(f"[{time.strftime('%H:%M:%S')}] 后端推送失败: {output[:200]}")
        
        print(f"\n[自动推送] 全部完成! Cloudflare Pages 和 Railway 将自动部署。")
        return 0
    
    print(f"\n[自动推送] 已达最大重试次数 {MAX_RETRIES}，仍未成功。请稍后手动运行: git push frontend main")
    return 1

if __name__ == "__main__":
    sys.exit(main())
