import json
import csv

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
    'DEA522': 'золотой',
    'C49648': 'бежевый',
    'FFC0CB': 'розовый'
}

FIELDS = ["brand", "model", "year", "mileage", "price", "color",
          "body_type", "auto_class", "owners_number", "accidents",
          "engine_type", "transmission", "gear_type", "displacement",
          "power", "url", "description", "region"]

total = 0
skipped = 0

with open("../data/raw/offers_with_descriptions.jsonl", "r", encoding="utf-8") as infile, \
     open("../data/processed/cars_v8.csv", "w", encoding="utf-8-sig", newline="") as outfile:

    writer = csv.DictWriter(outfile, fieldnames=FIELDS, quoting=csv.QUOTE_ALL)
    writer.writeheader()

    for line in infile:
        line = line.strip()
        if not line:
            continue

        try:
            offer = json.loads(line)
        except json.JSONDecodeError:
            skipped += 1
            continue

        try:
            row = {
                "brand":         offer["vehicle_info"]["mark_info"]["name"],
                "model":         offer["vehicle_info"]["model_info"]["name"],
                "year":          offer["documents"]["year"],
                "mileage":       offer["state"]["mileage"],
                "price":         offer["price_info"]["price"],
                "color":         COLOR_MAP.get(offer["color_hex"], "другой"),
                "body_type":     offer["vehicle_info"]["configuration"]["body_type"],
                "auto_class":    offer["vehicle_info"]["configuration"]["auto_class"],
                "owners_number": offer["documents"]["owners_number"],
                "accidents":     offer["documents"]["accidents_resolution"],
                "engine_type":   offer["vehicle_info"]["tech_param"]["engine_type"],
                "transmission":  offer["vehicle_info"]["tech_param"]["transmission"],
                "gear_type":     offer["vehicle_info"]["tech_param"]["gear_type"],
                "displacement":  offer["vehicle_info"]["tech_param"]["displacement"],
                "power":         offer["vehicle_info"]["tech_param"]["power"],
                "url":           offer["url"],
                "description":   offer.get("description", ""),
                "region":        offer["seller"]["location"]["region_info"]["name"],
            }
            writer.writerow(row)
            total += 1

            if total % 10000 == 0:
                print(f"Обработано: {total}")

        except KeyError as e:
            skipped += 1

print(f"Итого записано: {total}")
print(f"Пропущено: {skipped}")
