import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, KFold
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from xgboost import XGBRegressor
import optuna


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


def objective_xgb(trial):
    params = {
        "n_estimators": trial.suggest_int("n_estimators", 100, 1000),
        "learning_rate": trial.suggest_float("learning_rate", 0.01, 0.3),
        "max_depth": trial.suggest_int("max_depth", 4, 10),
        "subsample": trial.suggest_float("subsample", 0.6, 1.0),
        "colsample_bytree": trial.suggest_float("colsample_bytree", 0.6, 1.0),
        "reg_alpha": trial.suggest_float("reg_alpha", 0, 10),
        "reg_lambda": trial.suggest_float("reg_lambda", 0, 10),
        "random_state": 42,
        "verbosity": 0
    }

    kf = KFold(n_splits=5, shuffle=True, random_state=42)
    mae_scores = []

    for train_idx, val_idx in kf.split(X_train):
        x_tr, x_val = X_train.iloc[train_idx], X_train.iloc[val_idx]
        y_tr, y_val = y_train.iloc[train_idx], y_train.iloc[val_idx]

        pipeline_xgb = Pipeline(steps=[
            ("preprocessor", preprocessor),
            ("model", XGBRegressor(**params))
        ])
        pipeline_xgb.fit(x_tr, y_tr)
        y_pred = pipeline_xgb.predict(x_val)
        mae_scores.append(mean_absolute_error(y_val, y_pred))

    return np.mean(mae_scores)

study_xgb = optuna.create_study(direction="minimize")
study_xgb.optimize(objective_xgb, n_trials=50, show_progress_bar=True)

print(f"\nЛучшие параметры XGBoost: {study_xgb.best_params}")
print(f"Лучший MAE: {study_xgb.best_value:,.0f} руб.")

best_pipeline_xgb = Pipeline(steps=[
    ("preprocessor", preprocessor),
    ("model", XGBRegressor(**study_xgb.best_params, random_state=42, verbosity=0))
])
best_pipeline_xgb.fit(X_train, y_train)
y_pred_xgb = best_pipeline_xgb.predict(X_test)

mae = mean_absolute_error(y_test, y_pred_xgb)
rmse = np.sqrt(mean_squared_error(y_test, y_pred_xgb))
r2 = r2_score(y_test, y_pred_xgb)

print("\nXGBoost (оптимизированный):")
print(f"  MAE:  {mae:,.0f} руб.")
print(f"  RMSE: {rmse:,.0f} руб.")
print(f"  R²:   {r2:.4f}")