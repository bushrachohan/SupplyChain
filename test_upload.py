import asyncio
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        errors = []
        page.on('response', lambda r: errors.append(f'{r.status} {r.url}') if r.status >= 500 else None)
        await page.goto('http://localhost:5173/app/data-hub')
        await page.set_input_files('input[type="file"]', r'd:\SupplyChain\data\supplychain_data.xlsx')
        await page.wait_for_timeout(2000)
        try:
            await page.click('button:has-text("Validate")')
            await page.wait_for_timeout(2000)
        except Exception as e:
            print("Validate failed:", e)
        try:
            await page.click('button:has-text("Activate")')
            await page.wait_for_timeout(2000)
        except Exception as e:
            print("Activate failed:", e)
        
        print('Recorded 500s:', errors)
        await browser.close()

asyncio.run(run())
