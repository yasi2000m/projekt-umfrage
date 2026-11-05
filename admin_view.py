from __future__ import annotations

import hmac

import altair as alt
import pandas as pd
import streamlit as st

from database import (
    create_survey,
    delete_survey,
    list_surveys,
    set_survey_active,
    survey_results,
    update_survey,
)


CHART_COLORS = ["#6750E8", "#FF7A6E", "#24B8A6", "#F5B84B", "#4F8DE8", "#B45CE0"]


def _admin_password() -> str:
    try:
        return str(st.secrets.get("ADMIN_PASSWORD", "7777"))
    except FileNotFoundError:
        return "7777"


def _render_login() -> None:
    left, center, right = st.columns([1, 1.35, 1])
    with center:
        with st.container(border=True):
            st.markdown("### 🔐 Admin-Anmeldung")
            st.caption("Melde dich an, um Umfragen zu erstellen und auszuwerten.")
            with st.form("admin_login"):
                password = st.text_input("Passwort", type="password")
                login = st.form_submit_button("Sicher anmelden", type="primary", width="stretch")
            if login:
                if hmac.compare_digest(password, _admin_password()):
                    st.session_state.admin_authenticated = True
                    st.rerun()
                else:
                    st.error("Das Passwort ist nicht korrekt.")


def _default_question() -> dict:
    return {"text": "", "type": "single", "options": ["", ""]}


def _clear_builder_widgets(prefix: str) -> None:
    for key in list(st.session_state):
        if key.startswith(f"{prefix}_") and key != f"{prefix}_builder":
            del st.session_state[key]


def _render_builder_fields(builder: dict, prefix: str) -> None:
    builder["title"] = st.text_input(
        "Titel der Umfrage",
        value=builder["title"],
        placeholder="z. B. Fußball-Favoriten 2026",
        key=f"{prefix}_title",
    )

    for question_index, question in enumerate(builder["questions"]):
        with st.container(border=True):
            header_col, remove_col = st.columns([5, 1])
            header_col.markdown(f"#### Frage {question_index + 1}")
            if len(builder["questions"]) > 1 and remove_col.button(
                "Entfernen",
                key=f"{prefix}_remove_question_{question_index}",
                width="stretch",
            ):
                builder["questions"].pop(question_index)
                _clear_builder_widgets(prefix)
                st.rerun()

            question["text"] = st.text_area(
                "Fragetext",
                value=question["text"],
                placeholder="z. B. Wer ist der beste Fußballer?",
                key=f"{prefix}_question_text_{question_index}",
            )
            type_label = st.radio(
                "Auswahlart",
                ["Nur eine Antwort", "Mehrere Antworten"],
                index=0 if question["type"] == "single" else 1,
                horizontal=True,
                key=f"{prefix}_question_type_{question_index}",
            )
            question["type"] = "single" if type_label == "Nur eine Antwort" else "multiple"

            st.markdown("**Antwortoptionen**")
            for option_index, option in enumerate(question["options"]):
                option_col, delete_col = st.columns([6, 1])
                question["options"][option_index] = option_col.text_input(
                    f"Option {option_index + 1}",
                    value=option,
                    placeholder=f"Option {option_index + 1}",
                    key=f"{prefix}_option_{question_index}_{option_index}",
                    label_visibility="collapsed",
                )
                if len(question["options"]) > 2 and delete_col.button(
                    "✕",
                    key=f"{prefix}_remove_option_{question_index}_{option_index}",
                    help="Option entfernen",
                ):
                    question["options"].pop(option_index)
                    _clear_builder_widgets(prefix)
                    st.rerun()

            if st.button(
                "+ Option hinzufügen",
                key=f"{prefix}_add_option_{question_index}",
                width="stretch",
            ):
                question["options"].append("")
                st.rerun()

    if st.button(
        "+ Weitere Frage erstellen",
        key=f"{prefix}_add_question",
        width="stretch",
    ):
        builder["questions"].append(_default_question())
        st.rerun()


def _render_create() -> None:
    if "create_builder" not in st.session_state:
        st.session_state.create_builder = {"title": "", "questions": [_default_question()]}
    builder = st.session_state.create_builder

    st.markdown("### Neue Umfrage")
    st.caption("Erstelle Fragen, wähle die Antwortart und veröffentliche alles mit einem Klick.")
    _render_builder_fields(builder, "create")
    if st.button(
        "✨ Umfrage speichern & veröffentlichen",
        type="primary",
        width="stretch",
        key="create_save",
    ):
        try:
            create_survey(builder["title"], builder["questions"])
        except ValueError as error:
            st.error(str(error))
        else:
            st.session_state.create_builder = {"title": "", "questions": [_default_question()]}
            _clear_builder_widgets("create")
            st.session_state.admin_notice = "Die neue Umfrage ist veröffentlicht und jetzt sichtbar."
            st.rerun()


def _survey_to_builder(survey: dict) -> dict:
    return {
        "title": survey["title"],
        "questions": [
            {
                "text": question["question_text"],
                "type": question["question_type"],
                "options": [option["label"] for option in question["options"]],
            }
            for question in survey["questions"]
        ],
    }


def _render_edit_panel(surveys: list[dict]) -> None:
    editing_id = st.session_state.get("editing_survey_id")
    if editing_id is None:
        return
    survey = next((item for item in surveys if item["id"] == editing_id), None)
    if survey is None:
        st.session_state.pop("editing_survey_id", None)
        st.session_state.pop("edit_builder", None)
        return

    result = survey_results(editing_id)
    with st.container(border=True):
        st.markdown(f"### ✏️ Umfrage bearbeiten: {survey['title']}")
        if result["response_count"]:
            st.warning(
                f"Diese Umfrage hat bereits {result['response_count']} Antworten. Änderungen an "
                "Fragen oder Optionen setzen die bisherige Auswertung zurück. Eine reine Änderung "
                "des Titels behält die Antworten."
            )
        builder = st.session_state.edit_builder
        _render_builder_fields(builder, "edit")
        allow_reset = False
        if result["response_count"]:
            allow_reset = st.checkbox(
                "Ich bestätige, dass Antworten bei strukturellen Änderungen zurückgesetzt werden dürfen.",
                key="edit_allow_reset",
            )

        save_col, cancel_col = st.columns(2)
        if save_col.button("Änderungen speichern", type="primary", width="stretch"):
            try:
                update_survey(editing_id, builder["title"], builder["questions"], allow_reset)
            except ValueError as error:
                st.error(str(error))
            else:
                st.session_state.pop("editing_survey_id", None)
                st.session_state.pop("edit_builder", None)
                _clear_builder_widgets("edit")
                st.session_state.admin_notice = "Die Änderungen wurden gespeichert."
                st.rerun()
        if cancel_col.button("Abbrechen", width="stretch"):
            st.session_state.pop("editing_survey_id", None)
            st.session_state.pop("edit_builder", None)
            _clear_builder_widgets("edit")
            st.rerun()
    st.write("")


def _render_management() -> None:
    surveys = list_surveys()
    st.markdown("### Deine Umfragen")
    st.caption("Bestimme, was öffentlich sichtbar ist, oder bearbeite und lösche bestehende Umfragen.")
    if not surveys:
        st.info("Du hast noch keine Umfrage erstellt.")
        return

    _render_edit_panel(surveys)
    pending_delete = st.session_state.get("pending_delete_id")

    for survey in surveys:
        result = survey_results(survey["id"])
        with st.container(border=True):
            title_col, status_col = st.columns([4, 1], vertical_alignment="center")
            title_col.subheader(survey["title"])
            status_class = "status-live" if survey["active"] else "status-paused"
            status_text = "● Aktiv" if survey["active"] else "○ Pausiert"
            status_col.markdown(
                f'<div style="text-align:right"><span class="{status_class}">{status_text}</span></div>',
                unsafe_allow_html=True,
            )
            st.caption(
                f"{len(survey['questions'])} Fragen  ·  {result['response_count']} Teilnahmen  ·  ID #{survey['id']}"
            )

            active_col, edit_col, delete_col = st.columns([2, 1, 1], vertical_alignment="center")
            new_active = active_col.toggle(
                "In der Benutzeransicht anzeigen",
                value=bool(survey["active"]),
                key=f"manage_active_{survey['id']}",
            )
            if new_active != bool(survey["active"]):
                set_survey_active(survey["id"], new_active)
                st.session_state.admin_notice = (
                    "Die Umfrage wurde aktiviert." if new_active else "Die Umfrage wurde pausiert."
                )
                st.rerun()

            if edit_col.button("✏️ Bearbeiten", key=f"edit_{survey['id']}", width="stretch"):
                st.session_state.editing_survey_id = survey["id"]
                st.session_state.edit_builder = _survey_to_builder(survey)
                _clear_builder_widgets("edit")
                st.rerun()
            if delete_col.button("🗑️ Löschen", key=f"delete_{survey['id']}", width="stretch"):
                st.session_state.pending_delete_id = survey["id"]
                st.rerun()

            if pending_delete == survey["id"]:
                st.error("Diese Umfrage und alle zugehörigen Antworten dauerhaft löschen?")
                confirm_col, cancel_col = st.columns(2)
                if confirm_col.button(
                    "Ja, endgültig löschen",
                    key=f"confirm_delete_{survey['id']}",
                    type="primary",
                    width="stretch",
                ):
                    delete_survey(survey["id"])
                    st.session_state.pop("pending_delete_id", None)
                    if st.session_state.get("editing_survey_id") == survey["id"]:
                        st.session_state.pop("editing_survey_id", None)
                        st.session_state.pop("edit_builder", None)
                    st.session_state.admin_notice = "Die Umfrage wurde gelöscht."
                    st.rerun()
                if cancel_col.button(
                    "Nicht löschen", key=f"cancel_delete_{survey['id']}", width="stretch"
                ):
                    st.session_state.pop("pending_delete_id", None)
                    st.rerun()
        st.write("")


def _result_chart(frame: pd.DataFrame) -> alt.LayerChart:
    base = alt.Chart(frame).encode(
        y=alt.Y("Antwortoption:N", sort="-x", title=None, axis=alt.Axis(labelLimit=220)),
        x=alt.X("Stimmen:Q", title="Stimmen", axis=alt.Axis(tickMinStep=1)),
    )
    bars = base.mark_bar(cornerRadiusEnd=9, size=25).encode(
        color=alt.Color(
            "Antwortoption:N", scale=alt.Scale(range=CHART_COLORS), legend=None
        ),
        tooltip=["Antwortoption:N", "Stimmen:Q", "Anteil:N"],
    )
    labels = base.mark_text(align="left", baseline="middle", dx=7, fontWeight=700).encode(
        text="Stimmen:Q", color=alt.value("#423c50")
    )
    return (bars + labels).properties(height=max(130, len(frame) * 46))


def _render_results() -> None:
    surveys = list_surveys()
    if not surveys:
        st.info("Es wurden noch keine Umfragen erstellt.")
        return
    labels = {f"{survey['title']} (#{survey['id']})": survey["id"] for survey in surveys}
    selected_label = st.selectbox("Umfrage auswählen", list(labels))
    result = survey_results(labels[selected_label])

    st.markdown(
        f"""
        <div class="results-banner">
            <h2>📈 {result['title']}</h2>
            <p>Ergebnisse auf einen Blick – klar, farbig und live aus allen Antworten.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    metric_one, metric_two, metric_three = st.columns(3)
    metric_one.metric("👥 Teilnahmen", result["response_count"])
    metric_two.metric("❓ Fragen", len(result["questions"]))
    metric_three.metric("📡 Status", "Aktiv" if result["active"] else "Pausiert")
    st.write("")

    for number, question in enumerate(result["questions"], start=1):
        with st.container(border=True):
            st.markdown(
                f'<h3><span class="question-number">{number}</span>{question["question_text"]}</h3>',
                unsafe_allow_html=True,
            )
            frame = pd.DataFrame(question["results"])[["label", "votes"]]
            frame.columns = ["Antwortoption", "Stimmen"]
            participant_count = int(result["response_count"])
            frame["Anteil"] = (
                (frame["Stimmen"] / participant_count * 100).round(1).astype(str) + "%"
                if participant_count
                else "0.0%"
            )
            chart_col, table_col = st.columns([1.45, 1])
            with chart_col:
                st.altair_chart(_result_chart(frame), width="stretch")
            with table_col:
                st.dataframe(frame, hide_index=True, width="stretch")
            if question["question_type"] == "multiple":
                st.caption(
                    "Mehrfachauswahl: Die Prozentwerte können zusammen über 100 % liegen."
                )
        st.write("")


def render_admin_view() -> None:
    if not st.session_state.admin_authenticated:
        _render_login()
        return

    heading_col, logout_col = st.columns([5, 1])
    with heading_col:
        st.markdown(
            """<div class="admin-banner"><h2>Admin-Zentrale</h2>
            <p>Erstellen, verwalten und verstehen – alles an einem Ort.</p></div>""",
            unsafe_allow_html=True,
        )
    if logout_col.button("Abmelden", width="stretch"):
        st.session_state.admin_authenticated = False
        st.session_state.view = "user"
        st.rerun()

    if notice := st.session_state.pop("admin_notice", None):
        st.success(notice)

    manage_tab, create_tab, results_tab = st.tabs(
        ["🗂️ Umfragen verwalten", "✍️ Neue Umfrage", "📊 Auswertungen"]
    )
    with manage_tab:
        _render_management()
    with create_tab:
        _render_create()
    with results_tab:
        _render_results()
