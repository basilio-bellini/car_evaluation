from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.auth import get_admin_user
import app.models as models
import app.schemas as schemas
from typing import List

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/users", response_model=List[schemas.UserAdminResponse])
def get_users(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_admin_user)
):
    users = db.query(models.User).all()
    return users


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_admin_user)
):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден"
        )
    if user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Нельзя удалить самого себя"
        )
    db.delete(user)
    db.commit()


@router.put("/users/{user_id}/role", response_model=schemas.UserAdminResponse)
def change_role(
    user_id: int,
    role: models.RoleEnum,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_admin_user)
):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден"
        )
    user.role = role
    db.commit()
    db.refresh(user)
    return user