# Apps/forecasting.py

import os
from pathlib import Path

import torch
import numpy as np
import joblib
from collections import deque
from Apps.model_definition import load_model


DEVICE = torch.device("cpu")
PROJECT_ROOT = Path(__file__).resolve().parent.parent
MODEL_PATH = PROJECT_ROOT / "models" / "iot_lstm_model.pt"
SCALER_PATH = PROJECT_ROOT / "models" / "scaler.pkl"

SEQ_LEN = 60


class ForecastEngine:
    """
    Handles LSTM forecasting with rolling buffer.
    """

    def __init__(self, preload_buffer: bool = False):
        self.model = load_model(MODEL_PATH, DEVICE)
        self.scaler = joblib.load(SCALER_PATH)
        self.buffer = deque(maxlen=SEQ_LEN)

        # Preload is useful for local demos and tests.
        if preload_buffer:
            self._preload_dummy_data()

    def _preload_dummy_data(self):
        """
        Pre-fills buffer with stable dummy readings
        so prediction works immediately.
        """
        dummy_input = [30, 70, 100, 0, 1]

        for _ in range(SEQ_LEN):
            self.buffer.append(dummy_input)

    def update_buffer(self, new_input: list):
        """
        new_input format:
        [temp, humidity, light, room_encoded, motion]
        """

        if len(new_input) != 5:
            raise ValueError("Input must contain 5 features.")

        self.buffer.append(new_input)

    def can_forecast(self) -> bool:
        return len(self.buffer) == SEQ_LEN

    def forecast_next(self):
        """
        Returns predicted next timestep or None.
        """

        if not self.can_forecast():
            return None

        try:
            sequence = np.array(self.buffer)

            # Scale
            sequence_scaled = self.scaler.transform(sequence)

            tensor_input = torch.tensor(
                sequence_scaled,
                dtype=torch.float32
            ).unsqueeze(0)

            with torch.no_grad():
                prediction = self.model(tensor_input)

            prediction = prediction.numpy()
            prediction = self.scaler.inverse_transform(prediction)

            return prediction[0]

        except Exception as e:
            print("Forecasting Error:", e)
            return None


def _env_flag(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


forecast_engine = ForecastEngine(preload_buffer=_env_flag("FORECAST_PRELOAD_BUFFER", False))