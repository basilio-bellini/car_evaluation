from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine
import app.models as models
from app.routers import auth, predict, admin, history
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import FileResponse

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
app.include_router(history.router)

app.mount("/static", StaticFiles(directory="app/static"), name="static")


@app.get("/")
def home():
    return FileResponse("app/templates/home.html")

@app.get("/predict")
def predict_page():
    return FileResponse("app/templates/index.html")

@app.get("/about")
def about():
    return FileResponse("app/templates/about.html")

@app.get("/history")
def history():
    return FileResponse("app/templates/history.html")

@app.get("/admin")
def admin():
    return FileResponse("app/templates/admin.html")

@app.get("/profile")
def profile_page():
    return FileResponse("app/templates/profile.html")

