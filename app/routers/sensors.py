from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import SensorDataDB
from app.schemas.sensor import SensorData

router = APIRouter()


@router.post("/data", status_code=status.HTTP_201_CREATED)
async def receive_sensor_data(data: SensorData, db: Session = Depends(get_db)):
    db_data = SensorDataDB(
        device_id=data.device_id,
        sensor_type=data.sensor_type,
        value=data.value,
        unit=data.unit,
        timestamp=data.timestamp or datetime.utcnow(),
    )

    db.add(db_data)
    db.commit()
    db.refresh(db_data)

    return {
        "status": "received",
        "id": db_data.id,
        "device": data.device_id,
        "timestamp": db_data.timestamp,
    }


@router.get("{device_id}/latest")
async def get_latest(device_id: str, db: Session = Depends(get_db)):
    data = (
        db.query(SensorDataDB)
        .filter(SensorDataDB.device_id == device_id)
        .order_by(desc(SensorDataDB.timestamp))
        .first()
    )

    if not data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No data found for this device",
        )

    return {
        "device_id": data.device_id,
        "sensor_type": data.sensor_type,
        "value": data.value,
        "unit": data.unit,
        "timestamp": data.timestamp,
    }


@router.get("/{device_id}/history")
async def get_history(
    device_id: str, hours: int = 24, limit: int = 1000, db: Session = Depends(get_db)
):
    cutoff = datetime.utcnow() - timedelta(hours=hours)

    data = (
        db.query(SensorDataDB)
        .filter(SensorDataDB.device_id == device_id, SensorDataDB.timestamp > cutoff)
        .order_by(SensorDataDB.timestamp.desc())
        .limit(limit)
        .all()
    )

    return {
        "device_id": device_id,
        "period": f"last {hours} hours",
        "count": len(data),
        "data": [
            {"value": d.value, "unit": d.unit, "timestamp": d.timestamp} for d in data
        ],
    }
