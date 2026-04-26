import json
import pandas as pd

COLOR_MAP = {
    'FAFBFB': 'белый',
    'CACECB': 'серебристый',
    '97948F': 'серый',
    '040001': 'чёрный',
    '200204': 'коричневый',
    'EE1D19': 'красный',
    'FF8649': 'оранжевый',
    'FFD600': 'жёлтый',
    '007F00': 'зелёный',
    '22A0F8': 'голубой',
    '0000CC': 'синий',
    '4A2197': 'фиолетовый',
    '660099': 'пурпурный',
    'DEA522': 'золотистый',
    'C49648': 'бежевый',
}

with open("../data/raw/offers.json", "r", encoding="utf-8") as f:
    offers = json.load(f)

rows = []
for offer in offers:
    try:
        row = {
            "brand":          offer["vehicle_info"]["mark_info"]["name"],
            "model":          offer["vehicle_info"]["model_info"]["name"],
            "year":           offer["documents"]["year"],
            "mileage":        offer["state"]["mileage"],
            "price":          offer["price_info"]["price"],
            "color":          COLOR_MAP.get(offer.get("color_hex"), "другой"),
            "body_type":      offer["vehicle_info"]["configuration"]["body_type"],
            "auto_class":     offer["vehicle_info"]["configuration"].get("auto_class", "UNKNOWN"),
            "owners_number":  offer["documents"]["owners_number"],
            "accidents":      offer["documents"]["accidents_resolution"],
            "engine_type":    offer["vehicle_info"]["tech_param"]["engine_type"],
            "transmission":   offer["vehicle_info"]["tech_param"]["transmission"],
            "gear_type":      offer["vehicle_info"]["tech_param"]["gear_type"],
            "displacement":   offer["vehicle_info"]["tech_param"]["displacement"],
            "power":          offer["vehicle_info"]["tech_param"]["power"],
            "url":            offer["url"],
            "description":    offer.get("description", ""),
        }
        rows.append(row)
    except KeyError as e:
        print(f"Пропускаем объявление, нет поля: {e}")

df = pd.DataFrame(rows)
print(f"Итого строк: {len(df)}")
print(df.head())

df = df[df["description"].str.strip() != ""]
print(f"После удаления пустых описаний: {len(df)}")

df = df.drop_duplicates(subset='url')
print(f"После удаления дублей: {len(df)}")

df.to_csv("../data/processed/cars.csv", index=False, encoding="utf-8-sig")
print("Сохранено в data/processed/cars.csv")
