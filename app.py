
from fastapi import FastAPI
import sqlite3
import json

app = FastAPI(title="Health Risk Assessment API")


def get_database_connection():
    return sqlite3.connect("health_risk_assessment.db")


@app.get("/")
def home():
    return {
        "message": "Health Risk Assessment API is running"
    }


@app.get("/health-report/{patient_id}")
def generate_health_report(patient_id: int):

    connection = get_database_connection()
    cursor = connection.cursor()

    # Get patient profile
    cursor.execute("""
        SELECT *
        FROM patient_profiles
        WHERE patient_id = ?
    """, (patient_id,))

    patient = cursor.fetchone()

    if patient is None:
        connection.close()
        return {
            "error": "Patient not found"
        }

    # Get disease prediction
    cursor.execute("""
        SELECT predicted_disease, probability_scores
        FROM disease_predictions
        WHERE patient_id = ?
        ORDER BY prediction_id DESC
        LIMIT 1
    """, (patient_id,))

    prediction = cursor.fetchone()

    # Get risk assessment
    cursor.execute("""
        SELECT severity_score,
               severity_level,
               risk_score,
               risk_category
        FROM risk_assessments
        WHERE patient_id = ?
        ORDER BY risk_id DESC
        LIMIT 1
    """, (patient_id,))

    risk = cursor.fetchone()

    connection.close()

    if prediction is None or risk is None:
        return {
            "error": "Prediction or risk assessment not found"
        }

    predicted_disease = prediction[0]
    probability_scores = json.loads(prediction[1])

    severity_score = risk[0]
    severity_level = risk[1]
    risk_score = risk[2]
    risk_category = risk[3]

    # Generate health risk report
    report = {
        "patient_id": patient_id,
        "predicted_disease": predicted_disease,
        "disease_probability": probability_scores,
        "severity_score": severity_score,
        "severity_level": severity_level,
        "risk_score": risk_score,
        "risk_category": risk_category
    }

    return report
