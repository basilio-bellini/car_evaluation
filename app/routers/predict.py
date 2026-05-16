import re
from collections import Counter

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.auth import get_optional_user
from app.database import get_db
import app.models as models
import app.schemas as schemas
from catboost import CatBoostRegressor, Pool
import pandas as pd
from typing import Optional

router = APIRouter(prefix="/predict", tags=["predict"])

catboost_model = CatBoostRegressor()
catboost_model.load_model("model/catboost_model_v3.cbm")

numerical = ["year", "mileage", "displacement", "power", "owners_number"]
categorical = ["brand", "model", "color", "body_type", "auto_class",
               "accidents", "engine_type", "transmission", "gear_type", "region"]
text = ["description"]

VALUABLE_KEYWORDS = {
    # Опции
    "кожа",
    "кожаный",
    "кожаные",
    "алькантара",
    "панорама",
    "панорамный",
    "люк",
    "камера",
    "парктроник",
    "парковка",
    "навигация",
    "навигатор",
    "подогрев",
    "подогреваемые",
    "вентиляция",
    "круиз",
    "адаптивный",
    "xenon",
    "ксенон",
    "led",
    "светодиод",
    "карplay",
    "carplay",
    "android",
    "bose",
    "jbl",
    "harman",
    "meridian",
    # Состояние
    "дилер",
    "официальный",
    "гарантия",
    "сервис",
    "обслуживание",
    "техобслуживание",
    "ремонт",
    "замена",
    "новый",
    "новые",
    "битый",
    "небитый",
    "крашеный",
    "некрашеный",
    "ржавчина",
    "коррозия",
    # Комплектация
    "максимальная",
    "максимальный",
    "полная",
    "полный",
    "базовая",
    "люкс",
    "премиум",
    "executive",
    # История
    "один",
    "одна",
    "первый",
    "первая",
    "такси",
    "каршеринг",
    "аренда",
}


def extract_keywords(description: str, top_n: int = 5) -> list[str]:
    if not description:
        return []

    words = re.findall(r"[а-яёa-zA-Z]{3,}", description.lower())

    valuable = [w for w in words if w in VALUABLE_KEYWORDS]

    if not valuable:
        return []

    from collections import Counter

    counts = Counter(valuable)
    return [word for word, _ in counts.most_common(top_n)]


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
        "gear_type":     request.gear_type,
        "region":        request.region,
        "description":   request.description,
    }])

    pool = Pool(input_data, cat_features=categorical, text_features=text)
    predicted_price = catboost_model.predict(pool)[0]
    keywords = extract_keywords(request.description)

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
            description=request.description,
            region=request.region,
            predicted_price=float(predicted_price)
        )
        db.add(prediction)
        db.commit()

    return {"predicted_price": float(predicted_price), "text_keywords": keywords}
