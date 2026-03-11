from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import os
import asyncpg
from dotenv import load_dotenv

from Apps.automation import relay_controller
from Apps.forecasting import forecast_engine
from Apps.weather import get_outdoor_weather
from Apps.llm import ask_llm
from Apps.firebase_service import update_relay_state


load_dotenv()

POSTGRES_URL = os.getenv("DATABASE_URL")

if not POSTGRES_URL:
    raise ValueError("DATABASE_URL not found in environment variables")

db_pool = None


app = FastAPI(
    title="EcoTrackAI Backend",
    version="2.0"
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
# DATABASE CONNECTION
# -----------------------------------

@app.on_event("startup")
async def startup():
    global db_pool
    try:
        db_pool = await asyncpg.create_pool(
            POSTGRES_URL,
            min_size=2,
            max_size=10
        )
        print("PostgreSQL connected")
    except Exception as e:
        print("Database connection failed:", e)


@app.on_event("shutdown")
async def shutdown():
    global db_pool
    if db_pool:
        await db_pool.close()
        print("PostgreSQL closed")


# -----------------------------------
# HEALTH CHECK
# -----------------------------------

@app.get("/")
def root():
    return {
        "status": "EcoTrackAI backend running",
        "timestamp": datetime.now().isoformat()
    }


# -----------------------------------
# GET LATEST SENSOR DATA
# -----------------------------------

async def get_latest_sensor(room: str):

    if not db_pool:
        raise HTTPException(500, "Database not initialized")

    async with db_pool.acquire() as conn:

        row = await conn.fetchrow(
            """
            SELECT temperature, humidity, light, motion
            FROM room_sensors
            WHERE room_id = $1
            ORDER BY timestamp DESC
            LIMIT 1
            """,
            room
        )

        if not row:
            raise HTTPException(404, "No sensor data found")

        return {
            "temp": row["temperature"],
            "humidity": row["humidity"],
            "light": row["light"],
            "motion": row["motion"]
        }


# -----------------------------------
# LIVE SENSOR ENDPOINT
# -----------------------------------

@app.get("/live/{room}")
async def live_sensor(room: str):

    if room not in ["bedroom", "living_room"]:
        raise HTTPException(400, "Invalid room name")

    sensor = await get_latest_sensor(room)

    return {
        "room": room,
        "sensor": sensor,
        "timestamp": datetime.now().isoformat()
    }


# -----------------------------------
# RELAY CONTROL
# -----------------------------------

@app.post("/relay")
async def relay_control(room: str, motion: int):

    if motion not in [0, 1]:
        raise HTTPException(status_code=400, detail="Motion must be 0 or 1")

    if room not in ["bedroom", "living_room"]:
        raise HTTPException(status_code=400, detail="Invalid room name")

    try:
        state = relay_controller.control(room, motion)

        return {
            "room": room,
            "motion": motion,
            "relay_state": state,
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# -----------------------------------
# AI RECOMMENDATION (REALTIME)
# -----------------------------------

@app.get("/recommend")
async def recommend(room: str):

    if room not in ["bedroom", "living_room"]:
        raise HTTPException(status_code=400, detail="Invalid room name")

    try:

        # Fetch latest sensor data
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

        if predicted is None:
            return {
                "message": "Collecting sequence data for prediction."
            }

        predicted_temp = float(predicted[0])
        predicted_humidity = float(predicted[1])

        # Get outdoor weather
        outdoor = get_outdoor_weather()

        outdoor_temp = outdoor.get("outdoor_temp")
        outdoor_humidity = outdoor.get("outdoor_humidity")

        temp_difference = None
        humidity_difference = None

        if outdoor_temp is not None:
            temp_difference = predicted_temp - outdoor_temp

        if outdoor_humidity is not None:
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
        raise HTTPException(status_code=500, detail=str(e))


# -----------------------------------
# FORCE RELAY (MANUAL OVERRIDE)
# -----------------------------------

@app.post("/force-relay")
async def force_relay(room: str, state: bool):

    if room not in ["bedroom", "living_room"]:
        raise HTTPException(status_code=400, detail="Invalid room name")

    try:

        relay_controller.relay_states[f"{room}_light"] = state

        update_relay_state(
            f"{room}_light",
            state
        )

        return {
            "room": room,
            "forced_state": state,
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
