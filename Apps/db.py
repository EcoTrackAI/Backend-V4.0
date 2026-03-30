import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL is not set")


def get_connection():
    return psycopg2.connect(DATABASE_URL)


# -----------------------------------
# GET LATEST SENSOR DATA
# -----------------------------------
def get_latest_sensor_data(room: str):
    conn = get_connection()
    cursor = conn.cursor()

    query = """
    SELECT temperature, humidity, light, motion
    FROM room_sensors
    WHERE room_id = %s
    ORDER BY timestamp DESC
    LIMIT 1;
    """

    cursor.execute(query, (room,))
    result = cursor.fetchone()

    cursor.close()
    conn.close()

    if not result:
        return None

    return {
        "temp": float(result[0]),
        "humidity": float(result[1]),
        "light": float(result[2]),
        "motion": int(result[3])
    }


# -----------------------------------
# UPDATE RELAY STATE
# -----------------------------------
def update_relay_state_db(relay_key: str, state: bool):
    conn = get_connection()
    cursor = conn.cursor()

    # relay_key = "bedroom_light"
    room_id, relay_type = relay_key.split("_")

    query = """
    INSERT INTO relay_states (room_id, relay_type, state, updated_at)
    VALUES (%s, %s, %s, NOW())
    ON CONFLICT (room_id, relay_type)
    DO UPDATE SET state = EXCLUDED.state, updated_at = NOW();
    """

    cursor.execute(query, (room_id, relay_type, state))

    conn.commit()
    cursor.close()
    conn.close()