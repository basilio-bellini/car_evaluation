import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, KFold
from sklearn.preprocessing import StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from catboost import CatBoostRegressor, Pool
import optuna
import joblib

df = pd.read_csv("../data/processed/cars.csv")
X = df.drop(columns=["price", "url", "description"])
y = df["price"]

numerical = ["year", "mileage", "displacement", "power"]
categorical = ["brand", "model", "color", "body_type", "auto_class",
               "owners_number", "accidents", "engine_type",
               "transmission", "gear_type"]


preprocessor_cat = ColumnTransformer(transformers=[
    ("num", StandardScaler(), numerical)
], remainder="passthrough")

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)
X_train_cat = preprocessor_cat.fit_transform(X_train)
X_test_cat = preprocessor_cat.transform(X_test)

cat_feature_indices = list(range(len(numerical), len(numerical) + len(categorical)))


def objective(trial):
    params = {
        "iterations": trial.suggest_int("iterations", 100, 2000),
        "learning_rate": trial.suggest_float("learning_rate", 0.01, 0.3),
        "depth": trial.suggest_int("depth", 4, 10),
        "l2_leaf_reg": trial.suggest_float("l2_leaf_reg", 1, 10),
        "bagging_temperature": trial.suggest_float("bagging_temperature", 0, 1),
        "random_seed": 42,
        "verbose": 0,
    }

    kf = KFold(n_splits=5, shuffle=True, random_state=42)
    mae_scores = []

    for train_idx, val_idx in kf.split(X_train_cat):
        x_tr, x_val = X_train_cat[train_idx], X_train_cat[val_idx]
        y_tr, y_val = y_train.iloc[train_idx], y_train.iloc[val_idx]

        train_pool = Pool(x_tr, y_tr, cat_features=cat_feature_indices)

        model = CatBoostRegressor(**params)
        model.fit(train_pool, verbose=0)

        y_pred = model.predict(x_val)
        mae_scores.append(mean_absolute_error(y_val, y_pred))

    return np.mean(mae_scores)


study = optuna.create_study(direction="minimize")
study.optimize(objective, n_trials=50, show_progress_bar=True)

print(f"\nЛучшие параметры: {study.best_params}")
print(f"Лучший MAE: {study.best_value:,.0f} руб.")

best_params = study.best_params
best_params.update({"random_seed": 42, "verbose": 0})
best_model = CatBoostRegressor(**best_params)
best_train_pool = Pool(X_train_cat, y_train, cat_features=cat_feature_indices)
best_model.fit(best_train_pool)
y_pred_best = best_model.predict(X_test_cat)

mae = mean_absolute_error(y_test, y_pred_best)
rmse = np.sqrt(mean_squared_error(y_test, y_pred_best))
r2 = r2_score(y_test, y_pred_best)

print("\nCatBoost (оптимизированный):")
print(f"  MAE:  {mae:,.0f} руб.")
print(f"  RMSE: {rmse:,.0f} руб.")
print(f"  R²:   {r2:.4f}")


best_model.save_model("../model/catboost_model.cbm")
joblib.dump(preprocessor_cat, "../model/preprocessor.pkl")
print("Модель и препроцессор сохранены!")
