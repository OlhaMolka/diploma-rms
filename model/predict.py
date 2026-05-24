import joblib
import pandas as pd
from pathlib import Path

# Trained regression model used for the four risk dimensions.
MODEL_DIR = Path(__file__).resolve().parent
model = joblib.load(MODEL_DIR / "reg_model.pkl")

BASE_FEATURES = [
    "budget",
    "duration_md",
    "vendor_count",
    "requirements_clarity",
    "vendor_experience",
    "regulatory_impact",
    "criticality",
]

VENDOR_FEATURES = [
    "vendor_a",
    "vendor_b",
    "vendor_c",
    "vendor_d",
    "vendor_e",
    "vendor_f",
]

FEATURES = BASE_FEATURES + VENDOR_FEATURES

VENDOR_TO_FEATURE = {
    "Постачальник A": "vendor_a",
    "Постачальник B": "vendor_b",
    "Постачальник C": "vendor_c",
    "Постачальник D": "vendor_d",
    "Постачальник E": "vendor_e",
    "Постачальник F": "vendor_f",
    "IronMan": "vendor_a",
    "Thor": "vendor_b",
    "Hulk": "vendor_c",
    "CaptainAmerica": "vendor_d",
    "BlackWidow": "vendor_e",
    "Hawkeye": "vendor_f",
}


def vendor_flags(vendors):
    flags = {feature: 0 for feature in VENDOR_FEATURES}
    for vendor in vendors or []:
        feature = VENDOR_TO_FEATURE.get(vendor)
        if feature:
            flags[feature] = 1
    return flags


def preprocess_input(data):
    row = {}
    vendors = data.get("vendors", [])

    if "vendor_count" not in data:
        data["vendor_count"] = len(vendors)

    missing = [col for col in BASE_FEATURES if col not in data]
    if missing:
        raise ValueError(f"Missing model input fields: {', '.join(missing)}")

    for col in BASE_FEATURES:
        row[col] = data[col]

    row.update(vendor_flags(vendors))

    return pd.DataFrame([row], columns=FEATURES)


def predict_risk(data):
    df = preprocess_input(data)

    prediction = model.predict(df)[0]

    return {
        "deadline": float(round(prediction[0], 2)),
        "budget": float(round(prediction[1], 2)),
        "scope": float(round(prediction[2], 2)),
        "resources": float(round(prediction[3], 2))
    }
