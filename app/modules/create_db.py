import sqlite3
import os
import random
from datetime import date, timedelta

db_path = os.path.join(os.path.dirname(__file__), "..", "..", "tech.db")


def create_database():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("DROP TABLE IF EXISTS Schedule")
    cursor.execute("""
        CREATE TABLE Schedule (
            ScheduleID INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            time TEXT NOT NULL,
            position TEXT NOT NULL,
            available INTEGER NOT NULL
        )
    """)
    positions = ["Python Dev", "Sql Dev", "Analyst", "ML"]
    start_date = date.today()
    for day in range(60):
        current_date = start_date + timedelta(days=day)
        if current_date.strftime("%A") in ["Saturday", "Monday"]:
            continue
        for hour in range(9, 18):
            for position in positions:
                available = random.randint(0, 1)
                cursor.execute(
                    "INSERT INTO Schedule (date, time, position, available) VALUES (?, ?, ?, ?)",
                    (current_date.isoformat(), f"{hour:02d}:00", position, available)
                )
    conn.commit()
    conn.close()


def show_available_slots():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT date, time FROM Schedule WHERE position = 'Python Dev' AND available = 1 ORDER BY date, time LIMIT 10"
    )
    rows = cursor.fetchall()
    conn.close()
    for row in rows:
        print(row[0], row[1])


if __name__ == "__main__":
    create_database()
    print("tech.db was created")
    show_available_slots()
