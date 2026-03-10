from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import controls, sensors

app = FastAPI(
    title="GreenHouse Control API",
    description="GreenHouse Control API",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[""],  # разрешаем все источники
    allow_credentials=True,
    allow_methods=[""],
    allow_headers=["*"],
)

app.include_router(sensors.router, prefix="/sensors", tags=["sensors"])
app.include_router(controls.router, prefix="/controls", tags=["controls"])


@app.get("/")
async def root():
    return {"message": "Greenhouse API is running", "status": "ok"}
