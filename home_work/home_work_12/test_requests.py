import json
import sys
from pathlib import Path

import requests

BASE = "http://127.0.0.1:5000"
OUT = Path(__file__).resolve().parent / "results.txt"


def log(line=""):
    print(line)
    sys.stdout.flush()


def main():
    lines = []

    def record(line=""):
        log(line)
        lines.append(line if line else "")

    def req(method, url, **kw):
        r = requests.request(method, url, **kw)
        record(f"{method} {url}")
        if kw.get("json") is not None:
            record(f"  body: {json.dumps(kw['json'], ensure_ascii=False)}")
        try:
            body = r.json()
            text = json.dumps(body, ensure_ascii=False, indent=2)
        except ValueError:
            text = r.text
        record(f"  status: {r.status_code}")
        record(text)
        record()
        return r

    record("=== 1. GET усіх студентів ===")
    r1 = req("GET", f"{BASE}/students")
    record()

    record("=== 2. POST три студенти ===")
    created = []
    for payload in (
        {"first_name": "Олена", "last_name": "Коваленко", "age": 20},
        {"first_name": "Ігор", "last_name": "Бондар", "age": 22},
        {"first_name": "Марія", "last_name": "Шевченко", "age": 19},
    ):
        r = req("POST", f"{BASE}/students", json=payload)
        created.append(r.json())
    id1, id2, id3 = created[0]["id"], created[1]["id"], created[2]["id"]
    record()

    record("=== 3. GET усіх після створення ===")
    req("GET", f"{BASE}/students")
    record()

    record("=== 4. PATCH вік другого студента ===")
    req("PATCH", f"{BASE}/students/{id2}", json={"age": 23})
    record()

    record("=== 5. GET другого студента ===")
    req("GET", f"{BASE}/students/{id2}")
    record()

    record("=== 6. PUT третього студента ===")
    req(
        "PUT",
        f"{BASE}/students/{id3}",
        json={"first_name": "Марія-Анна", "last_name": "Шевченко", "age": 20},
    )
    record()

    record("=== 7. GET третього студента ===")
    req("GET", f"{BASE}/students/{id3}")
    record()

    record("=== 8. GET усіх ===")
    req("GET", f"{BASE}/students")
    record()

    record("=== 9. DELETE першого студента ===")
    req("DELETE", f"{BASE}/students/{id1}")
    record()

    record("=== 10. GET усіх після видалення ===")
    req("GET", f"{BASE}/students")
    record()

    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    log(f"\nЗаписано: {OUT}")


if __name__ == "__main__":
    main()
