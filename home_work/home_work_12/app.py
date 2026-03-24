import csv
import os
from flask import Flask, jsonify, request

CSV_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "students.csv")
FIELDNAMES = ("id", "first_name", "last_name", "age")
POST_PUT_KEYS = frozenset({"first_name", "last_name", "age"})
PATCH_KEYS = frozenset({"age"})

app = Flask(__name__)


@app.get("/")
def index():
    return jsonify(
        {
            "message": "API студентів. Головний ресурс: GET/POST /students",
            "endpoints": {
                "list_or_create": "/students",
                "by_id": "/students/<id>",
                "by_last_name_query": "/students?last_name=...",
            },
        }
    )


def _read_students():
    if not os.path.isfile(CSV_PATH):
        return []
    with open(CSV_PATH, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    out = []
    for row in rows:
        if not row.get("id", "").strip():
            continue
        out.append(
            {
                "id": int(row["id"]),
                "first_name": row["first_name"],
                "last_name": row["last_name"],
                "age": int(row["age"]),
            }
        )
    return out


def _write_students(students):
    os.makedirs(os.path.dirname(CSV_PATH) or ".", exist_ok=True)
    with open(CSV_PATH, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDNAMES)
        w.writeheader()
        for s in students:
            w.writerow(
                {
                    "id": s["id"],
                    "first_name": s["first_name"],
                    "last_name": s["last_name"],
                    "age": s["age"],
                }
            )


def _next_id(students):
    if not students:
        return 1
    return max(s["id"] for s in students) + 1


def _student_to_dict(s):
    return {
        "id": s["id"],
        "first_name": s["first_name"],
        "last_name": s["last_name"],
        "age": s["age"],
    }


def _validate_body_exact(body, allowed_keys):
    if body is None or not isinstance(body, dict):
        return "Очікується JSON-об'єкт у тілі запиту.", None
    if len(body) == 0:
        return "Тіло запиту порожнє.", None
    keys = frozenset(body.keys())
    if keys != allowed_keys:
        return "Дозволені лише поля: " + ", ".join(sorted(allowed_keys)) + ".", None
    return None, body


@app.get("/students")
def get_students():
    last_name = request.args.get("last_name")
    students = _read_students()
    if last_name is not None:
        if last_name == "":
            return jsonify({"error": "Параметр last_name порожній."}), 400
        matches = [s for s in students if s["last_name"] == last_name]
        if not matches:
            return (
                jsonify({"error": f"Студента з прізвищем «{last_name}» не знайдено."}),
                404,
            )
        return jsonify([_student_to_dict(s) for s in matches]), 200
    return jsonify([_student_to_dict(s) for s in students]), 200


@app.get("/students/<int:student_id>")
def get_student_by_id(student_id):
    students = _read_students()
    for s in students:
        if s["id"] == student_id:
            return jsonify(_student_to_dict(s)), 200
    return jsonify({"error": f"Студента з id={student_id} не знайдено."}), 404


@app.post("/students")
def create_student():
    body = request.get_json(silent=True)
    err, data = _validate_body_exact(body, POST_PUT_KEYS)
    if err:
        return jsonify({"error": err}), 400
    try:
        age = int(data["age"])
    except (TypeError, ValueError):
        return jsonify({"error": "Поле age має бути цілим числом."}), 400
    if not str(data.get("first_name", "")).strip() or not str(
        data.get("last_name", "")
    ).strip():
        return jsonify({"error": "Поля first_name та last_name не можуть бути порожніми."}), 400
    students = _read_students()
    new_id = _next_id(students)
    student = {
        "id": new_id,
        "first_name": str(data["first_name"]).strip(),
        "last_name": str(data["last_name"]).strip(),
        "age": age,
    }
    students.append(student)
    _write_students(students)
    return jsonify(_student_to_dict(student)), 201


@app.put("/students/<int:student_id>")
def replace_student(student_id):
    body = request.get_json(silent=True)
    err, data = _validate_body_exact(body, POST_PUT_KEYS)
    if err:
        return jsonify({"error": err}), 400
    try:
        age = int(data["age"])
    except (TypeError, ValueError):
        return jsonify({"error": "Поле age має бути цілим числом."}), 400
    if not str(data.get("first_name", "")).strip() or not str(
        data.get("last_name", "")
    ).strip():
        return jsonify({"error": "Поля first_name та last_name не можуть бути порожніми."}), 400
    students = _read_students()
    for i, s in enumerate(students):
        if s["id"] == student_id:
            students[i] = {
                "id": student_id,
                "first_name": str(data["first_name"]).strip(),
                "last_name": str(data["last_name"]).strip(),
                "age": age,
            }
            _write_students(students)
            return jsonify(_student_to_dict(students[i])), 200
    return jsonify({"error": f"Студента з id={student_id} не знайдено."}), 404


@app.patch("/students/<int:student_id>")
def patch_student_age(student_id):
    body = request.get_json(silent=True)
    err, data = _validate_body_exact(body, PATCH_KEYS)
    if err:
        return jsonify({"error": err}), 400
    try:
        age = int(data["age"])
    except (TypeError, ValueError):
        return jsonify({"error": "Поле age має бути цілим числом."}), 400
    students = _read_students()
    for i, s in enumerate(students):
        if s["id"] == student_id:
            students[i] = {**s, "age": age}
            _write_students(students)
            return jsonify(_student_to_dict(students[i])), 200
    return jsonify({"error": f"Студента з id={student_id} не знайдено."}), 404


@app.delete("/students/<int:student_id>")
def delete_student(student_id):
    students = _read_students()
    new_list = [s for s in students if s["id"] != student_id]
    if len(new_list) == len(students):
        return jsonify({"error": f"Студента з id={student_id} не знайдено."}), 404
    _write_students(new_list)
    return jsonify({"message": f"Студента з id={student_id} успішно видалено."}), 200


if __name__ == "__main__":
    app.run(debug=True)
