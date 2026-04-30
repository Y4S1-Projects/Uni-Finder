import csv
import json

with open("data/University_Courses_Dataset.csv", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        code = row["Course Code"].strip()
        req = row["A/L Subject Requirements"].strip()
        if "2 of these" in req.lower():
            print(f"[{code}] {req}")
