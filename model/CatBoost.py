import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, KFold
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from catboost import CatBoostRegressor, Pool
import optuna

df = pd.read_csv("../data/processed/cars_v3.csv")
X = df.drop(columns=["price", "url", "description"])
y = df["price"]

categorical = ["brand", "model", "color", "body_type", "auto_class",
               "accidents", "engine_type", "transmission", "gear_type", "region"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

def objective(trial):
    params = {
        "iterations": trial.suggest_int("iterations", 300, 2000),
        "learning_rate": trial.suggest_float("learning_rate", 0.01, 0.1),
        "depth": trial.suggest_int("depth", 4, 10),
        "l2_leaf_reg": trial.suggest_float("l2_leaf_reg", 1, 10),
        "bagging_temperature": trial.suggest_float("bagging_temperature", 0, 5),
        "loss_function": "RMSE",
        "random_seed": 42,
        "verbose": 0,
    }

    kf = KFold(n_splits=3, shuffle=True, random_state=42)
    scores = []

    for train_idx, val_idx in kf.split(X_train):
        x_tr, x_val = X_train.iloc[train_idx], X_train.iloc[val_idx]
        y_tr, y_val = y_train.iloc[train_idx], y_train.iloc[val_idx]

        train_pool = Pool(x_tr, y_tr, cat_features=categorical)
        val_pool = Pool(x_val, y_val, cat_features=categorical)

        model = CatBoostRegressor(**params)
        model.fit(train_pool, eval_set=val_pool, verbose=0)

        pred = model.predict(x_val)
        scores.append(mean_absolute_error(y_val, pred))

    return np.mean(scores)


study = optuna.create_study(direction="minimize")
study.optimize(objective, n_trials=50, show_progress_bar=True)

print(f"\nЛучшие параметры: {study.best_params}")
print(f"Лучший MAE: {study.best_value:,.0f} руб.")

best_params = study.best_params
best_params.update({"random_seed": 42, "verbose": 0})
best_model = CatBoostRegressor(**best_params)
best_model.fit(
    X_train,
    y_train,
    cat_features=categorical,
    verbose=0
)
y_pred_best = best_model.predict(X_test)

mae = mean_absolute_error(y_test, y_pred_best)
rmse = np.sqrt(mean_squared_error(y_test, y_pred_best))
r2 = r2_score(y_test, y_pred_best)

print("\nCatBoost (оптимизированный):")
print(f"  MAE:  {mae:,.0f} руб.")
print(f"  RMSE: {rmse:,.0f} руб.")
print(f"  R²:   {r2:.4f}")
