import asyncio
from playwright.async_api import async_playwright
import os

async def convert_html_to_pdf():
    html_path = os.path.abspath("presentation.html")
    pdf_path = os.path.abspath("presentation.pdf")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        
        # Load the HTML file
        await page.goto(f"file:///{html_path}")
        
        # Wait for reveal.js to load
        await page.wait_for_timeout(2000)
        
        # Generate PDF
        await page.pdf(
            path=pdf_path,
            format="A4",
            landscape=True,
            print_background=True,
            margin={"top": "0", "right": "0", "bottom": "0", "left": "0"}
        )
        
        await browser.close()
        print(f"✅ PDF generated successfully: {pdf_path}")

if __name__ == "__main__":
    asyncio.run(convert_html_to_pdf())
