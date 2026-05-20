import pandas as pd

df = pd.read_csv('../data/processed/cars_v8.csv')

df["body_type"] = df["body_type"].replace({
    'PICKUP_TWO': 'PICKUP',
    'PICKUP_ONE_HALF': 'PICKUP',
    'PICKUP_ONE': 'PICKUP',

    'ROADSTER': 'CABRIO',
    'TARGA': 'CABRIO',

    'ALLROAD_OPEN': 'CABRIO',
    'MICROVAN': 'VAN',
    'COUPE_HARDTOP': 'COUPE',
    'HATCHBACK_4_DOORS': 'HATCHBACK_5_DOORS',
    'LIMOUSINE': 'SEDAN',
    'FASTBACK': 'LIFTBACK'
})

region_counts = df["region"].value_counts()
major_regions = region_counts[region_counts >= 20].index
df["region"] = df["region"].apply(
    lambda x: x if x in major_regions else "Другой регион"
)


df.to_csv("../data/processed/cars_v8.csv", index=False, encoding="utf-8-sig")
print("Сохранено в data/processed/cars_v8.csv")