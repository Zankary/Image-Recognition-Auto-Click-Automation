from playwright.sync_api import sync_playwright
import time
with sync_playwright() as pw:
    browser = pw.chromium.launch(headless=False)
    page = browser.new_page()
    page.goto("https://syns.studio/more-ore/")

    canvas = page.locator("canvas.ore-canvas")
    box = canvas.bounding_box()

    x = box["x"] + box["width"] * 0.5
    y = box["y"] + box["height"] * 0.5
    
    time.sleep(30)
    while True:
        page.mouse.click(x, y)
