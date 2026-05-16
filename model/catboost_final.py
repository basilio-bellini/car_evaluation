import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from catboost import CatBoostRegressor, Pool

df = pd.read_csv("../data/processed/cars_v3.csv")
df["description"] = df["description"].fillna("")

X = df.drop(columns=["price", "url"])
y = df["price"]

numerical = ["year", "mileage", "displacement", "power", "owners_number"]
categorical = ["brand", "model", "color", "body_type", "auto_class",
               "accidents", "engine_type", "transmission", "gear_type", "region"]
text = ["description"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, shuffle=True
)

best_params = {
    "iterations": 1832,
    "learning_rate": 0.0973,
    "depth": 9,
    "l2_leaf_reg": 5.18928,
    "bagging_temperature": 2.71858,
    "random_seed": 42,
}

model = CatBoostRegressor(**best_params)

train_pool = Pool(
    X_train,
    y_train,
    cat_features=categorical,
    text_features=text
)

test_pool = Pool(
    X_test,
    y_test,
    cat_features=categorical,
    text_features=text
)

model.fit(train_pool)

y_pred = model.predict(test_pool)

mae = mean_absolute_error(y_test, y_pred)
rmse = np.sqrt(mean_squared_error(y_test, y_pred))
r2 = r2_score(y_test, y_pred)

print("CatBoost + text_features:")
print(f"  MAE:  {mae:,.0f} руб.")
print(f"  RMSE: {rmse:,.0f} руб.")
print(f"  R²:   {r2:.4f}")

model.save_model("../model/catboost_model_v3.cbm")