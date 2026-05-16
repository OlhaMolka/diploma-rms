import html

import pandas as pd
import streamlit as st

from db import get_project_risks, get_projects, insert_risk


IMPACT_SCORE = {
    "Low": 1,
    "Низький": 1,
    "Medium": 2,
    "Середній": 2,
    "High": 3,
    "Високий": 3,
}

IMPACT_LABEL = {
    "Low": "Низький",
    "Medium": "Середній",
    "High": "Високий",
    "Низький": "Низький",
    "Середній": "Середній",
    "Високий": "Високий",
}

STATUS_LABEL = {
    "Open": "Відкритий",
    "In Progress": "В роботі",
    "Closed": "Закритий",
    "Відкритий": "Відкритий",
    "В роботі": "В роботі",
    "Закритий": "Закритий",
}

PROJECT_TYPE_LABEL = {
    "core": "Автоматизована банківська система",
    "integrations": "Інтеграції",
    "data": "Дані",
    "security": "Безпека",
    "channels": "Канали",
    "infrastructure": "Інфраструктура",
    "automation": "Автоматизація",
}


def _score(probability, impact):
    probability = probability or 0
    impact = impact or "Середній"
    return round(probability * IMPACT_SCORE.get(impact, IMPACT_SCORE["Середній"]), 2)


def _score_level(score):
    if score < 0.7:
        return "Низький"
    if score < 1.5:
        return "Середній"
    return "Високий"


def _status_class(status):
    status = STATUS_LABEL.get(status or "Відкритий", status or "Відкритий")
    return {
        "Відкритий": "open",
        "В роботі": "in-progress",
        "Закритий": "closed",
    }.get(status, "open")


def _level_class(level):
    return {
        "Низький": "low",
        "Середній": "medium",
        "Високий": "high",
    }.get(level, "medium")


def _risk_card(row):
    score = _score(row["Ймовірність"], row["Вплив"])
    level = _score_level(score)
    status_value = STATUS_LABEL.get(row["Статус"] or "Відкритий", row["Статус"] or "Відкритий")
    description = html.escape(row["Ризик"] or "Ризик без назви")
    mitigation = html.escape(row["План реагування"] or "План реагування ще не додано.")
    status = html.escape(status_value)

    st.markdown(
        f"""
        <div class="risk-register-card">
            <div class="risk-card-main">
                <div class="risk-card-title">{description}</div>
                <div class="risk-card-note">{mitigation}</div>
            </div>
            <div class="risk-card-meta">
                <div class="risk-pill status-{_status_class(status_value)}">{status}</div>
                <div class="risk-score">{score:.2f}</div>
                <div class="risk-level {_level_class(level)}">{level}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


def render_risk_register():
    st.markdown(
        """
        <style>
            .risk-register-card {
                align-items: center;
                background: #ffffff;
                border: 1px solid var(--border);
                border-left: 5px solid var(--primary);
                border-radius: 8px;
                box-shadow: 0 6px 14px rgba(18, 24, 31, 0.04);
                display: flex;
                gap: 1rem;
                justify-content: space-between;
                margin-bottom: 0.75rem;
                padding: 0.95rem 1rem;
            }

            .risk-card-main {
                min-width: 0;
            }

            .risk-card-title {
                color: var(--text);
                font-size: 1rem;
                margin-bottom: 0.25rem;
            }

            .risk-card-note {
                color: var(--muted);
                font-size: 0.88rem;
                line-height: 1.35;
            }

            .risk-card-meta {
                align-items: center;
                display: flex;
                flex-shrink: 0;
                gap: 0.65rem;
            }

            .risk-pill,
            .risk-level {
                border-radius: 999px;
                font-size: 0.82rem;
                padding: 0.32rem 0.7rem;
            }

            .risk-pill {
                background: #eef4f7;
                color: var(--primary);
            }

            .status-closed {
                background: rgba(47, 185, 120, 0.12);
                color: var(--success);
            }

            .status-in-progress {
                background: rgba(196, 106, 27, 0.12);
                color: var(--accent);
            }

            .status-open {
                background: rgba(11, 95, 125, 0.10);
                color: var(--primary);
            }

            .risk-score {
                color: var(--text);
                font-size: 1.2rem;
            }

            .risk-level.low {
                background: rgba(47, 185, 120, 0.12);
                color: var(--success);
            }

            .risk-level.medium {
                background: rgba(196, 106, 27, 0.12);
                color: var(--accent);
            }

            .risk-level.high {
                background: rgba(199, 53, 47, 0.12);
                color: var(--danger);
            }
        </style>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div class="hero-panel">
            <div>
                <div class="app-kicker">Операційний контроль ризиків</div>
                <div class="hero-title">Реєстр ризиків</div>
                <p class="hero-copy">Відстежуйте ідентифіковані ризики проєкту, плани реагування та поточний статус виконання.</p>
            </div>
            <div class="hero-side">
                <span>Режим реєстру</span>
                Оберіть проєкт, додайте ризики та контролюйте ймовірність, вплив і заходи реагування.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    projects = get_projects()

    if not projects:
        st.info("Спочатку створіть проєкт на сторінці оцінки ризиків. Для реєстру потрібен щонайменше один проєкт.")
        return

    project_options = {
        f"{name or 'Проєкт без назви'} | {PROJECT_TYPE_LABEL.get((project_type or '').lower(), project_type or 'н/д')} | #{project_id}": project_id
        for project_id, name, project_type, owner, created_at in projects
    }

    selected_project = st.selectbox("Оберіть проєкт", list(project_options.keys()))
    project_id = project_options[selected_project]

    form_col, list_col = st.columns([0.9, 1.1], gap="large")

    with form_col:
        with st.container(border=True):
            st.markdown(
                """
                <div class="form-heading">
                    <div class="form-heading-title">Додати ризик</div>
                    <div class="form-heading-note">Операційний ризик проєкту</div>
                </div>
                """,
                unsafe_allow_html=True
            )

            with st.form("add_risk_form", clear_on_submit=True):
                description = st.text_input("Опис ризику")

                probability = st.number_input(
                    "Ймовірність",
                    min_value=0.0,
                    max_value=1.0,
                    value=0.3,
                    step=0.05
                )

                impact = st.segmented_control(
                    "Вплив",
                    ["Низький", "Середній", "Високий"],
                    default="Середній"
                )
                impact = impact or "Середній"

                mitigation = st.text_area("План реагування", height=120)

                status = st.segmented_control(
                    "Статус",
                    ["Відкритий", "В роботі", "Закритий"],
                    default="Відкритий"
                )
                status = status or "Відкритий"

                submitted = st.form_submit_button("Додати ризик", use_container_width=True)

            if submitted:
                if not description.strip():
                    st.error("Опис ризику є обов’язковим.")
                else:
                    insert_risk({
                        "project_id": project_id,
                        "description": description.strip(),
                        "probability": probability,
                        "impact": impact,
                        "mitigation": mitigation.strip(),
                        "status": status
                    })
                    st.markdown('<div class="status-text">Ризик додано</div>', unsafe_allow_html=True)

    with list_col:
        st.markdown(
            """
            <div class="form-heading">
                <div class="form-heading-title">Ризики проєкту</div>
                <div class="form-heading-note">Оцінка = ймовірність × вплив</div>
            </div>
            """,
            unsafe_allow_html=True
        )

        risk_rows = get_project_risks(project_id)

        if not risk_rows:
            st.markdown(
                '<div class="insight-card">Для цього проєкту ще не зареєстровано ризиків.</div>',
                unsafe_allow_html=True
            )
            return

        risks = pd.DataFrame(
            risk_rows,
            columns=["ID", "Ризик", "Ймовірність", "Вплив", "План реагування", "Статус", "Створено"]
        )
        risks["Ризик"] = risks["Ризик"].fillna("Ризик без назви")
        risks["Ймовірність"] = risks["Ймовірність"].fillna(0)
        risks["Вплив"] = risks["Вплив"].fillna("Середній").map(lambda value: IMPACT_LABEL.get(value, value))
        risks["План реагування"] = risks["План реагування"].fillna("")
        risks["Статус"] = risks["Статус"].fillna("Відкритий").map(lambda value: STATUS_LABEL.get(value, value))
        risks["Оцінка"] = risks.apply(lambda row: _score(row["Ймовірність"], row["Вплив"]), axis=1)
        risks["Рівень"] = risks["Оцінка"].apply(_score_level)

        total = len(risks)
        open_count = int((risks["Статус"] == "Відкритий").sum())
        high_count = int((risks["Рівень"] == "Високий").sum())

        metric1, metric2, metric3 = st.columns(3)
        metric1.markdown(
            f'<div class="kpi-card blue"><div class="kpi-label">Усього ризиків</div><div class="kpi-value">{total}</div></div>',
            unsafe_allow_html=True
        )
        metric2.markdown(
            f'<div class="kpi-card orange"><div class="kpi-label">Відкриті</div><div class="kpi-value">{open_count}</div></div>',
            unsafe_allow_html=True
        )
        metric3.markdown(
            f'<div class="kpi-card red"><div class="kpi-label">Високий рівень</div><div class="kpi-value">{high_count}</div></div>',
            unsafe_allow_html=True
        )

        st.write("")

        for _, row in risks.iterrows():
            _risk_card(row)

        st.dataframe(
            risks[["Ризик", "Ймовірність", "Вплив", "Оцінка", "Рівень", "Статус"]],
            hide_index=True,
            use_container_width=True
        )
