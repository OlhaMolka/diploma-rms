import joblib
import pandas as pd
from pathlib import Path

# Load the trained multi-output regression model used by the Streamlit app
# to estimate the four project risk dimensions from a single feature row.
MODEL_DIR = Path(__file__).resolve().parent
model = joblib.load(MODEL_DIR / "reg_model.pkl")

FEATURES = [
    "budget",
    "duration_md",
    "vendor_count",
    "changes_count",
    "requirements_clarity",
    "vendor_experience",
    "regulatory_impact",
    "criticality",
]


def preprocess_input(data):
    missing = [col for col in FEATURES if col not in data]
    if missing:
        raise ValueError(f"Missing model input fields: {', '.join(missing)}")

    return pd.DataFrame([{col: data[col] for col in FEATURES}])


def predict_risk(data):
    df = preprocess_input(data)

    prediction = model.predict(df)[0]

    return {
        "deadline": float(round(prediction[0], 2)),
        "budget": float(round(prediction[1], 2)),
        "scope": float(round(prediction[2], 2)),
        "resources": float(round(prediction[3], 2))
    }
