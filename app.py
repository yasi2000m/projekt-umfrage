import streamlit as st

from admin_view import render_admin_view
from database import init_database
from user_view import render_user_view


st.set_page_config(
    page_title="Online-Umfragen",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="collapsed",
)


def _global_styles() -> None:
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800&display=swap');
        :root { --ink:#172033; --purple:#6750e8; --violet:#8b5cf6; --coral:#ff7a6e; --teal:#24b8a6; }
        html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
        .stApp { background: linear-gradient(180deg, #fbfaff 0%, #f7f8fc 55%, #ffffff 100%); }
        .block-container { max-width: 1120px; padding-top: 1.35rem; padding-bottom: 4rem; }
        h1, h2, h3 { color: var(--ink); letter-spacing: -0.025em; }
        [data-testid="stHeader"] { background: transparent; }
        [data-testid="stForm"], [data-testid="stVerticalBlockBorderWrapper"] {
            background: rgba(255,255,255,.94); border: 1px solid #e9e6f5 !important;
            border-radius: 20px !important; box-shadow: 0 10px 35px rgba(66,52,120,.07);
        }
        .stButton > button, .stFormSubmitButton > button {
            border-radius: 12px; font-weight: 700; border-color: #ddd7f5;
            transition: transform .16s ease, box-shadow .16s ease;
        }
        .stButton > button:hover, .stFormSubmitButton > button:hover {
            transform: translateY(-1px); box-shadow: 0 7px 18px rgba(103,80,232,.16);
        }
        button[kind="primary"], [data-testid="stBaseButton-primaryFormSubmit"] {
            background: linear-gradient(135deg, var(--purple), var(--violet)); border: none;
        }
        div[data-baseweb="radio"] > div { gap: .45rem; }
        div[data-baseweb="radio"] label {
            padding: .6rem .8rem; border-radius: 11px; background: #f8f7fd;
            border: 1px solid #ebe8f7;
        }
        [data-testid="stCheckbox"] {
            padding: .48rem .75rem; margin:.3rem 0; border-radius:11px;
            background:#f8f7fd; border:1px solid #ebe8f7;
        }
        .hero-panel { min-height:330px; border-radius:28px; padding:.65rem 2.7rem; display:flex; align-items:flex-start;
            background-size:cover; background-position:center; box-shadow:0 18px 55px rgba(82,60,151,.13); overflow:hidden; }
        .hero-copy { max-width:42%; }
        .hero-kicker { display:inline-block; color:#6554d9; background:#eeeafe; border-radius:999px;
            padding:.38rem .75rem; font-size:.8rem; font-weight:800; text-transform:uppercase; letter-spacing:.07em; }
        .hero-copy h1 { font-size:2.45rem; line-height:1.06; margin:.4rem 0 .65rem; }
        .hero-subtext { margin:1.05rem auto 0; text-align:center; max-width:760px; color:#5e5870;
            font-size:1.02rem; line-height:1.65; }
        .section-title { margin:2rem 0 1rem; }
        .section-title span { color:#6d5ae7; font-size:.82rem; font-weight:800; letter-spacing:.08em; text-transform:uppercase; }
        .section-title h2 { margin:.25rem 0; }
        .survey-meta { color:#756f85; font-size:.9rem; margin-top:-.4rem; }
        .question-number { display:inline-grid; place-items:center; width:28px; height:28px; margin-right:.4rem;
            border-radius:9px; color:white; font-size:.82rem; background:linear-gradient(135deg,#6750e8,#9d64ee); }
        .admin-banner, .results-banner { border-radius:22px; padding:1.5rem 1.7rem; margin:.5rem 0 1.4rem;
            color:white; background:linear-gradient(120deg,#4536a8,#7158e8 60%,#9c62ee); box-shadow:0 12px 32px #6750e82b; }
        .admin-banner h2, .results-banner h2 { color:white; margin:0 0 .25rem; }
        .admin-banner p, .results-banner p { margin:0; opacity:.84; }
        .status-live, .status-paused { display:inline-block; border-radius:999px; padding:.28rem .65rem;
            font-size:.78rem; font-weight:800; }
        .status-live { color:#087f70; background:#dff9f3; }
        .status-paused { color:#897049; background:#fff3d8; }
        [data-testid="stMetric"] { background:white; border:1px solid #eae6f7; border-radius:17px;
            padding:1rem 1.15rem; box-shadow:0 7px 24px rgba(66,52,120,.06); }
        [data-testid="stTabs"] button { font-weight:700; }
        @media (max-width: 760px) {
            .hero-panel { min-height:360px; padding:.6rem 1.6rem; background-position:62% center; align-items:flex-start; }
            .hero-copy { max-width:88%; }
            .hero-copy h1 { font-size:2rem; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def main() -> None:
    init_database()
    _global_styles()
    st.session_state.setdefault("view", "user")
    st.session_state.setdefault("admin_authenticated", False)

    brand_col, nav_col = st.columns([5, 1.25], vertical_alignment="center")
    with nav_col:
        if st.session_state.view == "user":
            if st.button("🔐 Admin", width="stretch"):
                st.session_state.view = "admin"
                st.rerun()
        elif st.button("← Zur Umfrage", width="stretch"):
            st.session_state.view = "user"
            st.rerun()

    st.write("")
    if st.session_state.view == "admin":
        render_admin_view()
    else:
        render_user_view()


if __name__ == "__main__":
    main()
