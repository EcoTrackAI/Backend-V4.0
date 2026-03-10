# Apps/forecasting.py

import torch
import numpy as np
import joblib
from collections import deque
from Apps.model_definition import load_model


DEVICE = torch.device("cpu")
MODEL_PATH = "models/iot_lstm_model.pt"
SCALER_PATH = "models/scaler.pkl"

SEQ_LEN = 60


class ForecastEngine:
    """
    Handles LSTM forecasting with rolling buffer.
    """

    def __init__(self, preload_buffer: bool = True):
        self.model = load_model(MODEL_PATH, DEVICE)
        self.scaler = joblib.load(SCALER_PATH)
        self.buffer = deque(maxlen=SEQ_LEN)

        # 🔥 Preload buffer for testing
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


forecast_engine = ForecastEngine(preload_buffer=True)