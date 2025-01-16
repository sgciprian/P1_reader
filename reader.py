import sqlite3
import serial
import re

def setup_database():
    conn = sqlite3.connect("readings.db")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS electricity_readings (
            timestamp TEXT PRIMARY KEY,
            lifetime_power_t1 REAL,
            lifetime_power_t2 REAL,
            current_tariff TEXT,
            current_power_usage REAL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS gas_readings (
            timestamp TEXT PRIMARY KEY,
            lifetime_gas_usage REAL
        )
    """)

    conn.commit()
    conn.close()

electricity_patterns = {
    "timestamp": re.compile(r"0-0:1\.0\.0\(<(\d{12})>\)"),
    "lifetime_power_t1": re.compile(r"1-0:1\.8\.1\(<(\d+\.\d{3})>\)"),
    "lifetime_power_t2": re.compile(r"1-0:1\.8\.2\(<(\d+\.\d{3})>\)"),
    "current_tariff": re.compile(r"1-0:96\.14\.0\(<(\d{4})>\)"),
    "current_power_usage": re.compile(r"1-0:1\.7\.0\(<(\d+\.\d{3})>\)"),
}

gas_pattern = re.compile(r"0-1:24\.2\.1\(<(\d{12})>W\)\(<(\d+\.\d{3})>\)")

def parse_electricity(packet):
    data = {}
    for key, pattern in electricity_patterns.items():
        match = pattern.search(packet)
        if match:
            data[key] = match.group(1)
    return data

def parse_gas(packet):
    match = gas_pattern.search(packet)
    if match:
        return {
            "timestamp": match.group(1),
            "lifetime_gas_usage": float(match.group(2)),
        }
    return None

def insert_electricity_readings(data):
    conn = sqlite3.connect("readings.db")
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            INSERT INTO electricity_readings (timestamp, lifetime_power_t1, lifetime_power_t2, current_tariff, current_power_usage)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                data.get("timestamp"),
                float(data.get("lifetime_power_t1", 0)),
                float(data.get("lifetime_power_t2", 0)),
                data.get("current_tariff"),
                float(data.get("current_power_usage", 0)),
            ),
        )
    except sqlite3.IntegrityError as e:
        print(f"Duplicate electricity reading for timestamp {data.get('timestamp')}: {e}")

    conn.commit()
    conn.close()

def insert_gas_readings(data):
    conn = sqlite3.connect("readings.db")
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            INSERT INTO gas_readings (timestamp, lifetime_gas_usage)
            VALUES (?, ?)
            """,
            (data["timestamp"], data["lifetime_gas_usage"]),
        )
    except sqlite3.IntegrityError as e:
        print(f"Duplicate gas reading for timestamp {data['timestamp']}: {e}")

    conn.commit()
    conn.close()

serial_port = "/dev/ttyUSB0"
baud_rate = 115200

def main():
    setup_database()

    with serial.Serial(serial_port, baud_rate, timeout=1) as ser:
        buffer = ""

        while True:
            line = ser.readline().decode("utf-8").strip()
            if line == "":
                if "0-0:1.0.0" in buffer:
                    electricity_data = parse_electricity(buffer)
                    if electricity_data:
                        insert_electricity_readings(electricity_data)
                elif "0-1:24.2.1" in buffer:
                    gas_data = parse_gas(buffer)
                    if gas_data:
                        insert_gas_readings(gas_data)

                buffer = ""
            else:
                buffer += line + "\n"

if __name__ == "__main__":
    main()
