import pandas as pd

df = pd.read_csv('../data/processed/cars_v8.csv')

df = df[df["year"] >= 1990]
df = df[df["price"] > 0]
df = df[df["mileage"] > 0]
df = df[df["owners_number"] > 0]
df = df[df["displacement"] > 0]
df = df[df["power"] > 0]

q_low_price = df["price"].quantile(0.01)
q_high_price = df["price"].quantile(0.99)
q_low_mileage = df["mileage"].quantile(0.01)
q_high_mileage = df["mileage"].quantile(0.99)

df = df[(df["price"] >= q_low_price) & (df["price"] <= q_high_price)]
df = df[(df["mileage"] >= q_low_mileage) & (df["mileage"] <= q_high_mileage)]
print(f"После удаления выбросов: {len(df)}")

df['power_per_liter'] = df['power'] / (df['displacement'] / 1000)

premium = [
    'Porsche',
    'Li Auto (Lixiang)'
    'Lexus',
    'Cadillac',
    'Mercedes-Benz',
    'Land Rover',
    'BMW',
    'Infiniti',
    'Audi',
    'Land Rover',
    'Jaguar',
    'Volvo',
]
df['is_premium'] = df['brand'].isin(premium).astype(int)

df.to_csv("../data/processed/cars_v8.csv", index=False, encoding="utf-8-sig")
print("Сохранено в data/processed/cars_v8.csv")