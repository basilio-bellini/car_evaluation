from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from starlette import status

from app.auth import get_current_user
from app.database import get_db
import app.models as models
import app.schemas as schemas

from typing import List


router = APIRouter(prefix="/history", tags=["history"])


@router.get("/", response_model=List[schemas.PredictionResponse])
def get_history(
        db: Session = Depends(get_db),
        current_user: models.User = Depends(get_current_user),
):
    history = (db.query(models.Prediction)
               .filter(models.Prediction.user_id == current_user.id)
               .order_by(models.Prediction.created_at.desc())
               .all())
    return history


@router.get("/{prediction_id}", response_model=schemas.PredictionResponse)
def get_prediction(
        prediction_id: int,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(get_current_user),
):
    prediction = db.query(models.Prediction).filter(models.Prediction.id == prediction_id,
                                                             models.Prediction.user_id == current_user.id).first()
    if prediction is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Предсказание по этому id не найдено")
    return prediction


@router.delete("/{prediction_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_prediction(
        prediction_id: int,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(get_current_user),
):
    prediction = db.query(models.Prediction).filter(models.Prediction.id == prediction_id,
                                                    models.Prediction.user_id == current_user.id).first()
    if prediction is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Предсказание по этому id не найдено")
    db.delete(prediction)
    db.commit()