from flask import Flask, send_from_directory, jsonify, request
import os
import mysql.connector

app = Flask(__name__)


def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", "3306")),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME", "ehms_rhv"),
        ssl_disabled=False
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
# CLOSE EMERGENCY
# ----------------------------------------------------

@app.route("/api/emergencies/<int:emergency_id>/close", methods=["PUT"])
def close_emergency(emergency_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE Emergency
        SET status = 'Closed'
        WHERE emergency_id = %s
    """, (emergency_id,))

    conn.commit()

    if cursor.rowcount == 0:
        cursor.close()
        conn.close()

        return jsonify({
            "error": "Emergency not found"
        }), 404

    cursor.close()
    conn.close()

    return jsonify({
        "message": "Emergency closed successfully"
    })


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


# ----------------------------------------------------
# DELETE PATIENT
# ----------------------------------------------------

@app.route("/api/patients/<int:patient_id>", methods=["DELETE"])
def delete_patient(patient_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        conn.start_transaction()

        # Delete logs belonging to this patient's emergencies
        cursor.execute("""
            DELETE FROM Emergency_Log
            WHERE emergency_id IN (
                SELECT emergency_id
                FROM Emergency
                WHERE patient_id = %s
            )
        """, (patient_id,))

        # Delete emergencies belonging to the patient
        cursor.execute("""
            DELETE FROM Emergency
            WHERE patient_id = %s
        """, (patient_id,))

        # Delete the patient
        cursor.execute("""
            DELETE FROM Patient
            WHERE patient_id = %s
        """, (patient_id,))

        if cursor.rowcount == 0:
            conn.rollback()

            return jsonify({
                "error": "Patient not found"
            }), 404

        conn.commit()

        return jsonify({
            "message": "Patient and related emergency records deleted successfully"
        })

    except Exception as e:
        conn.rollback()

        return jsonify({
            "error": str(e)
        }), 500

    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    app.run(debug=True)