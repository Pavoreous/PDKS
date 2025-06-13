# utils.py
from datetime import datetime

def get_current_time():
    return datetime.now().strftime("%H:%M:%S")

def get_current_date():
    return datetime.now().strftime("%Y-%m-%d")