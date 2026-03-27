import time
import joblib
from datetime import datetime
from pathlib import Path
from app.services.firebase_service import update_relay_state


PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
LOW_ENERGY_PATH = PROJECT_ROOT / "models" / "low_energy_hours.pkl"
AUTO_OFF_TIMEOUT = 300  # 5 minutes


class RelayController:
    """
    Handles per-room relay automation with motion-based timeout.
    """

    def __init__(self):
        self.low_energy_hours = self._load_low_energy_hours()

        # stores last time motion became 0
        self.last_zero_motion_time = {}

        # relay states
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
        return datetime.now().hour in self.low_energy_hours

    def control(self, room: str, motion: int) -> bool:
        """
        room: bedroom | living_room
        motion: 0 or 1
        """

        relay_key = f"{room}_light"
        current_time = time.time()

        # initialize room state if first time
        if relay_key not in self.relay_states:
            self.relay_states[relay_key] = True
            self.last_zero_motion_time[relay_key] = None

        # Low energy window override
        if self._is_low_energy_window():
            update_relay_state(relay_key, self.relay_states[relay_key])
            return self.relay_states[relay_key]

        # ------------------------------
        # Motion detected
        # ------------------------------
        if motion == 1:

            # reset zero timer
            self.last_zero_motion_time[relay_key] = None

            # ensure relay is ON
            if not self.relay_states[relay_key]:
                self.relay_states[relay_key] = True

        # ------------------------------
        # No motion
        # ------------------------------
        else:

            # first zero event
            if self.last_zero_motion_time[relay_key] is None:
                self.last_zero_motion_time[relay_key] = current_time

            # check if 5 minutes passed
            elif (
                current_time - self.last_zero_motion_time[relay_key] >= AUTO_OFF_TIMEOUT
            ):
                self.relay_states[relay_key] = False

        # update firebase relay state
        update_relay_state(relay_key, self.relay_states[relay_key])

        return self.relay_states[relay_key]


relay_controller = RelayController()
