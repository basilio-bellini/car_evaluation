from playwright.sync_api import sync_playwright, Error as PlaywrightError
import json
import time
import random
import os

INPUT_FILE = "../data/raw/offers.jsonl"
OUTPUT_FILE = "../data/raw/offers_with_descriptions.jsonl"
exception_count = 0

def load_processed_urls():
    processed = set()
    if not os.path.exists(OUTPUT_FILE):
        return processed
    with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                offer = json.loads(line)
                url = offer.get("url", "")
                if url:
                    processed.add(url)
            except:
                continue
    print(f"Уже обработано: {len(processed)} объявлений")
    return processed

def iter_offers():
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                yield json.loads(line)
            except:
                continue

def save_offer(offer):
    with open(OUTPUT_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(offer, ensure_ascii=False) + "\n")

def create_browser(p):
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        locale="ru-RU",
    )
    page = context.new_page()
    return browser, page

processed_urls = load_processed_urls()

total = sum(1 for _ in iter_offers())
print(f"Всего объявлений: {total}")
print(f"Осталось обработать: {total - len(processed_urls)}")

with sync_playwright() as p:
    browser, page = create_browser(p)
    processed_count = len(processed_urls)

    for offer in iter_offers():
        url = offer.get("url", "")

        if url in processed_urls:
            continue

        retry = 0
        while retry < 3:
            try:
                page.goto(url, timeout=15000)

                try:
                    page.wait_for_selector(".CardDescriptionHTML", timeout=5000)
                    description = page.query_selector(".CardDescriptionHTML")
                    offer["description"] = (
                        description.inner_text() if description else ""
                    )
                except Exception as e:
                    exception_count += 1
                    print(f"Ошибка сбора  [{exception_count}], скорее всего нет описания  {e}")
                    offer["description"] = ""

                break

            except PlaywrightError as e:
                retry += 1
                print(f"Ошибка браузера (попытка {retry}/3): {e}")
                try:
                    browser.close()
                except:
                    pass
                time.sleep(5)
                browser, page = create_browser(p)

        save_offer(offer)
        processed_urls.add(url)
        processed_count += 1
        del offer

        if processed_count % 100 == 0:
            print(f"Прогресс: {processed_count}/{total}")

        time.sleep(random.uniform(0.5, 2.5))

    browser.close()

print(f"Готово! Обработано: {processed_count} объявлений")
