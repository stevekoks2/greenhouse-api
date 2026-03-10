from fastapi import APIRouter

from app.schemas.sensor import ActuatorCommand

router = APIRouter()


@router.post("/command")
def send_command(command: ActuatorCommand):
    if command.command == "off":
        return {"status": "command sent", "device": command.device_id}
