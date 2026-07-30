import os
import pandas as pd
from datetime import datetime
import json
import config

COLUMNS = ["Timestamp", "SessionID", "UserQuestion", "BotResponse", "IntentMatched", "Confidence", "ResponseTimeSec"]

def init_history_file():
    """Create the history CSV file with headers if it does not exist yet."""
    history_file_path = config.HISTORY_FILE
    if not os.path.exists(history_file_path):
        try:
            df = pd.DataFrame(columns=COLUMNS)
            df.to_csv(history_file_path, index=False)
        except Exception as e:
            print(f"Error initializing history file: {e}")

def save_chat_record(session_id: str, question: str, response: str, intent: str, confidence: float, response_time: float):
    """Save a single query-response round to the CSV history logs."""
    init_history_file()
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    new_record = {
        "Timestamp": timestamp,
        "SessionID": session_id,
        "UserQuestion": question,
        "BotResponse": response,
        "IntentMatched": intent,
        "Confidence": round(float(confidence), 4),
        "ResponseTimeSec": round(float(response_time), 4)
    }
    
    try:
        df = pd.DataFrame([new_record])
        df.to_csv(config.HISTORY_FILE, mode='a', header=False, index=False)
    except Exception as e:
        print(f"Error saving chat record: {e}")

def load_chat_history() -> pd.DataFrame:
    """Load and return the history log as a pandas DataFrame."""
    init_history_file()
    try:
        df = pd.read_csv(config.HISTORY_FILE)
        # Type conversions
        df["Timestamp"] = pd.to_datetime(df["Timestamp"], errors='coerce')
        df["Confidence"] = pd.to_numeric(df["Confidence"], errors='coerce').fillna(0.0)
        df["ResponseTimeSec"] = pd.to_numeric(df["ResponseTimeSec"], errors='coerce').fillna(0.0)
        return df
    except Exception as e:
        print(f"Error loading chat history: {e}")
        return pd.DataFrame(columns=COLUMNS)

def clear_chat_history() -> bool:
    """Delete the CSV history log and re-initialize it."""
    try:
        if os.path.exists(config.HISTORY_FILE):
            os.remove(config.HISTORY_FILE)
        init_history_file()
        return True
    except Exception as e:
        print(f"Error clearing chat history: {e}")
        return False

def export_history_to_json() -> str:
    """Read the history records and output them as a formatted JSON string."""
    df = load_chat_history()
    # Handle datetime conversion for JSON serializability
    if not df.empty:
        df["Timestamp"] = df["Timestamp"].astype(str)
        return df.to_json(orient="records", indent=2)
    return "[]"

def export_history_to_csv() -> str:
    """Read and return history file contents as text bytes/string."""
    try:
        if os.path.exists(config.HISTORY_FILE):
            with open(config.HISTORY_FILE, "r", encoding="utf-8") as f:
                return f.read()
    except Exception as e:
        print(f"Error reading history file bytes: {e}")
    return ",".join(COLUMNS)
