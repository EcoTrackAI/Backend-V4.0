# EcoTrackAI Backend (v4)

FastAPI backend for smart-home energy optimization using Firebase, LSTM forecasting, weather context, and LLM recommendations.

## What This Service Does

- Reads live room sensor data from Firebase Realtime Database
- Applies motion-driven relay automation with inactivity timeout
- Forecasts short-term indoor conditions using an LSTM model
- Fetches outdoor weather context from OpenWeather
- Generates concise energy recommendations via Groq LLM API

## Project Layout

```
Backend-V4.0/
  app/
    __init__.py
    main.py               # Primary FastAPI implementation
    services/
      __init__.py
      automation.py
      firebase_service.py
      forecasting.py
      llm.py
      model_definition.py
      weather.py
  models/
    iot_lstm_model.pt
    scaler.pkl
    room_encoder.pkl
    low_energy_hours.pkl
  training/
    EcotrackAI_training.ipynb
    Low_Energy_Time.ipynb
    energy-history-2026-02-25.csv
  requirements.txt
  .gitignore
  README.md
```

## API Endpoints

- `GET /` health check
- `GET /live/{room}` latest sensor values for `bedroom` or `living_room`
- `POST /relay?room=<room>&motion=<0|1>` automated relay logic
- `GET /recommend?room=<room>` forecast + weather + recommendation pipeline
- `POST /force-relay?room=<room>&state=<true|false>` manual relay override

## Environment Variables

Create a `.env` file (or set platform env vars):

- `OPENWEATHER_API_KEY` required for weather integration
- `WEATHER_CITY` optional, default `Kolkata`
- `GROQ_API_KEY` required for LLM recommendation
- `GROQ_MODEL` optional, default `llama-3.1-8b-instant`
- `GROQ_URL` optional, default Groq chat completions URL
- `FIREBASE_DATABASE_URL` optional if using default project URL
- `FIREBASE_CREDENTIALS_PATH` optional absolute/relative path to service account JSON
- `FIREBASE_CREDENTIALS_JSON` optional raw JSON string for cloud secret injection
- `FORECAST_PRELOAD_BUFFER` optional (`true`/`false`), default `false`

Firebase credentials resolution order:

1. `FIREBASE_CREDENTIALS_JSON`
2. `FIREBASE_CREDENTIALS_PATH`
3. local `serviceAccountKey.json`
4. default application credentials (cloud runtime)

## Run Locally

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open docs at `http://localhost:8000/docs`.

## Render Deployment

- Build command:

```bash
pip install -r requirements.txt
```

- Start command:

```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

- Recommended secret setup on Render:
  - Set `FIREBASE_CREDENTIALS_JSON` from secret manager
  - Set API keys (`OPENWEATHER_API_KEY`, `GROQ_API_KEY`)
  - Do not commit any credential files
