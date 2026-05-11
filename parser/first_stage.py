from playwright.sync_api import sync_playwright, Error as PlaywrightError
import json
from decimal import Decimal
import time
import random

OUTPUT_FILE = "../data/raw/offers.jsonl"

brands_by_year = [
    "vaz",
    "kia",
    "hyundai",
    "volkswagen",
    "bmw",
    "toyota",
    "mercedes",
    "ford",
    "nissan",
    "chevrolet",
    "audi",
    "skoda",
    "renault",
    "mitsubishi",
    "opel",
]

brands_single = [
    "mazda",
    "geely",
    "land_rover",
    "haval",
    "honda",
    "citroen",
    "daewoo",
    "peugeot",
    "lexus",
    "porsche",
    "infiniti",
    "subaru",
    "suzuki",
    "volvo",
    "chery",
]

years = list(range(1990, 2027))


def convert_decimals(obj):
    if isinstance(obj, Decimal):
        return float(obj)
    if isinstance(obj, dict):
        return {k: convert_decimals(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [convert_decimals(i) for i in obj]
    return obj


def load_collected_keys():
    keys = set()
    try:
        with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    offer = json.loads(line)
                    key = offer.get("_collected_key", "")
                    if key:
                        keys.add(key)
                except:
                    continue
        print(f"Загружено ключей: {len(keys)}")
    except FileNotFoundError:
        print("Файл не найден — начинаем сбор заново")
    except Exception as e:
        print(f"Ошибка загрузки ключей: {e}")
    return keys


def save_progress(new_offers):
    with open(OUTPUT_FILE, "a", encoding="utf-8") as f:
        for offer in new_offers:
            offer = convert_decimals(offer)
            f.write(json.dumps(offer, ensure_ascii=False) + "\n")


def collect_pages(page, url, key):
    total_collected = 0

    try:
        page.goto(url, timeout=30000)
        page.wait_for_load_state("domcontentloaded")
    except PlaywrightError as e:
        print(f"Ошибка загрузки страницы: {e}")
        raise

    for i in range(2, 100):
        time.sleep(random.uniform(0.5, 2.5))
        try:
            with page.expect_response(
                lambda r: "ajax/desktop-search/listing/" in r.url,
                timeout=5000
            ) as response_info:
                page.click(".ListingPagination__next", timeout=5000)

            data = response_info.value.json()
            offers = data.get("offers", [])

            for offer in offers:
                offer["_collected_key"] = key

            save_progress(offers)
            total_collected += len(offers)

            print(f"  Страница {i}: {len(offers)} объявлений, всего по ключу: {total_collected}")

            del offers
            del data

            if total_collected % 37 != 0:
                break
        except Exception as e:
            print(f"  Конец страниц или ошибка: {e}")
            break

    return total_collected


def create_browser(p):
    browser = p.chromium.launch(headless=False)
    context = browser.new_context(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        locale="ru-RU",
    )
    page = context.new_page()
    return browser, page


def collect_brand(page, browser, p, url, key, collected_keys):
    retry = 0
    while retry < 3:
        try:
            total = collect_pages(page, url, key)
            collected_keys.add(key)
            print(f"  Сохранено {total} объявлений для {key}")
            return browser, page
        except PlaywrightError as e:
            retry += 1
            print(f"  Ошибка браузера (попытка {retry}/3): {e}")
            try:
                browser.close()
            except:
                pass
            time.sleep(5)
            browser, page = create_browser(p)

    print(f"  Пропускаем {key} после 3 попыток")
    return browser, page


collected_keys = load_collected_keys()

with sync_playwright() as p:
    browser, page = create_browser(p)

    try:
        page.goto("https://auto.ru/moskva/cars/used")
        page.get_by_title("Москва", exact=True).click()
        page.get_by_role("button", name="Москва").click()
        page.get_by_role("button", name="Сохранить", exact=True).click()
        page.wait_for_load_state("domcontentloaded")
    except Exception as e:
        print(f"Ошибка установки региона: {e}")

    for brand in brands_by_year:
        print(f"\nСобираем {brand}")
        for year in years:
            key = f"{brand}_{year}"
            if key in collected_keys:
                print(f"  Пропускаем {key} — уже собрано")
                continue
            print(f"  Год: {year}")
            url = f"https://auto.ru/cars/{brand}/{year}-year/used/?resolution_filter=is_legal_ok&steering_wheel=LEFT&top_days=60"
            browser, page = collect_brand(page, browser, p, url, key, collected_keys)

    for brand in brands_single:
        key = f"{brand}_all"
        if key in collected_keys:
            print(f"Пропускаем {key} — уже собрано")
            continue
        print(f"\nСобираем {brand}")
        url = f"https://auto.ru/cars/{brand}/used/?resolution_filter=is_legal_ok&steering_wheel=LEFT&top_days=60"
        browser, page = collect_brand(page, browser, p, url, key, collected_keys)

    browser.close()

total = 0
with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
    for line in f:
        if line.strip():
            total += 1

print(f"\nИтого в файле: {total} объявлений")

