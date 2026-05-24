from pathlib import Path

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.multioutput import MultiOutputRegressor
from sklearn.preprocessing import LabelEncoder


MODEL_DIR = Path(__file__).resolve().parent
DATA_PATH = MODEL_DIR.parent / "data" / "projects_dataset_v7.xlsx"

VENDOR_MAP = {
    "IronMan": "vendor_a",
    "Thor": "vendor_b",
    "Hulk": "vendor_c",
    "CaptainAmerica": "vendor_d",
    "BlackWidow": "vendor_e",
    "Hawkeye": "vendor_f",
}
VENDOR_FEATURES = list(VENDOR_MAP.values())


def add_vendor_flags(row):
    selected = str(row.get("vendors", "")).split(",")
    selected = {vendor.strip() for vendor in selected if vendor.strip()}
    return pd.Series({
        feature: int(raw_vendor in selected)
        for raw_vendor, feature in VENDOR_MAP.items()
    })


df = pd.read_excel(DATA_PATH)

clarity_map = {
    "Well defined": 0,
    "Clearly defined and approved": 0,
    "Partially defined": 1,
    "Partially defined, уточнення можливі": 1,
    "Unclear": 2,
    "Unclear and evolving": 2,
}

experience_map = {
    "Worked before": 0,
    "Proven experience with similar projects": 0,
    "Mixed experience": 1,
    "Partial experience": 1,
    "New vendor": 2,
    "New vendor / no relevant experience": 2,
}

regulatory_map = {
    "No regulatory impact": 0,
    "No regulatory constraints": 0,
    "Internal compliance": 1,
    "Internal compliance requirements": 1,
    "External regulation": 2,
    "Strict external regulation": 2,
}

criticality_map = {
    "Low": 0,
    "Minimal impact": 0,
    "Medium": 1,
    "Noticeable impact": 1,
    "High": 2,
    "Serious business disruption": 2,
    "Critical for bank operations": 3,
}

df["requirements_clarity"] = df["requirements_clarity"].map(clarity_map)
df["vendor_experience"] = df["vendor_experience"].map(experience_map)
df["regulatory_impact"] = df["regulatory_impact"].map(regulatory_map).fillna(0)
df["criticality"] = df["criticality"].map(criticality_map)
df[VENDOR_FEATURES] = df.apply(add_vendor_flags, axis=1)

features = [
    "budget",
    "duration_md",
    "vendor_count",
    "requirements_clarity",
    "vendor_experience",
    "regulatory_impact",
    "criticality",
] + VENDOR_FEATURES

X = df[features]
y_reg = df[[
    "risk_deadline_delay",
    "risk_budget_overrun",
    "risk_scope_change",
    "risk_resource_issue",
]]

le = LabelEncoder()
y_cls = le.fit_transform(df["risk_level"])

X_train, X_test, y_reg_train, y_reg_test = train_test_split(
    X,
    y_reg,
    test_size=0.2,
    random_state=42,
)
_, _, y_cls_train, y_cls_test = train_test_split(
    X,
    y_cls,
    test_size=0.2,
    random_state=42,
)

reg_model = MultiOutputRegressor(
    RandomForestRegressor(n_estimators=200, random_state=42)
)
reg_model.fit(X_train, y_reg_train)

cls_model = RandomForestClassifier(n_estimators=200, random_state=42)
cls_model.fit(X_train, y_cls_train)

joblib.dump(reg_model, MODEL_DIR / "reg_model.pkl")
joblib.dump(cls_model, MODEL_DIR / "cls_model.pkl")
joblib.dump(le, MODEL_DIR / "label_encoder.pkl")

print("Models trained and saved.")
print("Features:", ", ".join(features))
