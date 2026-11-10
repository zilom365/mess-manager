import re
from datetime import date, timedelta
import pandas as pd

MONTHS = {"january":1,"jan":1,"february":2,"feb":2,"march":3,"april":4,"may":5,
          "june":6,"july":7,"august":8,"september":9,"october":10,"oct":10,
          "november":11,"nov":11,"december":12,"dec":12}
KEYWORDS = ["meeting","quiz","exam","bill","assignment","class","submit",
            "deadline","presentation","lab"]
RELATIVE = {"ajke":0,"aj":0,"kal":1,"kalke":1,"kalle":1,"porshu":2}
COLUMNS = ["task", "due", "needs_confirmation", "source"]

def extract(text, today):
    rows = []
    for clause in re.split(r",| ar | and ", text.lower()):
        clause = clause.strip()
        task = next((k for k in KEYWORDS if k in clause), None)
        if not clause or not task:
            continue
        due, confirm = None, True
        m = re.search(r"(\d{1,2})\s*(?:th|st|nd|rd)?\s+([a-z]+)", clause)
        words = clause.split()
        if m and m.group(2) in MONTHS:
            try:
                d = date(today.year, MONTHS[m.group(2)], int(m.group(1)))
                if d < today:
                    d = d.replace(year=today.year + 1)
                due, confirm = d, False
            except ValueError:
                pass
        elif any(w in RELATIVE for w in words):
            w = next(w for w in words if w in RELATIVE)
            due, confirm = today + timedelta(days=RELATIVE[w]), False
        elif "porer shoptaho" in clause or "next week" in clause:
            due, confirm = today + timedelta(days=7), True
        rows.append({"task": task, "due": due,
                     "needs_confirmation": confirm, "source": clause})
    return pd.DataFrame(rows, columns=COLUMNS)
