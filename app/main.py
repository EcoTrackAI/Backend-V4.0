from datetime import datetime

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from firebase_admin import db

from app.services.automation import relay_controller
from app.services.firebase_service import initialize_firebase, update_relay_state
from app.services.forecasting import forecast_engine
from app.services.llm import ask_llm
from app.services.weather import get_outdoor_weather


load_dotenv()


ALLOWED_ROOMS = {"bedroom", "living_room"}


app = FastAPI(title="EcoTrackAI Backend", version="4.0")


@app.on_event("startup")
def startup() -> None:
    initialize_firebase()


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://ecotrackai-dashboard.vercel.app",
        "https://ecotrackai-preview.vercel.app",
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _validate_room(room: str) -> None:
    if room not in ALLOWED_ROOMS:
        raise HTTPException(status_code=400, detail="Invalid room name")


def _now() -> str:
    return datetime.now().isoformat()


@app.get("/")
def root() -> dict:
    return {"status": "EcoTrackAI backend running", "timestamp": _now()}


async def get_latest_sensor(room: str) -> dict:
    try:
        ref = db.reference(f"/sensors/{room}")
        data = ref.get()

        if not data:
            raise HTTPException(status_code=404, detail="No sensor data found")

        return {
            "temp": data.get("temperature", 0),
            "humidity": data.get("humidity", 0),
            "light": data.get("light", 0),
            "motion": int(bool(data.get("motion", 0))),
        }
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Firebase error: {exc}") from exc


@app.get("/live/{room}")
async def live_sensor(room: str) -> dict:
    _validate_room(room)
    sensor = await get_latest_sensor(room)
    return {"room": room, "sensor": sensor, "timestamp": _now()}


@app.post("/relay")
async def relay_control(room: str, motion: int) -> dict:
    _validate_room(room)
    if motion not in (0, 1):
        raise HTTPException(status_code=400, detail="Motion must be 0 or 1")

    try:
        state = relay_controller.control(room, motion)
        return {
            "room": room,
            "motion": motion,
            "relay_state": state,
            "timestamp": _now(),
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.get("/recommend")
async def recommend(room: str) -> dict:
    _validate_room(room)

    try:
        sensor = await get_latest_sensor(room)

        temp = sensor["temp"]
        humidity = sensor["humidity"]
        light = sensor["light"]
        motion = sensor["motion"]
        room_encoded = 0 if room == "bedroom" else 1

        forecast_engine.update_buffer([temp, humidity, light, room_encoded, motion])
        predicted = forecast_engine.forecast_next()

        if predicted is None:
            return {"message": "Collecting sequence data for prediction."}

        predicted_temp = float(predicted[0])
        predicted_humidity = float(predicted[1])

        outdoor = get_outdoor_weather()
        outdoor_temp = outdoor.get("outdoor_temp")
        outdoor_humidity = outdoor.get("outdoor_humidity")

        context = {
            "timestamp": _now(),
            "room": room,
            "current_indoor_temp": temp,
            "predicted_indoor_temp": predicted_temp,
            "outdoor_temp": outdoor_temp,
            "temp_difference": (
                predicted_temp - outdoor_temp if outdoor_temp is not None else None
            ),
            "current_humidity": humidity,
            "predicted_humidity": predicted_humidity,
            "outdoor_humidity": outdoor_humidity,
            "humidity_difference": (
                predicted_humidity - outdoor_humidity
                if outdoor_humidity is not None
                else None
            ),
            "motion": motion,
            "light": light,
            "hour": datetime.now().hour,
        }

        recommendation = ask_llm(context)
        return {
            "sensor_data": sensor,
            "forecast_data": context,
            "recommendation": recommendation,
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.post("/force-relay")
async def force_relay(room: str, state: bool) -> dict:
    _validate_room(room)

    try:
        relay_key = f"{room}_light"
        relay_controller.relay_states[relay_key] = state
        update_relay_state(relay_key, state)
        return {"room": room, "forced_state": state, "timestamp": _now()}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
