import re
import pandas as pd
from datetime import datetime

def parse_whatsapp_chat(file_content):
    """
    Parses raw WhatsApp chat export text into a clean DataFrame.
    Handles both 12-hour and 24-hour time formats.
    """

    # Pattern covers: DD/MM/YYYY, HH:MM - Name: Message
    pattern = r'(\d{1,2}/\d{1,2}/\d{2,4}),\s(\d{1,2}:\d{2}(?:\s?[APap][Mm])?)\s-\s(.*?):\s(.*)'

    messages = []

    for line in file_content.split('\n'):
        match = re.match(pattern, line)
        if match:
            date_str, time_str, author, message = match.groups()
            try:
                # Try parsing with AM/PM first
                try:
                    dt = datetime.strptime(f"{date_str} {time_str}", "%d/%m/%Y %I:%M %p")
                except:
                    dt = datetime.strptime(f"{date_str} {time_str}", "%d/%m/%Y %H:%M")
                messages.append({
                    "date": dt.date(),
                    "time": dt.time(),
                    "hour": dt.hour,
                    "day_name": dt.strftime("%A"),
                    "month": dt.strftime("%B %Y"),
                    "author": author.strip(),
                    "message": message.strip()
                })
            except:
                continue

    df = pd.DataFrame(messages)
    return df
