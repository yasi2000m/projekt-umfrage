import base64
from functools import lru_cache
from pathlib import Path

import streamlit as st

from database import list_surveys, submit_survey


HERO_PATH = Path(__file__).resolve().parent / "assets" / "survey-hero.png"


@lru_cache(maxsize=1)
def _hero_data_uri() -> str:
    encoded = base64.b64encode(HERO_PATH.read_bytes()).decode("ascii")
    return f"data:image/png;base64,{encoded}"


def _render_hero() -> None:
    st.markdown(
        f"""
        <section class="hero-panel" style="background-image:linear-gradient(rgba(255,255,255,.42), rgba(255,255,255,.42)),url('{_hero_data_uri()}')">
            <div class="hero-copy">
                <span class="hero-kicker">Deine Stimme zählt</span>
                <h1>Teile deine Meinung.</h1>
            </div>
        </section>
        <p class="hero-subtext">Ein paar Klicks genügen. Deine Antworten helfen dabei, ein ehrliches Bild zu bekommen.</p>
        """,
        unsafe_allow_html=True,
    )


def render_user_view() -> None:
    _render_hero()
    surveys = list_surveys(active_only=True)
    submitted_surveys = st.session_state.setdefault("submitted_surveys", set())

    st.markdown(
        """
        <div class="section-title">
            <span>Aktuelle Umfragen</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if not surveys:
        st.info("🌿 Momentan ist keine Umfrage aktiv. Schau gerne später wieder vorbei.")
        return

    for survey in surveys:
        if survey["id"] in submitted_surveys:
            with st.container(border=True):
                st.subheader(f"✅ {survey['title']}")
                st.success("Vielen Dank – deine Antworten wurden gespeichert.")
            st.write("")
            continue

        with st.container(border=True):
            st.header(survey["title"])
            st.markdown(
                f'<p class="survey-meta">{len(survey["questions"])} Fragen · anonym · dauert nur wenige Minuten</p>',
                unsafe_allow_html=True,
            )
            with st.form(f"survey_form_{survey['id']}", clear_on_submit=True):
                answers: dict[int, list[int]] = {}
                for number, question in enumerate(survey["questions"], start=1):
                    st.markdown(
                        f'<h4><span class="question-number">{number}</span>{question["question_text"]}</h4>',
                        unsafe_allow_html=True,
                    )
                    option_lookup = {
                        option["label"]: option["id"] for option in question["options"]
                    }
                    labels = list(option_lookup)
                    if question["question_type"] == "single":
                        st.caption("Eine Antwort auswählen")
                        selected = st.radio(
                            "Eine Antwort auswählen",
                            labels,
                            index=None,
                            key=f"single_{survey['id']}_{question['id']}",
                            label_visibility="collapsed",
                        )
                        answers[question["id"]] = (
                            [option_lookup[selected]] if selected is not None else []
                        )
                    else:
                        st.caption("Mehrere Antworten möglich")
                        selected_ids = []
                        for option in question["options"]:
                            if st.checkbox(
                                option["label"],
                                key=(
                                    f"multiple_{survey['id']}_{question['id']}_"
                                    f"{option['id']}"
                                ),
                            ):
                                selected_ids.append(option["id"])
                        answers[question["id"]] = selected_ids
                    st.write("")

                submitted = st.form_submit_button(
                    "Antworten absenden  →", type="primary", width="stretch"
                )

            if submitted:
                try:
                    submit_survey(survey["id"], answers)
                except ValueError as error:
                    st.error(str(error))
                else:
                    submitted_surveys.add(survey["id"])
                    st.toast("Antworten erfolgreich gespeichert!", icon="🎉")
                    st.rerun()
        st.write("")
