import pandas as pd
import re

df = pd.read_csv('../data/processed/cars_v2.csv')

def clean_description(text):
    if not isinstance(text, str):
        return ""
    text = text.replace("\n", " ").replace("\r", " ")
    text = re.sub(r'[^\w\s]', '', text)
    text = re.sub(r'\d+', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

df["description"] = df["description"].apply(clean_description)

df.to_csv("../data/processed/cars_v2.csv", index=False, encoding="utf-8-sig")
print("Сохранено в data/processed/cars_v2.csv")
