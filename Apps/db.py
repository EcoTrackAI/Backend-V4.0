import psycopg2
import os

DATABASE_URL = os.getenv("DATABASE_URL")


def get_connection():
    return psycopg2.connect(DATABASE_URL)


# ---------------------------
# FETCH LATEST SENSOR DATA
# ---------------------------
def get_latest_sensor_data(room: str):
    conn = get_connection()
    cursor = conn.cursor()

    query = """
    SELECT temperature, humidity, light, motion
    FROM sensors
    WHERE room = %s
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
        "temp": result[0],
        "humidity": result[1],
        "light": result[2],
        "motion": int(result[3])
    }


# ---------------------------
# UPDATE RELAY STATE
# ---------------------------
def update_relay_state_db(relay_key: str, state: bool):
    conn = get_connection()
    cursor = conn.cursor()

    query = """
    INSERT INTO relays (relay_key, state, timestamp)
    VALUES (%s, %s, NOW())
    ON CONFLICT (relay_key)
    DO UPDATE SET state = EXCLUDED.state, timestamp = NOW();
    """

    cursor.execute(query, (relay_key, state))

    conn.commit()
    cursor.close()
    conn.close()