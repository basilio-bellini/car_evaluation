import pandas as pd

df = pd.read_csv('../data/processed/cars_v8.csv')

df = df.drop_duplicates(subset='url')
df = df.drop_duplicates(
    subset=[
        "brand",
        "model",
        "year",
        "mileage",
        "price",
        "description",
        "region",
        "color"
    ]
)
print(f"После удаления дублей: {len(df)}")

df.to_csv("../data/processed/cars_v8.csv", index=False, encoding="utf-8-sig")
print("Сохранено в data/processed/cars_v8.csv")