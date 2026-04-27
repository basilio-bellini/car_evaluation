import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

# Загружаем данные
df = pd.read_csv("../data/processed/cars.csv")

# Признаки и целевая переменная
X = df.drop(columns=["price", "url", "description"])
y = df["price"]

# Числовые и категориальные признаки
numerical = ["year", "mileage", "displacement", "power"]
categorical = ["brand", "model", "color", "body_type", "auto_class",
               "owners_number", "accidents", "engine_type",
               "transmission", "gear_type"]

# Препроцессинг
preprocessor = ColumnTransformer(transformers=[
    ("num", StandardScaler(), numerical),
    ("cat", OneHotEncoder(handle_unknown="ignore"), categorical)
])

# Pipeline
pipeline = Pipeline(steps=[
    ("preprocessor", preprocessor),
    ("model", LinearRegression())
])

# Разбивка на train/test
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Обучение
pipeline.fit(X_train, y_train)

# Предсказание
y_pred = pipeline.predict(X_test)

# Метрики
mae = mean_absolute_error(y_test, y_pred)
rmse = np.sqrt(mean_squared_error(y_test, y_pred))
r2 = r2_score(y_test, y_pred)

print("Linear Regression:")
print(f"  MAE:  {mae:,.0f} руб.")
print(f"  RMSE: {rmse:,.0f} руб.")
print(f"  R²:   {r2:.4f}")