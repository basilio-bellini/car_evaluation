import re

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
catboost_model.load_model("model/catboost_model_v4.cbm")

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
    "пневма",
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
    "одна",
    "первый",
    "первая",
    "такси",
    "каршеринг",
    "аренда",
    # Сделка
    "обмен"
}

premium = [
    'Porsche',
    'Li Auto (Lixiang)'
    'Lexus',
    'Cadillac',
    'Mercedes-Benz',
    'Land Rover',
    'BMW',
    'Infiniti',
    'Audi',
    'Land Rover',
    'Jaguar',
    'Volvo',
]

def clean_description(text):
    if not isinstance(text, str):
        return ""
    text = text.lower()
    text = text.replace("\n", " ").replace("\r", " ")
    text = re.sub(r'[^\w\s]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


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
    input_data = pd.DataFrame(
        [
            {
                "brand": request.brand,
                "model": request.model,
                "year": request.year,
                "mileage": request.mileage,
                "color": request.color,
                "body_type": request.body_type,
                "auto_class": request.auto_class,
                "owners_number": request.owners_number,
                "accidents": request.accidents,
                "engine_type": request.engine_type,
                "transmission": request.transmission,
                "gear_type": request.gear_type,
                "displacement": request.displacement * 1000,
                "power": request.power,
                "description": request.description,
                "region": request.region,
                "power_per_liter": request.power / request.displacement,
                "is_premium": int(request.brand in premium),
            }
        ]
    )
    input_data["description"] = input_data["description"].apply(clean_description)
    pool = Pool(input_data, cat_features=categorical, text_features=text)
    predicted_price = catboost_model.predict(pool)[0]
    keywords = extract_keywords(request.description)

    shap_values = catboost_model.get_feature_importance(pool, type="ShapValues")
    feature_shap = shap_values[0, :-1]
    feature_names = list(input_data.columns)
    shap_with_names = list(zip(feature_names, feature_shap))
    top5 = sorted(
        [(name, val) for name, val in shap_with_names if name not in ["power_per_liter", "is_premium"]],
        key=lambda x: abs(x[1]),
        reverse=True,
    )[:5]
    shap_factors = [
        {
            "feature": name,
            "value": float(shap_val),
            "display_value": (
                f"+{int(shap_val):,} ₽" if shap_val > 0 else f"{int(shap_val):,} ₽"
            ),
        }
        for name, shap_val in top5
    ]

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
    return {"predicted_price": float(predicted_price),
            "text_keywords": keywords,
            "shap_factors": shap_factors}
