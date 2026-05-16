import pandas as pd

df = pd.read_csv('../data/processed/cars_v3.csv')

df = df.drop_duplicates(subset='url')
print(f"После удаления дублей: {len(df)}")