import html
import sys
from pathlib import Path

import streamlit as st
import pandas as pd
import altair as alt

# Streamlit Cloud starts the app from the app/ directory, so the repository
# root is not always available for imports. Adding it explicitly keeps shared
# packages such as model/ importable both locally and after deployment.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from db import get_dashboard_stats, init_db, insert_project
from model.predict import predict_risk
from risk_register import render_risk_register

st.set_page_config(
    page_title="Система управління ризиками",
    layout="wide"
)

st.markdown("""
<style>
    :root {
        --page-bg: #eef1f2;
        --panel: #ffffff;
        --panel-soft: #f7f9fa;
        --text: #1f2933;
        --muted: #667085;
        --border: #d7dde1;
        --primary: #0b5f7d;
        --primary-hover: #084b63;
        --success: #2fb978;
        --accent: #c46a1b;
        --danger: #c7352f;
        --navy: #084b7a;
    }

    .stApp {
        background: var(--page-bg);
        color: var(--text);
    }

    .block-container {
        max-width: 1240px;
        padding-top: 1.4rem;
        padding-bottom: 3rem;
    }

    [data-testid="stToolbar"],
    [data-testid="stDecoration"],
    [data-testid="stStatusWidget"],
    #MainMenu,
    header {
        display: none !important;
        visibility: hidden !important;
    }

    h1, h2, h3,
    div[data-testid="stHeading"] *,
    div[data-testid="stMarkdownContainer"] h1,
    div[data-testid="stMarkdownContainer"] h2,
    div[data-testid="stMarkdownContainer"] h3,
    div[data-testid="stMarkdownContainer"] strong,
    div[data-testid="stWidgetLabel"] *,
    div[data-testid="stRadio"] p,
    div[data-testid="stSegmentedControl"] p {
        letter-spacing: 0;
        font-weight: 400 !important;
    }

    label, button, strong {
        font-weight: 400 !important;
    }

    .hero-panel {
        align-items: center;
        background: #ffffff;
        border: 1px solid var(--border);
        border-left: 5px solid var(--primary);
        border-radius: 8px;
        box-shadow: 0 8px 18px rgba(18, 24, 31, 0.05);
        display: flex;
        justify-content: space-between;
        margin: 0.4rem 0 1.45rem;
        padding: 1.35rem 1.55rem;
    }

    .hero-title {
        color: var(--text);
        font-size: 2.15rem;
        font-weight: 400;
        line-height: 1.12;
        margin: 0.15rem 0 0.55rem;
    }

    .hero-copy {
        color: var(--muted);
        font-size: 1rem;
        line-height: 1.45;
        margin: 0;
    }

    .hero-side {
        background: var(--panel-soft);
        border: 1px solid var(--border);
        border-radius: 8px;
        color: var(--muted);
        font-size: 0.9rem;
        line-height: 1.35;
        max-width: 270px;
        padding: 0.85rem 1rem;
    }

    .hero-side span {
        color: var(--primary);
        display: block;
        font-size: 0.78rem;
        letter-spacing: 0.06em;
        margin-bottom: 0.25rem;
        text-transform: uppercase;
    }

    .form-heading {
        align-items: baseline;
        display: flex;
        justify-content: space-between;
        margin: 0.25rem 0 0.95rem;
    }

    .form-heading-title {
        color: var(--text);
        font-size: 1.45rem;
        font-weight: 400;
    }

    .form-heading-note {
        color: var(--muted);
        font-size: 0.92rem;
    }

    .app-kicker {
        color: var(--primary);
        font-size: 0.78rem;
        font-weight: 400;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        margin-bottom: 0.4rem;
    }

    .app-subtitle {
        color: var(--muted);
        font-size: 1.05rem;
        margin-top: -0.6rem;
        margin-bottom: 2.2rem;
    }

    .kpi-card {
        background: #ffffff;
        border: 1px solid var(--border);
        box-shadow: 0 8px 18px rgba(18, 24, 31, 0.06);
        min-height: 96px;
        padding: 1.1rem 1.25rem 1rem 1.45rem;
        position: relative;
    }

    .kpi-card::before {
        bottom: 0.85rem;
        content: "";
        left: 0;
        position: absolute;
        top: 0.85rem;
        width: 6px;
    }

    .kpi-card.green::before { background: var(--success); }
    .kpi-card.blue::before { background: var(--navy); }
    .kpi-card.orange::before { background: var(--accent); }
    .kpi-card.red::before { background: var(--danger); }

    .kpi-label {
        color: var(--text);
        font-size: 0.92rem;
        font-weight: 400;
        line-height: 1.25;
    }

    .kpi-value {
        color: #111827;
        float: right;
        font-size: 2.2rem;
        font-weight: 300;
        line-height: 1;
        margin-top: 0.2rem;
    }

    .insight-card {
        background: #ffffff;
        border: 1px solid var(--border);
        border-left: 5px solid var(--primary);
        border-radius: 8px;
        box-shadow: 0 6px 14px rgba(18, 24, 31, 0.04);
        color: var(--text);
        font-size: 0.98rem;
        line-height: 1.45;
        margin-bottom: 0.8rem;
        padding: 0.9rem 1rem;
    }

    .status-text {
        color: var(--success);
        font-size: 1rem;
        font-weight: 400;
        margin: 1rem 0 0.35rem;
    }

    .interpretation-card {
        background: #ffffff;
        border: 1px solid var(--border);
        border-radius: 8px;
        box-shadow: 0 6px 14px rgba(18, 24, 31, 0.04);
        min-height: 112px;
        padding: 1rem;
        position: relative;
    }

    .interpretation-card::before {
        border-radius: 8px 0 0 8px;
        bottom: 0;
        content: "";
        left: 0;
        position: absolute;
        top: 0;
        width: 5px;
    }

    .interpretation-card.low::before { background: var(--success); }
    .interpretation-card.moderate::before { background: var(--accent); }
    .interpretation-card.high::before { background: var(--danger); }

    .interpretation-title {
        color: var(--muted);
        font-size: 0.82rem;
        font-weight: 400;
        margin-bottom: 0.55rem;
        text-transform: uppercase;
    }

    .interpretation-level {
        color: var(--text);
        font-size: 1.25rem;
        font-weight: 400;
        margin-bottom: 0.35rem;
    }

    .interpretation-card.low .interpretation-level { color: var(--success); }
    .interpretation-card.moderate .interpretation-level { color: var(--accent); }
    .interpretation-card.high .interpretation-level { color: var(--danger); }

    .interpretation-note {
        color: var(--muted);
        font-size: 0.9rem;
        line-height: 1.35;
    }

    .section-label {
        color: var(--text);
        font-size: 1rem;
        font-weight: 400;
        margin: 1.1rem 0 0.85rem;
    }

    div[data-testid="stMarkdownContainer"] p {
        color: var(--text);
    }

    div[data-testid="stVerticalBlockBorderWrapper"] {
        background: #ffffff;
        border-color: var(--border);
        border-radius: 2px;
        box-shadow: 0 8px 18px rgba(18, 24, 31, 0.06);
    }

    section[data-testid="stSidebar"] {
        background: #ffffff;
        border-right: 1px solid var(--border);
    }

    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3,
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] label {
        font-weight: 400 !important;
    }

    .sidebar-title {
        color: var(--primary);
        font-size: 1.05rem;
        margin: 0.8rem 0 0.25rem;
    }

    .sidebar-note {
        color: var(--muted);
        font-size: 0.85rem;
        line-height: 1.35;
        margin-bottom: 1rem;
    }

    .dashboard-grid {
        display: grid;
        gap: 1rem;
        grid-template-columns: repeat(3, minmax(0, 1fr));
        margin-bottom: 1.15rem;
    }

    .dashboard-panel {
        background: #ffffff;
        border: 1px solid var(--border);
        border-radius: 8px;
        box-shadow: 0 6px 14px rgba(18, 24, 31, 0.04);
        padding: 1rem;
    }

    .dashboard-panel-title {
        color: var(--text);
        font-size: 1.12rem;
        margin-bottom: 0.75rem;
    }

    .recent-risk {
        border-bottom: 1px solid var(--border);
        padding: 0.75rem 0;
    }

    .recent-risk:last-child {
        border-bottom: 0;
    }

    .recent-risk-title {
        color: var(--text);
        font-size: 0.95rem;
        margin-bottom: 0.2rem;
    }

    .recent-risk-meta {
        color: var(--muted);
        font-size: 0.84rem;
    }

    div[data-testid="stTextInput"] input,
    div[data-testid="stNumberInput"] input,
    div[data-baseweb="select"] > div {
        border-radius: 8px;
        border: 1px solid var(--border);
        background-color: #ffffff;
        box-shadow: 0 1px 2px rgba(18, 24, 31, 0.04);
    }

    div[data-testid="stTextInput"] input:focus,
    div[data-testid="stNumberInput"] input:focus {
        border-color: var(--primary);
        box-shadow: 0 0 0 2px rgba(11, 95, 125, 0.14);
    }

    div[data-testid="stNumberInput"] button {
        background-color: #eef5f1;
        border-color: var(--border);
        color: var(--text);
    }

    div[data-testid="stRadio"] label,
    div[data-testid="stSegmentedControl"] label {
        color: var(--text);
    }

    div[data-testid="stRadio"] input[type="radio"] {
        accent-color: var(--primary);
    }

    div[data-testid="stRadio"] label:has(input:checked) {
        border-color: var(--primary) !important;
    }

    div[data-testid="stRadio"] label:has(input:checked) svg,
    div[data-testid="stRadio"] label:has(input:checked) svg * {
        fill: var(--primary) !important;
        stroke: var(--primary) !important;
    }

    div[data-testid="stRadio"] label:has(input:checked) svg circle:last-child {
        fill: #ffffff !important;
        stroke: #ffffff !important;
    }

    div[data-testid="stRadio"] [role="radiogroup"] {
        gap: 0.65rem;
    }

    div[data-testid="stRadio"] [role="radiogroup"] label {
        background: #ffffff;
        border: 1px solid var(--border);
        border-radius: 8px;
        padding: 0.5rem 0.75rem;
        min-height: 2.65rem;
    }

    div[data-testid="stRadio"] [role="radiogroup"] label:hover {
        border-color: var(--primary);
        background: #f7fbf9;
    }

    div[data-testid="stSegmentedControl"] button[aria-pressed="true"] {
        border-color: var(--primary);
        color: var(--primary);
    }

    div[data-testid="stSegmentedControl"] button[aria-selected="true"],
    div[data-testid="stSegmentedControl"] button[aria-checked="true"] {
        background-color: rgba(11, 95, 125, 0.10) !important;
        border-color: var(--primary) !important;
        color: var(--primary) !important;
    }

    div[data-testid="stSegmentedControl"] button[aria-pressed="true"]::before {
        background-color: var(--primary);
    }

    div[data-testid="stSegmentedControl"] button[aria-selected="true"]::before,
    div[data-testid="stSegmentedControl"] button[aria-checked="true"]::before {
        background-color: var(--primary) !important;
    }

    div[data-testid="stMetric"] {
        background: #ffffff;
        border: 1px solid var(--border);
        border-radius: 2px;
        padding: 1rem 1.1rem;
        box-shadow: 0 8px 18px rgba(18, 24, 31, 0.06);
    }

    div[data-testid="stMetric"] label {
        color: var(--muted);
    }

    div[data-testid="stMetricValue"] {
        color: var(--primary);
    }

    div.stButton > button {
        height: 3rem;
        border-radius: 8px;
        border: 0;
        background: var(--primary);
        color: #ffffff;
        font-weight: 400;
        box-shadow: 0 10px 20px rgba(11, 95, 125, 0.22);
    }

    div.stButton > button:hover {
        background: var(--primary-hover);
        color: #ffffff;
        border: 0;
    }

    hr {
        border-color: var(--border);
    }
</style>
""", unsafe_allow_html=True)

init_db()

st.sidebar.markdown(
    """
    <div class="sidebar-title">Система управління ризиками</div>
    <div class="sidebar-note">Прогнозування ризиків та операційний реєстр.</div>
    """,
    unsafe_allow_html=True
)

page = st.sidebar.radio(
    "Навігація",
    ["Дашборд", "Оцінка ризиків", "Реєстр ризиків"]
)


def render_dashboard():
    stats = get_dashboard_stats()

    st.markdown(
        """
        <div class="hero-panel">
            <div>
                <div class="app-kicker">Огляд управління ризиками</div>
                <div class="hero-title">Дашборд</div>
                <p class="hero-copy">Короткий огляд проєктів, зареєстрованих ризиків та поточного операційного статусу.</p>
            </div>
            <div class="hero-side">
                <span>Зведення системи</span>
                Використовуйте оцінку ризиків для прогнозу, а реєстр ризиків — для щоденного контролю.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    card1, card2, card3, card4 = st.columns(4)
    card1.markdown(
        f'<div class="kpi-card blue"><div class="kpi-label">Проєкти</div><div class="kpi-value">{stats["project_count"]}</div></div>',
        unsafe_allow_html=True
    )
    card2.markdown(
        f'<div class="kpi-card orange"><div class="kpi-label">Зареєстровані ризики</div><div class="kpi-value">{stats["risk_count"]}</div></div>',
        unsafe_allow_html=True
    )
    card3.markdown(
        f'<div class="kpi-card red"><div class="kpi-label">Високі ризики</div><div class="kpi-value">{stats["high_count"]}</div></div>',
        unsafe_allow_html=True
    )
    card4.markdown(
        f'<div class="kpi-card green"><div class="kpi-label">Закриті ризики</div><div class="kpi-value">{stats["closed_count"]}</div></div>',
        unsafe_allow_html=True
    )

    st.write("")

    left, right = st.columns(2, gap="large")

    with left:
        st.markdown('<div class="dashboard-panel"><div class="dashboard-panel-title">Ризики за статусом</div>', unsafe_allow_html=True)
        status_data = pd.DataFrame(stats["risk_statuses"], columns=["Статус", "Кількість"])
        if status_data.empty:
            st.markdown('<div class="insight-card">Ризики ще не зареєстровані.</div>', unsafe_allow_html=True)
        else:
            status_chart = (
                alt.Chart(status_data)
                .mark_arc(innerRadius=58, outerRadius=98)
                .encode(
                    theta=alt.Theta("Кількість:Q"),
                    color=alt.Color(
                        "Статус:N",
                        scale=alt.Scale(
                            domain=["Відкритий", "В роботі", "Закритий"],
                            range=["#0b5f7d", "#c46a1b", "#2fb978"]
                        ),
                        legend=alt.Legend(title=None, orient="bottom")
                    ),
                    tooltip=["Статус:N", "Кількість:Q"]
                )
                .properties(height=260)
            )
            st.altair_chart(status_chart, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with right:
        st.markdown('<div class="dashboard-panel"><div class="dashboard-panel-title">Проєкти за типом</div>', unsafe_allow_html=True)
        type_data = pd.DataFrame(stats["project_types"], columns=["Тип проєкту", "Кількість"])
        type_labels = {
            "core": "Автоматизована банківська система",
            "integrations": "Інтеграції",
            "data": "Дані",
            "security": "Безпека",
            "channels": "Канали",
            "infrastructure": "Інфраструктура",
            "automation": "Автоматизація",
            "n/a": "н/д"
        }
        if not type_data.empty:
            type_data["Тип проєкту"] = type_data["Тип проєкту"].map(lambda value: type_labels.get(value, value))
        if type_data.empty:
            st.markdown('<div class="insight-card">Проєкти ще не створені.</div>', unsafe_allow_html=True)
        else:
            type_chart = (
                alt.Chart(type_data)
                .mark_bar(cornerRadiusTopRight=4, cornerRadiusBottomRight=4, color="#0b5f7d")
                .encode(
                    x=alt.X("Кількість:Q", title=None),
                    y=alt.Y("Тип проєкту:N", title=None, sort="-x"),
                    tooltip=[alt.Tooltip("Тип проєкту:N"), alt.Tooltip("Кількість:Q")]
                )
                .properties(height=260)
            )
            st.altair_chart(type_chart, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown(
        """
        <div class="form-heading">
            <div class="form-heading-title">Останні ризики</div>
            <div class="form-heading-note">Останні записи з операційного реєстру</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    if not stats["recent_risks"]:
        st.markdown('<div class="insight-card">Останніх ризиків ще немає. Додайте перший у реєстрі ризиків.</div>', unsafe_allow_html=True)
        return

    for description, project_name, status, impact, probability in stats["recent_risks"]:
        description = html.escape(description)
        project_name = html.escape(project_name)
        status = html.escape(status)
        impact = html.escape(impact)
        st.markdown(
            f"""
            <div class="recent-risk">
                <div class="recent-risk-title">{description}</div>
                <div class="recent-risk-meta">{project_name} | {status} | вплив: {impact} | ймовірність: {probability:.2f}</div>
            </div>
            """,
            unsafe_allow_html=True
        )


if page == "Дашборд":
    render_dashboard()
    st.stop()

if page == "Реєстр ризиків":
    render_risk_register()
    st.stop()

st.markdown(
    """
    <div class="hero-panel">
        <div>
            <div class="app-kicker">Інтелектуальна оцінка ризиків</div>
            <div class="hero-title">Оцінка ризиків</div>
            <p class="hero-copy">Оцініть ризики строків, бюджету, обсягу та ресурсів до старту проєкту.</p>
        </div>
        <div class="hero-side">
            <span>Режим оцінки</span>
            Заповніть контекст проєкту й запустіть прогноз за чотирма ключовими напрямами.
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <div class="form-heading">
        <div class="form-heading-title">Створити новий проєкт</div>
        <div class="form-heading-note">Обов’язкові вхідні дані для моделі прогнозування</div>
    </div>
    """,
    unsafe_allow_html=True
)

with st.container(border=True):
    st.markdown(
        """
        <div class="form-heading">
            <div class="form-heading-title">Оцінка проєкту</div>
            <div class="form-heading-note">Профіль проєкту та контекст виконання</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    left, right = st.columns([1, 1], gap="large")

    with left:
        st.markdown('<div class="section-label">Профіль проєкту</div>', unsafe_allow_html=True)
        name = st.text_input("Назва проєкту")

        project_type = st.selectbox(
            "Тип проєкту",
            [
                "Автоматизована банківська система", "Інтеграції", "Дані", "Безпека",
                "Канали", "Інфраструктура", "Автоматизація"
            ]
        )

        owner = st.selectbox(
            "Власник",
            [
                "Бізнес", "Офіс даних", "Безпека",
                "Ризики", "Бухгалтерія", "Кредити"
            ]
        )

        vendors = st.multiselect(
            "Постачальники",
            [
                "Залізна Людина", "Тор", "Галк", "Капітан Америка",
                "Чорна Вдова", "Соколине Око", "Доктор Стрендж"
            ]
        )

        estimate_col1, estimate_col2 = st.columns(2)
        with estimate_col1:
            budget = st.number_input(
                "Бюджет (€)",
                min_value=0,
                max_value=1000000,
                step=5000
            )
        with estimate_col2:
            duration = st.number_input(
                "Тривалість (людино-дні)",
                min_value=10,
                max_value=400,
                value=60,
                step=10
            )

    with right:
        st.markdown('<div class="section-label">Контекст виконання</div>', unsafe_allow_html=True)

        clarity = st.radio(
            "Чіткість вимог",
            ["Чіткі", "Часткові", "Нечіткі"],
            horizontal=True
        )

        experience = st.radio(
            "Досвід постачальника",
            ["Підтверджений", "Частковий", "Відсутній"],
            horizontal=True
        )

        regulatory = st.radio(
            "Регуляторний вплив",
            ["Відсутній", "Помірний", "Високий"],
            horizontal=True
        )

        criticality = st.radio(
            "Рівень критичності",
            ["Низький", "Середній", "Критичний"],
            horizontal=True
        )

        submitted_assessment = st.button("Оцінити ризики", use_container_width=True)

# Translate user-facing Ukrainian option labels into the numeric feature values
# expected by the trained model. Keeping this mapping close to the form makes it
# easier to verify that UI choices and model inputs stay aligned.
clarity_map = {
    "Чіткі": 0,
    "Часткові": 1,
    "Нечіткі": 2
}

experience_map = {
    "Підтверджений": 0,
    "Частковий": 1,
    "Відсутній": 2
}

regulatory_map = {
    "Відсутній": 0,
    "Помірний": 1,
    "Високий": 2
}

criticality_map = {
    "Низький": 0,
    "Середній": 1,
    "Критичний": 2
}

change_by_clarity = {
    "Чіткі": 2,
    "Часткові": 5,
    "Нечіткі": 8
}

# The assessment action persists the project for later tracking, prepares the
# model feature vector, and then renders the prediction output in the same view.
if submitted_assessment:
    changes = change_by_clarity[clarity]

    # Preserve the original project context in SQLite so it can be selected from
    # the Risk Register module after the initial assessment is complete.
    project_data = {
        "name": name,
        "type": project_type,
        "owner": owner,
        "vendors": vendors,
        "budget": budget,
        "duration": duration,
        "changes": changes,
        "clarity": clarity,
        "experience": experience,
        "regulatory": regulatory,
        "criticality": criticality
    }

    insert_project(project_data)

    # Build the exact feature schema used during training. Extra UI-only fields
    # such as project name are intentionally excluded from the prediction call.
    ml_data = {
        "project_type": project_type,
        "owner": owner,
        "duration_md": duration,
        "vendor_count": len(vendors),
        "changes_count": changes,
        "requirements_clarity": clarity_map[clarity],
        "vendor_experience": experience_map[experience],
        "regulatory_impact": regulatory_map[regulatory],
        "criticality": criticality_map[criticality],
        "budget": budget
    }

    # Run the trained model and convert the returned risk values into UI metrics.
    result = predict_risk(ml_data)

    # Present the four predicted risk dimensions as compact KPI cards so the user
    # can scan the result before reading the detailed interpretation.
    st.markdown('<div class="status-text">Оцінку ризиків завершено</div>', unsafe_allow_html=True)

    st.subheader("Огляд ризиків")

    metric1, metric2, metric3, metric4 = st.columns(4)

    deadline = result["deadline"] * 100
    budget_risk = result["budget"] * 100
    scope = result["scope"] * 100
    resources = result["resources"] * 100

    def kpi_card(column, label, value, color_class):
        column.markdown(
            f"""
            <div class="kpi-card {color_class}">
                <div class="kpi-label">{label}</div>
                <div class="kpi-value">{value:.0f}%</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    kpi_card(metric1, "Ризик строків", deadline, "blue")
    kpi_card(metric2, "Ризик бюджету", budget_risk, "orange")
    kpi_card(metric3, "Ризик обсягу", scope, "red")
    kpi_card(metric4, "Ризик ресурсів", resources, "green")

    # Aggregate the four dimensions into a single project-level indicator. This
    # is a simple dashboard summary, not a separate ML prediction.
    overall = (deadline + budget_risk + scope + resources) / 4

    st.subheader("Загальний ризик проєкту")
    st.markdown(
        f"""
        <div class="kpi-card blue">
            <div class="kpi-label">Загальний рівень ризику</div>
            <div class="kpi-value">{overall:.0f}%</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Convert numeric percentages into business-friendly labels used by the
    # interpretation cards. Thresholds are intentionally simple for explainability.
    def interpret(value):
        if value < 30:
            return "Низький", "Стабільні умови", "low"
        elif value < 60:
            return "Помірний", "Потребує уваги", "moderate"
        else:
            return "Високий", "Потрібні заходи зниження", "high"

    def interpretation_card(column, title, value):
        level, note, level_class = interpret(value)
        column.markdown(
            f"""
            <div class="interpretation-card {level_class}">
                <div class="interpretation-title">{title}</div>
                <div class="interpretation-level">{level}</div>
                <div class="interpretation-note">{note}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.subheader("Інтерпретація")

    int1, int2, int3, int4 = st.columns(4)
    interpretation_card(int1, "Строки", deadline)
    interpretation_card(int2, "Бюджет", budget_risk)
    interpretation_card(int3, "Обсяг", scope)
    interpretation_card(int4, "Ресурси", resources)

    # Highlight the most likely drivers behind elevated risks. These rules make
    # the model output easier to discuss in a project-management context.
    st.subheader("Фактори ризику")

    def insight_card(message):
        st.markdown(
            f'<div class="insight-card">{message}</div>',
            unsafe_allow_html=True
        )

    if resources > 40:
        insight_card("Ресурсний ризик пов’язаний із кількістю постачальників або недостатнім досвідом")

    if deadline > 40:
        insight_card("Ризик строків зростає через тривалість проєкту")

    if scope > 40:
        insight_card("Нестабільність обсягу пов’язана з нечіткими вимогами")

    if budget_risk > 40:
        insight_card("Бюджетний ризик може бути пов’язаний зі складністю або постачальниками")

    # Use a lightweight dot plot instead of bars so the distribution reads as a
    # comparison of risk scores rather than progress toward completion.
    st.subheader("Розподіл ризиків")

    chart_data = pd.DataFrame({
        "Ризик": ["Строки", "Бюджет", "Обсяг", "Ресурси"],
        "Значення": [deadline, budget_risk, scope, resources],
        "Колір": ["#084b7a", "#c46a1b", "#c7352f", "#2fb978"]
    })

    points = (
        alt.Chart(chart_data)
        .mark_circle(size=260)
        .encode(
            x=alt.X("Значення:Q", title="Рівень ризику (%)", scale=alt.Scale(domain=[0, 100])),
            y=alt.Y("Ризик:N", title=None, sort=None),
            color=alt.Color("Колір:N", scale=None, legend=None),
            tooltip=[
                alt.Tooltip("Ризик:N", title="Ризик"),
                alt.Tooltip("Значення:Q", title="Оцінка", format=".0f")
            ],
        )
    )

    labels = (
        alt.Chart(chart_data)
        .mark_text(align="left", dx=12, color="#1f2933", fontSize=13)
        .encode(
            x=alt.X("Значення:Q", title="Рівень ризику (%)", scale=alt.Scale(domain=[0, 100])),
            y=alt.Y("Ризик:N", title=None, sort=None),
            text=alt.Text("Значення:Q", format=".0f")
        )
    )

    chart = (points + labels).properties(height=260)

    st.altair_chart(chart, use_container_width=True)
