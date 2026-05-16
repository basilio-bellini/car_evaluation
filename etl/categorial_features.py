import pandas as pd

df = pd.read_csv('../data/processed/cars_v3.csv')

rare_colors = ['пурпурный', 'оранжевый', 'фиолетовый', 'жёлтый', 'золотистый']
df["color"] = df["color"].apply(lambda x: "другой" if x in rare_colors else x)

df["body_type"] = df["body_type"].replace({
    'PICKUP_TWO': 'PICKUP',
    'PICKUP_ONE_HALF': 'PICKUP',
    'PICKUP_ONE': 'PICKUP',

    'ROADSTER': 'CABRIO',
    'TARGA': 'CABRIO',

    'MICROVAN': 'VAN',

    'COUPE_HARDTOP': 'COUPE',

    'HATCHBACK_4_DOORS': 'OTHER',
    'LIMOUSINE': 'OTHER'
})

rare_engines = ['LPG', 'HYBRID']
df["engine_type"] = df["engine_type"].apply(lambda x: "OTHER" if x in rare_engines else x)


big_cities = ['Москва', 'Санкт-Петербург', 'Новосибирск',
              'Екатеринбург', 'Казань', 'Красноярск',
              'Нижний Новгород', 'Челябинск', 'Уфа',
              'Краснодар', 'Самара', 'Ростов-на-дону',
              'Омск', 'Воронеж', 'Пермь', 'Волгоград']
df["region"] = df["region"].apply(lambda x: "Регион" if x not in big_cities else x)


print('\n', f"Финальное количество: {len(df)}")

df.to_csv("../data/processed/cars_v3.csv", index=False, encoding="utf-8-sig")
print("Сохранено в data/processed/cars_v3.csv")