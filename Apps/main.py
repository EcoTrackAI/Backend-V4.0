from datetime import datetime

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from Apps.automation import relay_controller
from Apps.db import get_latest_sensor_data, update_relay_state_db
from Apps.forecasting import forecast_engine
from Apps.llm import ask_llm
from Apps.weather import get_outdoor_weather


load_dotenv()

ALLOWED_ROOMS = {"bedroom", "living_room"}

app = FastAPI(
    title="EcoTrackAI Backend",
    version="5.0 (PostgreSQL Edition)"
)

# -----------------------------------
# CORS CONFIGURATION
# -----------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://ecotrackai-dashboard.vercel.app",
        "https://ecotrackai-preview.vercel.app",
        "http://localhost:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------------
# HEALTH CHECK
# -----------------------------------

@app.get("/")
def root():
    return {
        "status": "EcoTrackAI backend running (PostgreSQL)",
        "timestamp": datetime.now().isoformat()
    }


# -----------------------------------
# GET LATEST SENSOR DATA (POSTGRESQL)
# -----------------------------------

async def get_latest_sensor(room: str):

    data = get_latest_sensor_data(room)

    if not data:
        raise HTTPException(404, "No sensor data found")

    return data


# -----------------------------------
# LIVE SENSOR ENDPOINT
# -----------------------------------

@app.get("/live/{room}")
async def live_sensor(room: str):

    if room not in ALLOWED_ROOMS:
        raise HTTPException(400, "Invalid room name")

    sensor = await get_latest_sensor(room)

    return {
        "room": room,
        "sensor": sensor,
        "timestamp": datetime.now().isoformat()
    }


# -----------------------------------
# RELAY CONTROL (AUTO)
# -----------------------------------

@app.post("/relay")
async def relay_control(room: str, motion: int):

    if motion not in [0, 1]:
        raise HTTPException(400, "Motion must be 0 or 1")

    if room not in ALLOWED_ROOMS:
        raise HTTPException(400, "Invalid room name")

    try:
        state = relay_controller.control(room, motion)

        return {
            "room": room,
            "motion": motion,
            "relay_state": state,
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        raise HTTPException(500, str(e))


# -----------------------------------
# AI RECOMMENDATION (REALTIME)
# -----------------------------------

@app.get("/recommend")
async def recommend(room: str):

    if room not in ALLOWED_ROOMS:
        raise HTTPException(400, "Invalid room name")

    try:

        # Fetch latest sensor data from PostgreSQL
        sensor = await get_latest_sensor(room)

        temp = sensor["temp"]
        humidity = sensor["humidity"]
        light = sensor["light"]
        motion = sensor["motion"]

        room_encoded = 0 if room == "bedroom" else 1

        # Update LSTM buffer
        forecast_engine.update_buffer([
            temp,
            humidity,
            light,
            room_encoded,
            motion
        ])

        predicted = forecast_engine.forecast_next()

        # Handle prediction safely
        if predicted is None:
            predicted_temp = temp
            predicted_humidity = humidity
        else:
            try:
                predicted_temp = float(predicted[0])
                predicted_humidity = float(predicted[1])
            except:
                predicted_temp = temp
                predicted_humidity = humidity

        # Get outdoor weather
        outdoor = get_outdoor_weather()

        outdoor_temp = outdoor.get("outdoor_temp", temp)
        outdoor_humidity = outdoor.get("outdoor_humidity", humidity)

        temp_difference = predicted_temp - outdoor_temp
        humidity_difference = predicted_humidity - outdoor_humidity

        # Context for LLM
        context = {
            "timestamp": datetime.now().isoformat(),
            "room": room,

            "current_indoor_temp": temp,
            "predicted_indoor_temp": predicted_temp,
            "outdoor_temp": outdoor_temp,
            "temp_difference": temp_difference,

            "current_humidity": humidity,
            "predicted_humidity": predicted_humidity,
            "outdoor_humidity": outdoor_humidity,
            "humidity_difference": humidity_difference,

            "motion": motion,
            "light": light,
            "hour": datetime.now().hour
        }

        recommendation = ask_llm(context)

        return {
            "sensor_data": sensor,
            "forecast_data": context,
            "recommendation": recommendation
        }

    except Exception as e:
        raise HTTPException(500, str(e))


# -----------------------------------
# FORCE RELAY (MANUAL OVERRIDE)
# -----------------------------------

@app.post("/force-relay")
async def force_relay(room: str, state: bool):

    if room not in ALLOWED_ROOMS:
        raise HTTPException(400, "Invalid room name")

    try:
        relay_key = f"{room}_light"

        # Update internal state
        relay_controller.relay_states[relay_key] = state

        # Update PostgreSQL
        update_relay_state_db(relay_key, state)

        return {
            "room": room,
            "forced_state": state,
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        raise HTTPException(500, str(e))