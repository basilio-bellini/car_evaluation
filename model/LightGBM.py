import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from lightgbm import LGBMRegressor



df = pd.read_csv("../data/processed/cars_v2.csv")
X = df.drop(columns=["price", "url", "description"])
y = df["price"]

numerical = ["year", "mileage", "displacement", "power"]
categorical = ["brand", "model", "color", "body_type", "auto_class",
               "owners_number", "accidents", "engine_type",
               "transmission", "gear_type"]

preprocessor = ColumnTransformer(transformers=[
    ("num", StandardScaler(), numerical),
    ("cat", OneHotEncoder(handle_unknown="ignore"), categorical)
])

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

pipeline_lgbm = Pipeline(steps=[
    ("preprocessor", preprocessor),
    ("model", LGBMRegressor(
        n_estimators=100,
        learning_rate=0.1,
        max_depth=6,
        random_state=42
    ))
])

pipeline_lgbm.fit(X_train, y_train)
y_pred_lgbm = pipeline_lgbm.predict(X_test)

mae = mean_absolute_error(y_test, y_pred_lgbm)
rmse = np.sqrt(mean_squared_error(y_test, y_pred_lgbm))
r2 = r2_score(y_test, y_pred_lgbm)

print("LightGBM:")
print(f"  MAE:  {mae:,.0f} руб.")
print(f"  RMSE: {rmse:,.0f} руб.")
print(f"  R²:   {r2:.4f}")