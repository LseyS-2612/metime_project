import json
import os
import time

SETTINGS_PATH = "settings.json"
MEDITATION_DATA_PATH = "meditation_data.json"

def load_settings():
    """Ayarları settings.json dosyasından yükler."""
    base_dir = os.path.dirname(__file__)
    settings_path = os.path.join(base_dir, "..", "settings.json")
    try:
        with open(settings_path, "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

def save_settings(settings):
    """Ayarları settings.json dosyasına kaydeder."""
    base_dir = os.path.dirname(__file__)
    settings_path = os.path.join(base_dir, "..", "settings.json")
    with open(settings_path, "w", encoding="utf-8") as file:
        json.dump(settings, file, ensure_ascii=False, indent=4)

def load_meditation_data():
    if not os.path.exists(MEDITATION_DATA_PATH):
        return {"last_meditation_date": None, "streak": 0}
    with open(MEDITATION_DATA_PATH, "r") as f:
        return json.load(f)

def save_meditation_data(data):
    with open(MEDITATION_DATA_PATH, "w") as f:
        json.dump(data, f, indent=4)

def update_streak():
    data = load_meditation_data()
    today = time.strftime("%Y-%m-%d")
    last_date = data.get("last_meditation_date")

    if last_date == today:
        return data["streak"]

    if last_date:
        last_date_obj = time.strptime(last_date, "%Y-%m-%d")
        today_obj = time.strptime(today, "%Y-%m-%d")
        days_diff = (time.mktime(today_obj) - time.mktime(last_date_obj)) / (24 * 3600)

        if days_diff == 1:
            data["streak"] += 1
        else:
            data["streak"] = 1
    else:
        data["streak"] = 1

    data["last_meditation_date"] = today
    save_meditation_data(data)
    return data["streak"]