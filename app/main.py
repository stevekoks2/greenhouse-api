from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="GreenHouse API")

import paho.mqtt.client as mqtt

MQTT_BROKER = "192.168.1.37"
MQTT_PORT = 1488
RELAY_TOPIC = "home/relay"

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

mqtt_client = mqtt.Client()


@app.on_event("startup")
async def startup_event():
    mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
    mqtt_client.loop_start()


@app.get("/")
def root():
    return "GreenHouse API is running"


@app.post("/relay/{state}")
def led(state):

    if state not in ["0", "1"]:
        raise HTTPException(status_code=400, detail="State must be 0 or 1")

    result = mqtt_client.publish(MQTT_TOPIC, state)

    if result.rc == mqtt.MQTT_ERR_SUCCESS:
        return {"status": "success", "sent_state": state}
    else:
        raise HTTPException(status_code=500, detail="Failed to send MQTT message")
