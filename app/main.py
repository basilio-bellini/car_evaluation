from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine
import app.models as models
from app.routers import auth, predict, admin

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Car Price Estimation API",
    description="API для оценки стоимости автомобилей",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(predict.router)
app.include_router(admin.router)


@app.get("/")
def root():
    return {"message": "Car Price Estimation API"}