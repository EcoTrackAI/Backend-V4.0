import time
import joblib
from datetime import datetime
from pathlib import Path
from Apps.firebase_service import update_relay_state


LOW_ENERGY_PATH = Path("models/low_energy_hours.pkl")


class RelayController:
    """
    Handles per-room relay automation.
    """

    def __init__(self):
        self.low_energy_hours = self._load_low_energy_hours()

        self.motion_start_time = {}

        self.relay_states = {}

    def _load_low_energy_hours(self):
        if LOW_ENERGY_PATH.exists():
            try:
                hours = joblib.load(LOW_ENERGY_PATH)
                return set(hours)
            except Exception:
                return set()
        return set()

    def _is_low_energy_window(self):
        current_hour = datetime.now().hour
        return current_hour in self.low_energy_hours

    def control(self, room: str, motion: int, timeout_seconds: int = 60) -> bool:
        """
        room: "bedroom" or "living_room"
        motion: 0 or 1
        """

        relay_key = f"{room}_light"

        if relay_key not in self.relay_states:
            self.relay_states[relay_key] = True
            self.motion_start_time[relay_key] = None

        if self._is_low_energy_window():
            update_relay_state(relay_key, self.relay_states[relay_key])
            return self.relay_states[relay_key]

        current_time = time.time()

        if motion == 0:
            if self.motion_start_time[relay_key] is None:
                self.motion_start_time[relay_key] = current_time
            elif current_time - self.motion_start_time[relay_key] >= timeout_seconds:
                self.relay_states[relay_key] = False
        else:
            self.motion_start_time[relay_key] = None
            self.relay_states[relay_key] = True

        update_relay_state(relay_key, self.relay_states[relay_key])

        return self.relay_states[relay_key]


relay_controller = RelayController()
