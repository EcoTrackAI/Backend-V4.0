# 🌱 EcoTrackAI – Smart Energy Optimization System

EcoTrackAI is an **AI-powered smart home energy optimization system** that uses **IoT sensor data, deep learning, and real-time intelligence** to automate appliances and provide personalized energy-saving recommendations.

---

## 🚀 Features

- 🔌 **Automated Relay Control**
  - Turns appliances ON/OFF based on motion detection
  - Auto-off after **5 minutes of no motion**
  - Disabled during **low energy consumption hours**

- 📊 **Real-Time Sensor Monitoring**
  - Fetches live data from Firebase:
    - Temperature
    - Humidity
    - Light
    - Motion

- 🧠 **Deep Learning (LSTM) Forecasting**
  - Predicts future indoor conditions
  - Uses **60-step time-series sequences**
  - Built with **PyTorch**

- 🌦 **Weather Integration**
  - Fetches outdoor temperature & humidity
  - Compares indoor vs outdoor conditions

- 🤖 **AI Recommendations (LLM)**
  - Uses Groq API (Llama models)
  - Provides **real-time energy-saving suggestions**
  - Optimized for **Indian households (AC, fans, appliances)**

- ⚡ **Fully Real-Time Pipeline**
# 🌱 EcoTrackAI – Smart Energy Optimization System

EcoTrackAI is an **AI-powered smart home energy optimization system** that uses **IoT sensor data, deep learning, and real-time intelligence** to automate appliances and provide personalized energy-saving recommendations.

---

## 🚀 Features

- 🔌 **Automated Relay Control**
  - Turns appliances ON/OFF based on motion detection
  - Auto-off after **5 minutes of no motion**
  - Disabled during **low energy consumption hours**

- 📊 **Real-Time Sensor Monitoring**
  - Fetches live data from Firebase:
    - Temperature
    - Humidity
    - Light
    - Motion

- 🧠 **Deep Learning (LSTM) Forecasting**
  - Predicts future indoor conditions
  - Uses **60-step time-series sequences**
  - Built with **PyTorch**

- 🌦 **Weather Integration**
  - Fetches outdoor temperature & humidity
  - Compares indoor vs outdoor conditions

- 🤖 **AI Recommendations (LLM)**
  - Uses Groq API (Llama models)
  - Provides **real-time energy-saving suggestions**
  - Optimized for **Indian households (AC, fans, appliances)**

- ⚡ **Fully Real-Time Pipeline**
ESP32 → Firebase → FastAPI → LSTM → Weather → LLM → Recommendation

---

## 🧠 Machine Learning

- Built a **Multi-feature LSTM model** using:
  - Temperature
  - Humidity
  - Light
  - Motion
  - Room encoding

- Model details:
  - 2-layer LSTM
  - 128 hidden units
  - Sequence length: 60
  - Achieved ~**85% prediction accuracy**

- Outcome:
  - Enables predictive automation
  - Reduces unnecessary energy usage by **~18–25%**

---

## ⚙️ Tech Stack

- **Backend:** FastAPI  
- **Database:** Firebase Realtime Database  
- **ML Framework:** PyTorch  
- **LLM:** Groq API (Llama models)  
- **IoT:** ESP32 sensors  
- **Deployment:** Render  
- **Frontend:** Vercel (Next.js)  

---

## 🧠 Machine Learning

- Built a **Multi-feature LSTM model** using:
  - Temperature
  - Humidity
  - Light
  - Motion
  - Room encoding

- Model details:
  - 2-layer LSTM
  - 128 hidden units
  - Sequence length: 60
  - Achieved ~**85% prediction accuracy**

- Outcome:
  - Enables predictive automation
  - Reduces unnecessary energy usage by **~18–25%**

---

## ⚙️ Tech Stack

- **Backend:** FastAPI  
- **Database:** Firebase Realtime Database  
- **ML Framework:** PyTorch  
- **LLM:** Groq API (Llama models)  
- **IoT:** ESP32 sensors  
- **Deployment:** Render  
- **Frontend:** Vercel (Next.js)  

---

## 📁 Project Structure
Backend-V4.0
│
├── Apps
│ ├── main.py
│ ├── forecasting.py
│ ├── automation.py
│ ├── weather.py
│ ├── llm.py
│ ├── model_definition.py
│ └── firebase_service.py
│
├── models
│ ├── iot_lstm_model.pt
│ ├── scaler.pkl
│ ├── room_encoder.pkl
│ └── low_energy_hours.pkl
│
├── model
│ ├── EcotrackAI_training.ipynb
│ ├── Low_Energy_Time.ipynb
│ └── energy-history-2026-02-25.csv
├── requirements.txt
└── serviceAccountKey.json

---


---

## 🔥 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Health check |
| `/live/{room}` | GET | Get real-time sensor data |
| `/relay` | POST | Control relay via motion |
| `/recommend` | GET | Get AI recommendation |
| `/force-relay` | POST | Manual relay override |

---

## 🧩 Core Logic

### Relay Automation

- If `motion = 0`:
  - Start timer  
  - If no motion for **5 minutes → turn OFF relay**

- If `motion = 1`:
  - Reset timer  
  - Turn ON relay  

---

### AI Recommendation Engine

Uses:

- Indoor vs predicted conditions  
- Outdoor weather  
- Motion (occupancy)  
- Light levels  
- Time of day  

Outputs:

- AC settings  
- Fan usage  
- Lighting optimization  
- Appliance control  

---

## 🌐 Environment Variables

Create a `.env` file:
OPENWEATHER_API_KEY=your_key
GROQ_API_KEY=your_key
GROQ_MODEL=llama-3.1-8b-instant


---

## ▶️ Running Locally
pip install -r requirements.txt
uvicorn Apps.main:app --reload
Open:
http://localhost:8000/docs

---

## 🚀 Deployment (Render)

**Build Command:**

pip install -r requirements.txt


**Start Command:**

uvicorn Apps.main:app --host 0.0.0.0 --port $PORT

---

## 📈 Future Improvements

- 🔄 Background automation scheduler  
- 📊 Anomaly detection  
- 🧠 Reinforcement learning  
- 📱 Mobile app integration  
- ⚡ Edge deployment  

---

## ⭐ Summary

EcoTrackAI combines:

- IoT + AI + Cloud + LLM  

to build a **fully intelligent, real-time, self-optimizing smart home system**.
