import optuna
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, KFold
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from lightgbm import LGBMRegressor


df = pd.read_csv("../data/processed/cars_v3.csv")
X = df.drop(columns=["price", "url", "description"])
y = df["price"]

numerical = ["year", "mileage", "displacement", "power", "owners_number"]
categorical = ["brand", "model", "color", "body_type", "auto_class",
               "accidents", "engine_type", "transmission", "gear_type", "region"]

preprocessor = ColumnTransformer(transformers=[
    ("num", "passthrough", numerical),
    ("cat", OneHotEncoder(handle_unknown="ignore"), categorical)
])

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)


def objective_lgbm(trial):
    params = {
        "n_estimators": trial.suggest_int("n_estimators", 300, 2000),
        "learning_rate": trial.suggest_float("learning_rate", 0.01, 0.1),
        "num_leaves": trial.suggest_int("num_leaves", 20, 200),
        "max_depth": trial.suggest_int("max_depth", 4, 12),
        "min_child_samples": trial.suggest_int("min_child_samples", 5, 100),
        "subsample": trial.suggest_float("subsample", 0.6, 1.0),
        "colsample_bytree": trial.suggest_float("colsample_bytree", 0.6, 1.0),
        "reg_alpha": trial.suggest_float("reg_alpha", 0, 10),
        "reg_lambda": trial.suggest_float("reg_lambda", 0, 10),
        "random_state": 42,
        "n_jobs": -1,
        "verbose": -1
    }

    kf = KFold(n_splits=5, shuffle=True, random_state=42)
    mae_scores = []

    for train_idx, val_idx in kf.split(X_train):
        x_tr, x_val = X_train.iloc[train_idx], X_train.iloc[val_idx]
        y_tr, y_val = y_train.iloc[train_idx], y_train.iloc[val_idx]

        pipeline_lgbm = Pipeline(steps=[
            ("preprocessor", preprocessor),
            ("model", LGBMRegressor(**params))
        ])
        pipeline_lgbm.fit(x_tr, y_tr)
        y_pred = pipeline_lgbm.predict(x_val)
        mae_scores.append(mean_absolute_error(y_val, y_pred))

    return np.mean(mae_scores)

study_lgbm = optuna.create_study(direction="minimize")
study_lgbm.optimize(objective_lgbm, n_trials=50, show_progress_bar=True)

print(f"\nЛучшие параметры LightGBM: {study_lgbm.best_params}")
print(f"Лучший MAE: {study_lgbm.best_value:,.0f} руб.")

best_pipeline_lgbm = Pipeline(steps=[
    ("preprocessor", preprocessor),
    ("model", LGBMRegressor(**study_lgbm.best_params, random_state=42))
])
best_pipeline_lgbm.fit(X_train, y_train)
y_pred_xgb = best_pipeline_lgbm.predict(X_test)

mae = mean_absolute_error(y_test, y_pred_xgb)
rmse = np.sqrt(mean_squared_error(y_test, y_pred_xgb))
r2 = r2_score(y_test, y_pred_xgb)

print("\nLightGBM (оптимизированный):")
print(f"  MAE:  {mae:,.0f} руб.")
print(f"  RMSE: {rmse:,.0f} руб.")
print(f"  R²:   {r2:.4f}")
