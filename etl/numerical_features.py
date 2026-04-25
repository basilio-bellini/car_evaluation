import pandas as pd

df = pd.read_csv('../data/processed/cars.csv')
print(df[["year", "mileage", "price", "displacement", "power"]].describe(),'\n')

Q1 = df["price"].quantile(0.25)
Q3 = df["price"].quantile(0.75)
IQR = Q3 - Q1

lower = Q1 - 1.5 * IQR
upper = Q3 + 1.5 * IQR

outliers = df[(df["price"] < lower) | (df["price"] > upper)]
print(f"Выбросов по цене: {len(outliers)}")

Q1 = df["price"].quantile(0.25)
Q3 = df["price"].quantile(0.75)
IQR = Q3 - Q1
upper = Q3 + 1.5 * IQR
lower = Q1 - 1.5 * IQR

print("Дорогие:")
print(df[df["price"] > upper][["brand", "model", "year", "price"]].sort_values("price", ascending=False).head(10))

print("\nДешёвые:")
print(df[df["price"] < lower][["brand", "model", "year", "price"]].sort_values("price").head(10), '\n')

print(f"Верхняя граница цены: {upper:,.0f} руб.")
print(f"До фильтрации: {len(df)}")

df = df[df["price"] <= upper]

print(f"После фильтрации: {len(df)}")

df = df[df["mileage"] >= 100]

print(f"После фильтрации по пробегу: {len(df)}")

df.to_csv("../data/processed/cars.csv", index=False, encoding="utf-8-sig")
print("Сохранено в data/processed/cars.csv")