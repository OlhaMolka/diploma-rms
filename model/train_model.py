import pandas as pd
import joblib
import sklearn

from sklearn.model_selection import train_test_split
from sklearn.multioutput import MultiOutputRegressor
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.preprocessing import LabelEncoder

# Historical project dataset used for model training.
df = pd.read_excel("../data/projects_dataset_v7.xlsx")

# Categorical drivers are encoded to match the assessment form.
clarity_map = {
    "Clearly defined and approved": 0,
    "Partially defined, уточнення можливі": 1,
    "Unclear and evolving": 2
}

experience_map = {
    "Proven experience with similar projects": 0,
    "Partial experience": 1,
    "New vendor / no relevant experience": 2
}

regulatory_map = {
    "No regulatory constraints": 0,
    "Internal compliance requirements": 1,
    "Strict external regulation": 2
}

criticality_map = {
    "Minimal impact": 0,
    "Noticeable impact": 1,
    "Serious business disruption": 2,
    "Critical for bank operations": 3
}

df["requirements_clarity"] = df["requirements_clarity"].map(clarity_map)
df["vendor_experience"] = df["vendor_experience"].map(experience_map)
df["regulatory_impact"] = df["regulatory_impact"].map(regulatory_map)
df["criticality"] = df["criticality"].map(criticality_map)

features = [
    "budget",
    "duration_md",
    "vendor_count",
    "changes_count",
    "requirements_clarity",
    "vendor_experience",
    "regulatory_impact",
    "criticality"
]

X = df[features]

y_reg = df[[
    "risk_deadline_delay",
    "risk_budget_overrun",
    "risk_scope_change",
    "risk_resource_issue"
]]

le = LabelEncoder()
y_cls = le.fit_transform(df["risk_level"])

X_train, X_test, y_reg_train, y_reg_test = train_test_split(X, y_reg, test_size=0.2, random_state=42)
_, _, y_cls_train, y_cls_test = train_test_split(X, y_cls, test_size=0.2, random_state=42)

reg_model = MultiOutputRegressor(RandomForestRegressor(n_estimators=100, random_state=42))
reg_model.fit(X_train, y_reg_train)

cls_model = RandomForestClassifier(n_estimators=100, random_state=42)
cls_model.fit(X_train, y_cls_train)

joblib.dump(reg_model, "reg_model.pkl")
joblib.dump(cls_model, "cls_model.pkl")
joblib.dump(le, "label_encoder.pkl")

print("Models trained and saved.")
