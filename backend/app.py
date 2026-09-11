from flask import Flask, send_from_directory, jsonify, request
import os
import mysql.connector

app = Flask(__name__)


def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME", "ehms_rhv")
    )


FRONTEND_FOLDER = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "frontend"
)


@app.route("/")
def home():
    return send_from_directory(FRONTEND_FOLDER, "index.html")


# ----------------------------------------------------
# GET EMERGENCIES
# ----------------------------------------------------

@app.route("/api/emergencies", methods=["GET"])
def get_emergencies():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            Emergency.emergency_id,
            Emergency.patient_id,
            Patient.name AS patient_name,
            Patient.village,
            Emergency.priority,
            Emergency.emergency_type,
            Emergency.status,
            Emergency.request_time
        FROM Emergency
        JOIN Patient
            ON Emergency.patient_id = Patient.patient_id
        ORDER BY Emergency.priority ASC, Emergency.request_time ASC
    """)

    emergencies = cursor.fetchall()

    cursor.close()
    conn.close()

    return jsonify(emergencies)


# ----------------------------------------------------
# CREATE EMERGENCY
# ----------------------------------------------------

@app.route("/api/emergencies", methods=["POST"])
def create_emergency():
    data = request.get_json()

    patient_id = data.get("patient_id")
    priority = data.get("priority")
    emergency_type = data.get("emergency_type")

    if not patient_id or not priority or not emergency_type:
        return jsonify({
            "error": "patient_id, priority and emergency_type are required"
        }), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO Emergency
        (patient_id, priority, emergency_type, status)
        VALUES (%s, %s, %s, %s)
    """, (
        patient_id,
        priority,
        emergency_type,
        "Pending"
    ))

    conn.commit()

    emergency_id = cursor.lastrowid

    cursor.close()
    conn.close()

    return jsonify({
        "message": "Emergency created successfully",
        "emergency_id": emergency_id
    }), 201


# ----------------------------------------------------
# PATIENT API
# ----------------------------------------------------

@app.route("/api/patients", methods=["POST"])
def create_patient():
    data = request.get_json()

    name = data.get("name")
    age = data.get("age")
    gender = data.get("gender")
    phone = data.get("phone")
    village = data.get("village")

    if not name or not age or not gender or not phone or not village:
        return jsonify({
            "error": "name, age, gender, phone and village are required"
        }), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO Patient
        (name, age, gender, phone, village)
        VALUES (%s, %s, %s, %s, %s)
    """, (
        name,
        age,
        gender,
        phone,
        village
    ))

    conn.commit()

    patient_id = cursor.lastrowid

    cursor.close()
    conn.close()

    return jsonify({
        "message": "Patient created successfully",
        "patient_id": patient_id
    }), 201


if __name__ == "__main__":
    app.run(debug=True)