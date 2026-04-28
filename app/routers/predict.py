from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.auth import get_optional_user
from app.database import get_db
import app.models as models
import app.schemas as schemas
from catboost import CatBoostRegressor
import joblib
import pandas as pd
from typing import Optional

router = APIRouter(prefix="/predict", tags=["predict"])

catboost_model = CatBoostRegressor()
catboost_model.load_model("model/catboost_model.cbm")
preprocessor = joblib.load("model/preprocessor.pkl")

numerical = ["year", "mileage", "displacement", "power"]
categorical = ["brand", "model", "color", "body_type", "auto_class",
               "owners_number", "accidents", "engine_type",
               "transmission", "gear_type"]


@router.post("/", response_model=schemas.PredictResponse)
def predict(
    request: schemas.PredictRequest,
    db: Session = Depends(get_db),
    current_user: Optional[models.User] = Depends(get_optional_user)
):
    input_data = pd.DataFrame([{
        "year":          request.year,
        "mileage":       request.mileage,
        "displacement":  request.displacement,
        "power":         request.power,
        "brand":         request.brand,
        "model":         request.model,
        "color":         request.color,
        "body_type":     request.body_type,
        "auto_class":    request.auto_class,
        "owners_number": request.owners_number,
        "accidents":     request.accidents,
        "engine_type":   request.engine_type,
        "transmission":  request.transmission,
        "gear_type":     request.gear_type
    }])

    input_processed = preprocessor.transform(input_data)

    predicted_price = catboost_model.predict(input_processed)[0]

    if current_user:
        prediction = models.Prediction(
            user_id=current_user.id,
            brand=request.brand,
            model=request.model,
            year=request.year,
            mileage=request.mileage,
            color=request.color,
            body_type=request.body_type,
            auto_class=request.auto_class,
            owners_number=request.owners_number,
            accidents=request.accidents,
            engine_type=request.engine_type,
            transmission=request.transmission,
            gear_type=request.gear_type,
            displacement=request.displacement,
            power=request.power,
            predicted_price=float(predicted_price)
        )
        db.add(prediction)
        db.commit()

    return {"predicted_price": float(predicted_price)}