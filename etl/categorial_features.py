import pandas as pd

df = pd.read_csv('../data/processed/cars_v2.csv')

rare_colors = ['жёлтый', 'золотистый']
df["color"] = df["color"].apply(lambda x: "другой" if x in rare_colors else x)

rare_bodies = ['CABRIO', 'MICROVAN', 'HATCHBACK_4_DOORS', 'COUPE', 'PICKUP_ONE', 'PICKUP_TWO']
df["body_type"] = df["body_type"].apply(lambda x: "OTHER" if x in rare_bodies else x)

rare_classes = ['UNKNOWN', 'F', 'S']
df["auto_class"] = df["auto_class"].apply(lambda x: "OTHER" if x in rare_bodies else x)

rare_engines = ['LPG', 'HYBRID', 'ELECTRO']
df["engine_type"] = df["engine_type"].apply(lambda x: "OTHER" if x in rare_bodies else x)

print('\n', f"Финальное количество: {len(df)}")

df.to_csv("../data/processed/cars.csv", index=False, encoding="utf-8-sig")
print("Сохранено в data/processed/cars_v2.csv")