from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="GreenHouse API")

import paho.mqtt.client as mqtt

MQTT_BROKER = "192.168.1.37"
MQTT_PORT = 1488
RELAY_TOPIC = "home/relay"
HUMIDITY_TOPIC = "home/sensor/humidity"

origins = ["*"]


def on_message(client, userdata, msg):
    print(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic")


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


@app.post("/devices/relay/{state}")
def relay(state):

    if state not in ["0", "1"]:
        raise HTTPException(status_code=400, detail="State must be 0 or 1")

    result = mqtt_client.publish(RELAY_TOPIC, state)

    if result.rc == mqtt.MQTT_ERR_SUCCESS:
        return {"status": "success", "sent_state": state}
    else:
        raise HTTPException(status_code=500, detail="Failed to send MQTT message")


@app.get("/sensors/humidity/")
def humidity():
    mqtt_client.subscribe(HUMIDITY_TOPIC)
    mqtt_client.on_message = on_message
    mqtt_client.unsubscribe(HUMIDITY_TOPIC)
    return True
