from playwright.sync_api import sync_playwright
import json
import time
import random

# Загружаем уже собранные данные
with open("../data/raw/offers.json", "r", encoding="utf-8") as f:
    offers = json.load(f)

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        locale="ru-RU",
    )
    page = context.new_page()

    for offer in offers:
        if not offer.get("description_parsed", False):
            url = offer["url"]

            try:
                page.goto(url)
                page.wait_for_selector(".CardDescriptionHTML", timeout=10000)
                description = page.query_selector(".CardDescriptionHTML")
                offer["description"] = description.inner_text() if description else ""

            except Exception as e:
                print(f"Ошибка: {url} — {e}")
                offer["description"] = ""

            offer["description_parsed"] = True

            with open("../data/raw/offers.json", "w", encoding="utf-8") as f:
                json.dump(offers, f, ensure_ascii=False, indent=2)

        time.sleep(random.uniform(0.5, 2.5))

    browser.close()
