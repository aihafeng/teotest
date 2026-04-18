import asyncio
import os
import sys
import requests
from playwright.async_api import async_playwright

# 兼容性处理：修复 playwright_stealth 导入问题
try:
    from playwright_stealth import stealth_async
except ImportError:
    # 备用方案：如果 stealth_async 导入失败，尝试同步版包装
    async def stealth_async(page):
        from playwright_stealth import stealth_page_sync
        stealth_page_sync(page)

# 从 GitHub Secrets 获取环境变量
EMAIL = os.getenv("TEO_EMAIL")
PASSWORD = os.getenv("TEO_PASSWORD")
TG_TOKEN = os.getenv("TG_TOKEN")
TG_CHAT_ID = os.getenv("TG_CHAT_ID")

async def send_tg_msg(message):
    """发送 Telegram 通知"""
    if TG_TOKEN and TG_CHAT_ID:
        try:
            url = f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage"
            payload = {"chat_id": TG_CHAT_ID, "text": message}
            requests.post(url, json=payload, timeout=10)
        except Exception as e:
            print(f"⚠️ TG 推送失败: {e}")

async def run_bot():
    async with async_playwright() as p:
        print("🚀 启动浏览器...")
        # 模拟真实浏览器环境
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            viewport={'width': 1920, 'height': 1080}
        )
        page = await context.new_page()
        
        # 隐藏自动化特征
        await stealth_async(page)

        try:
            # 1. 登录
            print("🔑 正在打开登录页面...")
            await page.goto("https://manager.teoheberg.fr/login", wait_until="networkidle")
            await page.fill('input[type="email"]', EMAIL)
            await page.fill('input[type="password"]', PASSWORD)
            
            print("⏳ 提交登录请求...")
            await page.click('button[type="submit"]')
            
            # 等待跳转到主页（根据你的截图，登录后是 /home）
            await page.wait_for_url("**/home", timeout=60000)
            print("✅ 登录成功！")

            # 2. 导航到领取页面
            print("💰 正在导航至 Credits 领取页面...")
            await page.goto("https://manager.teoheberg.fr/coins/earn", wait_until="networkidle")

            # 3. 模拟点击生成按钮 (Commencer maintenant)
            # 注意：如果这里有验证码，GitHub Actions 的 IP 可能会卡住
            if await page.get_by_text("Commencer maintenant").is_visible():
                await page.click('text=Commencer maintenant')
                print("🔘 已点击开始按钮...")
            
            # 4. 模拟等待（此处逻辑视 Linkvertise 跳转而定）
            print("💤 等待系统处理 (15s)...")
            await asyncio.sleep(15) 
            
            print("🎉 任务执行完毕！")
            await send_tg_msg("TeoHeberg 脚本运行完毕，请检查金币数。")

        except Exception as e:
            error_msg = f"❌ 运行出错: {str(e)}"
            print(error_msg)
            # 出错时截图便于调试
            await page.screenshot(path="error_debug.png")
            await send_tg_msg(error_msg)
        finally:
            await browser.close()
            print("🚫 浏览器已关闭")

# 正确的入口判断
if name == "__main__":
    if not EMAIL or not PASSWORD:
        print("❌ 错误: 请在 GitHub Secrets 中设置 TEO_EMAIL 和 TEO_PASSWORD")
        sys.exit(1)
    
    # 启动异步任务
    asyncio.run(run_bot())
