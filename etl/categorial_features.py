import pandas as pd

df = pd.read_csv('../data/processed/cars.csv')
for col in ["color", "body_type", "auto_class", "owners_number",
            "accidents", "engine_type", "transmission", "gear_type"]:
    print(f"\n{col}:")
    print(df[col].value_counts())

rare_colors = ['жёлтый', 'золотистый', 'фиолетовый', 'оранжевый', 'голубой', 'пурпурный']
df["color"] = df["color"].apply(lambda x: "другой" if x in rare_colors else x)

rare_bodies = ['ALLROAD_3_DOORS', 'ALLROAD_OPEN', 'VAN', 'CABRIO', 'ROADSTER']
df["body_type"] = df["body_type"].apply(lambda x: "OTHER" if x in rare_bodies else x)

df["auto_class"] = df["auto_class"].replace({'A': 'B', 'S': 'F'})

df = df[df["engine_type"] != "ELECTRO"]

print('\n', f"Финальное количество: {len(df)}")

df.to_csv("../data/processed/cars.csv", index=False, encoding="utf-8-sig")
print("Сохранено в data/processed/cars.csv")