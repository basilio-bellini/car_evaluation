from playwright.sync_api import sync_playwright
import json
import time
import random

all_offers = []

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        locale="ru-RU",
    )

    page = context.new_page()

    page.goto("https://auto.ru/moskva/cars/used/?page=2")
    page.wait_for_selector(".ListingPagination__page", timeout=10000)

    print("Кликаем на страницу 1...")
    try:
        with page.expect_response(
                lambda r: "ajax/desktop-search/listing/" in r.url
        ) as response_info:
            page.click(".ListingPagination__page >> text='1'")

        data = response_info.value.json()
        offers = data.get("offers", [])
        all_offers.extend(offers)
        print(f"Страница 1: {len(offers)} объявлений")
    except Exception as e:
        print(f"Ошибка на странице 1: {e}")

    for i in range(2, 31):
        time.sleep(random.uniform(0.5, 2.5))
        print(f"Кликаем страницу {i}...")
        try:
            with page.expect_response(
                    lambda r: "ajax/desktop-search/listing/" in r.url,
                    timeout=10000
            ) as response_info:
                page.click(".ListingPagination__next")

            data = response_info.value.json()
            offers = data.get("offers", [])
            all_offers.extend(offers)
            print(f"Страница {i}: {len(offers)} объявлений, всего: {len(all_offers)}")
        except Exception as e:
            print(f"Конец страниц или ошибка: {e}")
            break

    browser.close()

with open("../data/raw/offers.json", "w", encoding="utf-8") as f:
    json.dump(all_offers, f, ensure_ascii=False, indent=2)

print(f"Итого собрано: {len(all_offers)} объявлений")
