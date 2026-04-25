from threading import Lock

import paho.mqtt.client as mqtt
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="GreenHouse API")

MQTT_BROKER = "192.168.1.37"
MQTT_PORT = 1488

DEVICE_RELAY_TOPIC = "/device/relay/"
DEVICE_AIR_TOPIC = "/device/air/"
DEVICE_SHINE_TOPIC = "/device/shine/"

SENSOR_HUMIDITY_TOPIC = "/sensor/humidity/"
SENSOR_TEMPERATURE_TOPIC = "/sensor/temperature/"
SENSOR_SHINE_TOPIC = "/sensor/shine/"
SENSOR_WATER_LEVEL_TOPIC = "/sensor/water_lvl"
STATS = "/statistic/"


origins = ["*"]

sensor_data = {"humidity": None, "temperature": None, "last_update": None}

data_lock = Lock()


def on_message(client, userdata, msg):
    global sensor_data
    topic = msg.topic
    payload = msg.payload.decode()

    print(f"Received `{payload}` from `{topic}` topic")

    with data_lock:
        if topic == SENSOR_HUMIDITY_TOPIC:
            sensor_data["humidity"] = payload
        elif topic == SENSOR_TEMPERATURE_TOPIC:
            sensor_data["temperature"] = payload
        elif topic == SENSOR_SHINE_TOPIC:
            sensor_data["shine"] = payload
        elif topic == SENSOR_WATER_LEVEL_TOPIC:
            sensor_data["water_lvl"] = payload


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
    mqtt_client.subscribe(SENSOR_HUMIDITY_TOPIC)
    mqtt_client.subscribe(SENSOR_TEMPERATURE_TOPIC)
    mqtt_client.subscribe(SENSOR_SHINE_TOPIC)
    mqtt_client.subscribe(SENSOR_WATER_LEVEL_TOPIC)
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

    result = mqtt_client.publish(DEVICE_RELAY_TOPIC, state)

    if result.rc == mqtt.MQTT_ERR_SUCCESS:
        return {"status": "success", "sent_state": state}
    else:
        raise HTTPException(status_code=500, detail="Failed to send MQTT message")


@app.post("/devices/air/{state}")
def air(state):
    if state not in ["0", "1"]:
        raise HTTPException(status_code=400, detail="State must be 0 or 1")

    result = mqtt_client.publish(DEVICE_AIR_TOPIC, state)

    if result.rc == mqtt.MQTT_ERR_SUCCESS:
        return {"status": "success", "sent_state": state}
    else:
        raise HTTPException(status_code=500, detail="Failed to send MQTT message")


@app.post("/devices/shine/{state}")
def shine(state):
    if state not in ["0", "1"]:
        raise HTTPException(status_code=400, detail="State must be 0 or 1")

    result = mqtt_client.publish(DEVICE_SHINE_TOPIC, state)

    if result.rc == mqtt.MQTT_ERR_SUCCESS:
        return {"status": "success", "sent_state": state}
    else:
        raise HTTPException(status_code=500, detail="Failed to send MQTT message")


@app.get("/sensor/humidity/")
def get_humidity():
    with data_lock:
        if sensor_data["humidity"] is None:
            raise HTTPException(status_code=404, detail="No data received yet")
        return {
            "humidity": sensor_data["humidity"],
            "last_update": sensor_data["last_update"],
        }


@app.get("/sensor/temperature/")
def get_temp():
    with data_lock:
        if sensor_data["temperature"] is None:
            raise HTTPException(status_code=404, detail="No data received yet")
        return {
            "humidity": sensor_data["humidity"],
            "last_update": sensor_data["last_update"],
        }


@app.get("/sensor/shine/")
def get_shine():
    with data_lock:
        if sensor_data["shine"] is None:
            raise HTTPException(status_code=404, detail="No data received yet")
        return {
            "humidity": sensor_data["humidity"],
            "last_update": sensor_data["last_update"],
        }


@app.get("/sensor/water-lvl/")
def get_water_lvl():
    with data_lock:
        if sensor_data["water_lvl"] is None:
            raise HTTPException(status_code=404, detail="No data received yet")
        return {
            "humidity": sensor_data["humidity"],
            "last_update": sensor_data["last_update"],
        }
