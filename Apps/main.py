# Apps/main.py

from fastapi import FastAPI, HTTPException
from datetime import datetime

from Apps.automation import relay_controller
from Apps.forecasting import forecast_engine
from Apps.weather import get_outdoor_weather
from Apps.llm import ask_mistral
from Apps.firebase_service import update_relay_state


app = FastAPI(
    title="EcoTrackAI Backend",
    version="1.2"
)


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
# RELAY CONTROL
# -----------------------------------

@app.post("/relay")
def relay_control(room: str, motion: int):

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
# AI RECOMMENDATION
# -----------------------------------

@app.get("/recommend")
def recommend(
    room: str,
    motion: int,
    temp: float,
    humidity: float,
    light: float
):

    if motion not in [0, 1]:
        raise HTTPException(status_code=400, detail="Motion must be 0 or 1")

    if room not in ["bedroom", "living_room"]:
        raise HTTPException(status_code=400, detail="Invalid room name")

    room_encoded = 0 if room == "bedroom" else 1

    try:

        # -------------------------
        # UPDATE LSTM BUFFER
        # -------------------------

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

        # -------------------------
        # WEATHER DATA
        # -------------------------

        outdoor = get_outdoor_weather()

        outdoor_temp = outdoor.get("outdoor_temp")
        outdoor_humidity = outdoor.get("outdoor_humidity")

        temp_difference = None
        humidity_difference = None

        if outdoor_temp is not None:
            temp_difference = predicted_temp - outdoor_temp

        if outdoor_humidity is not None:
            humidity_difference = predicted_humidity - outdoor_humidity

        # -------------------------
        # CONTEXT FOR LLM
        # -------------------------

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

        # -------------------------
        # LLM RECOMMENDATION
        # -------------------------

        recommendation = ask_mistral(context)

        return {
            "forecast_data": context,
            "recommendation": recommendation
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# -----------------------------------
# FORCE RELAY (MANUAL OVERRIDE)
# -----------------------------------

@app.post("/force-relay")
def force_relay(room: str, state: bool):

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