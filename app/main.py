import asyncio
from threading import Lock

import paho.mqtt.client as mqtt
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="GreenHouse API")

MQTT_BROKER = "192.168.1.37"
MQTT_PORT = 1488
RELAY_TOPIC = "home/relay"
HUMIDITY_TOPIC = "home/sensor/humidity"

origins = ["*"]

# Хранилище для последних значений датчиков
sensor_data = {"humidity": None, "temperature": None, "last_update": None}

data_lock = Lock()


def on_message(client, userdata, msg):
    global sensor_data
    topic = msg.topic
    payload = msg.payload.decode()

    print(f"Received `{payload}` from `{topic}` topic")

    # Сохраняем данные в зависимости от топика
    with data_lock:
        if topic == HUMIDITY_TOPIC:
            sensor_data["humidity"] = payload


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

mqtt_client = mqtt.Client()
mqtt_client.on_message = on_message


@app.on_event("startup")
async def startup_event():
    mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
    # Подписываемся на все нужные топики при старте
    mqtt_client.subscribe(HUMIDITY_TOPIC)
    mqtt_client.subscribe("home/sensor/#")  # можно использовать wildcard
    mqtt_client.loop_start()


@app.on_event("shutdown")
async def shutdown_event():
    mqtt_client.loop_stop()
    mqtt_client.disconnect()


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
def get_humidity():
    with data_lock:
        if sensor_data["humidity"] is None:
            raise HTTPException(status_code=404, detail="No data received yet")
        return {
            "humidity": sensor_data["humidity"],
            "last_update": sensor_data["last_update"],
        }


@app.get("/sensors/all/")
def get_all_sensors():
    with data_lock:
        return sensor_data
