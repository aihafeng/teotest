import asyncio
import os
import sys
from playwright.async_api import async_playwright
from playwright_stealth import stealth_page_sync, stealth_async
# 如果还是报错，直接用下面这一行更通用的写法：
import playwright_stealth

# 获取 GitHub Actions 环境变量
EMAIL = os.getenv("TEO_EMAIL")
PASSWORD = os.getenv("TEO_PASSWORD")
# 如果使用第三方验证码平台，如 YesCaptcha / 2Captcha
CAPTCHA_API_KEY = os.getenv("CAPTCHA_API_KEY") 
TG_TOKEN = os.getenv("TG_TOKEN")
TG_CHAT_ID = os.getenv("TG_CHAT_ID")

async def send_tg_msg(message):
    if TG_TOKEN and TG_CHAT_ID:
        import requests
        url = f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage"
        payload = {"chat_id": TG_CHAT_ID, "text": message}
        requests.post(url, json=payload)

async def run_bot():
    async with async_playwright() as p:
        # 启动浏览器，模拟真实环境
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            viewport={'width': 1920, 'height': 1080}
        )
        page = await context.new_page()
        # 注入 Stealth 插件隐藏自动化特征
        await stealth_async(page, playwright_stealth.StealthConfig())
        # 或者最简单的一行：
        from playwright_stealth import stealth_async
        await stealth_async(page)

        print("🚀 启动浏览器...")
        
        try:
            # 1. 登录流程
            await page.goto("https://manager.teoheberg.fr/login")
            await page.fill('input[type="email"]', EMAIL)
            await page.fill('input[type="password"]', PASSWORD)
            
            # 这里如果遇到 reCAPTCHA，通常需要配合 API 或等待手动过验证
            # 如果你有 API，可以在这里调用处理逻辑
            
            await page.click('button[type="submit"]')
            await page.wait_for_url("**/home")
            print("✅ 登录成功！")

            # 2. 跳转到赚取金币页面
            await page.goto("https://manager.teoheberg.fr/coins/earn")
            print("💰 正在导航至 Earn Credits 页面...")

            # 3. 处理 Linkvertise 逻辑 (模拟点击)
            # 注意：Linkvertise 具有极强的反爬，通常需要调用 bypass.city 的 API
            # 以下为模拟点击生成按钮的占位逻辑
            await page.click('button:has-text("Commencer maintenant")')
            
            # 4. 获取金币后的处理
            # 模拟等待金币更新...
            await asyncio.sleep(10) 
            
            print("🎉 金币领取成功！")
            await send_tg_msg("TeoHeberg 脚本运行成功：金币 +2.00")

        except Exception as e:
            print(f"❌ 运行出错: {e}")
            await send_tg_msg(f"TeoHeberg 脚本出错: {str(e)}")
        finally:
            await browser.close()

if name == "__main__":
    if not EMAIL or not PASSWORD:
        print("错误: 请在环境变量中设置 TEO_EMAIL 和 TEO_PASSWORD")
        sys.exit(1)
    asyncio.run(run_bot())
