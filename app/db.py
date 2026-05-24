import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "data", "database.db")

def init_db():
    os.makedirs(os.path.join(BASE_DIR, "data"), exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Project profiles are saved after assessment and reused in the register.
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS projects (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        project_type TEXT,
        owner TEXT,
        budget INTEGER,
        duration_md INTEGER,
        vendors TEXT,
        vendor_count INTEGER,
        changes_count INTEGER,
        requirements_clarity TEXT,
        vendor_experience TEXT,
        regulatory_impact INTEGER,
        criticality TEXT,

        risk_deadline REAL,
        risk_budget REAL,
        risk_scope REAL,
        risk_resource REAL,
        risk_level TEXT,

        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # Register records are stored separately from assessment results.
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS risks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        project_id INTEGER,
        description TEXT,
        probability REAL,
        impact TEXT,
        mitigation TEXT,
        status TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()
    conn.close()


def insert_project(data):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    regulatory_map = {
        "No regulatory constraints": 0,
        "Moderate regulatory requirements": 1,
        "High regulatory pressure": 2,
        "None": 0,
        "Moderate": 1,
        "High": 2,
        "Відсутній": 0,
        "Помірний": 1,
        "Високий": 2
    }

    cursor.execute("""
        INSERT INTO projects (
            name, project_type, owner, budget,
            duration_md, vendors, vendor_count,
            changes_count, requirements_clarity,
            vendor_experience, regulatory_impact,
            criticality
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data["name"],
        data["type"],
        data["owner"],
        data["budget"],
        data["duration"],
        ",".join(data["vendors"]),
        len(data["vendors"]),
        data["changes"],
        data["clarity"],
        data["experience"],
        regulatory_map.get(data["regulatory"], 0),
        data["criticality"]
    ))

    conn.commit()
    conn.close()


def get_projects():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, name, project_type, owner, created_at
        FROM projects
        ORDER BY created_at DESC, id DESC
    """)
    projects = cursor.fetchall()

    conn.close()
    return projects


def insert_risk(data):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO risks (
            project_id, description, probability,
            impact, mitigation, status
        )
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        data["project_id"],
        data["description"],
        data["probability"],
        data["impact"],
        data["mitigation"],
        data["status"]
    ))

    conn.commit()
    conn.close()


def update_risk(risk_id, data):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE risks
        SET description = ?,
            probability = ?,
            impact = ?,
            mitigation = ?,
            status = ?
        WHERE id = ?
    """, (
        data["description"],
        data["probability"],
        data["impact"],
        data["mitigation"],
        data["status"],
        risk_id
    ))

    conn.commit()
    conn.close()


def get_project_risks(project_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, description, probability, impact, mitigation, status, created_at
        FROM risks
        WHERE project_id = ?
        ORDER BY created_at DESC, id DESC
    """, (project_id,))
    risks = cursor.fetchall()

    conn.close()
    return risks


def get_dashboard_stats():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    project_count = cursor.execute("SELECT COUNT(*) FROM projects").fetchone()[0]
    risk_count = cursor.execute("SELECT COUNT(*) FROM risks").fetchone()[0]
    open_count = cursor.execute("""
        SELECT COUNT(*)
        FROM risks
        WHERE COALESCE(status, 'Відкритий') IN ('Open', 'Відкритий')
    """).fetchone()[0]
    in_progress_count = cursor.execute("""
        SELECT COUNT(*)
        FROM risks
        WHERE COALESCE(status, 'Відкритий') IN ('In Progress', 'В роботі')
    """).fetchone()[0]
    closed_count = cursor.execute("""
        SELECT COUNT(*)
        FROM risks
        WHERE COALESCE(status, 'Відкритий') IN ('Closed', 'Закритий')
    """).fetchone()[0]
    high_count = cursor.execute("""
        SELECT COUNT(*)
        FROM risks
        WHERE COALESCE(probability, 0) *
            CASE COALESCE(impact, 'Середній')
                WHEN 'Low' THEN 1
                WHEN 'Низький' THEN 1
                WHEN 'Medium' THEN 2
                WHEN 'Середній' THEN 2
                WHEN 'High' THEN 3
                WHEN 'Високий' THEN 3
                ELSE 2
            END >= 1.5
    """).fetchone()[0]

    project_types = cursor.execute("""
        SELECT LOWER(COALESCE(project_type, 'n/a')) AS project_type, COUNT(*) AS count
        FROM projects
        GROUP BY LOWER(COALESCE(project_type, 'n/a'))
        ORDER BY count DESC
    """).fetchall()

    risk_statuses = cursor.execute("""
        SELECT
            CASE COALESCE(status, 'Відкритий')
                WHEN 'Open' THEN 'Відкритий'
                WHEN 'In Progress' THEN 'В роботі'
                WHEN 'Closed' THEN 'Закритий'
                ELSE COALESCE(status, 'Відкритий')
            END AS status,
            COUNT(*) AS count
        FROM risks
        GROUP BY
            CASE COALESCE(status, 'Відкритий')
                WHEN 'Open' THEN 'Відкритий'
                WHEN 'In Progress' THEN 'В роботі'
                WHEN 'Closed' THEN 'Закритий'
                ELSE COALESCE(status, 'Відкритий')
            END
        ORDER BY count DESC
    """).fetchall()

    recent_risks = cursor.execute("""
        SELECT
            COALESCE(r.description, 'Ризик без назви') AS description,
            COALESCE(p.name, 'Проєкт без назви') AS project_name,
            CASE COALESCE(r.status, 'Відкритий')
                WHEN 'Open' THEN 'Відкритий'
                WHEN 'In Progress' THEN 'В роботі'
                WHEN 'Closed' THEN 'Закритий'
                ELSE COALESCE(r.status, 'Відкритий')
            END AS status,
            CASE COALESCE(r.impact, 'Середній')
                WHEN 'Low' THEN 'Низький'
                WHEN 'Medium' THEN 'Середній'
                WHEN 'High' THEN 'Високий'
                ELSE COALESCE(r.impact, 'Середній')
            END AS impact,
            COALESCE(r.probability, 0) AS probability
        FROM risks r
        LEFT JOIN projects p ON p.id = r.project_id
        ORDER BY r.created_at DESC, r.id DESC
        LIMIT 5
    """).fetchall()

    conn.close()

    return {
        "project_count": project_count,
        "risk_count": risk_count,
        "open_count": open_count,
        "in_progress_count": in_progress_count,
        "closed_count": closed_count,
        "high_count": high_count,
        "project_types": project_types,
        "risk_statuses": risk_statuses,
        "recent_risks": recent_risks
    }
