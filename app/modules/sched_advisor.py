import sqlite3
import os
from datetime import date
from dotenv import load_dotenv
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent

load_dotenv()

db_path = os.path.join(os.path.dirname(__file__), "..", "..", "tech.db")


@tool
def get_available_slots(from_date: str) -> list:
    """Return the 3 nearest available interview slots for the Python Dev position, starting from the given date. The date format is YYYY-MM-DD."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT date, time FROM Schedule WHERE position = 'Python Dev' AND available = 1 AND date >= ? ORDER BY date, time LIMIT 3",
        (from_date,)
    )
    rows = cursor.fetchall()
    conn.close()
    return rows


@tool
def book_slot(slot_date: str, slot_time: str) -> str:
    """Book an interview slot for the Python Dev position. The date format is YYYY-MM-DD and the time format is HH:MM. Returns a confirmation or a failure message."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT ScheduleID FROM Schedule WHERE position = 'Python Dev' AND date = ? AND time = ? AND available = 1",
        (slot_date, slot_time)
    )
    row = cursor.fetchone()
    if row is None:
        conn.close()
        return "This slot is not available"
    cursor.execute("UPDATE Schedule SET available = 0 WHERE ScheduleID = ?", (row[0],))
    conn.commit()
    conn.close()
    return f"The interview is booked for {slot_date} at {slot_time}"


llm = ChatOpenAI(model="gpt-4o", temperature=0)

tools = [get_available_slots, book_slot]


def suggest_slots(conversation):
    today = date.today().isoformat()
    system_text = (
        "You are an Interview Scheduling Advisor for a Python Developer position. "
        f"Today's date is {today}. "
        "Read the conversation and help schedule an interview between the candidate and the recruiter. "
        "If the candidate mentioned a preferred day like 'next Friday' or 'tomorrow', calculate the real date from today's date. "
        "Use get_available_slots to find the 3 nearest available slots from the relevant date and offer them to the candidate. "
        "If the candidate already agreed to a specific available slot, use book_slot to book it and confirm. "
        "If the time the candidate asked for is not available, offer the nearest available options instead. "
        "Reply with one short SMS style message to send to the candidate."
    )
    agent = create_agent(llm, tools, system_prompt=system_text)
    result = agent.invoke({"messages": [{"role": "user", "content": conversation}]})
    return result["messages"][-1].content


if __name__ == "__main__":
    conversation_1 = """recruiter: Would you like to schedule an interview?
candidate: Yes, can we meet sometime next week?"""
    print(suggest_slots(conversation_1))
    print()

    conversation_2 = """recruiter: Would you like to schedule an interview?
candidate: Yes, tomorrow morning if possible."""
    print(suggest_slots(conversation_2))
