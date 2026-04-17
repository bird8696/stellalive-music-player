import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
from app_utils.auth_utils import sign_in, sign_up, logout_session, AuthError
from app_config.settings import THEME, FONTS, GOOGLE_FONTS_URL

GOLD  = THEME['gold_primary']
GOLDL = THEME['gold_light']
BG    = THEME['bg_primary']
BGS   = THEME['bg_secondary']
BGT   = THEME['bg_tertiary']
TP    = THEME['text_primary']
TS    = THEME['text_secondary']
TM    = THEME['text_muted']
BRD   = THEME['border']
BRDG  = THEME['border_gold']

def _inject_auth_styles() -> None:
    st.markdown(f"""
    <link href="{GOOGLE_FONTS_URL}" rel="stylesheet">
    <style>
        .stApp {{
            background-color: {BG};
            background-image:
                radial-gradient(ellipse at 20% 20%, #1a1040 0%, transparent 50%),
                radial-gradient(ellipse at 80% 80%, #0a0d2a 0%, transparent 50%);
        }}
        .auth-wrap {{
            max-width: 420px;
            margin: 6vh auto 0;
            padding: 2.5rem 2rem;
            background: {BGS};
            border: 1px solid {BRDG};
            border-radius: 16px;
            box-shadow: 0 0 40px {GOLD}18;
        }}
        .auth-logo {{
            font-family: {FONTS['display']};
            font-size: 32px;
            letter-spacing: 0.2em;
            color: {GOLD};
            text-align: center;
            margin-bottom: 4px;
            text-shadow: 0 0 20px {GOLD}66;
        }}
        .auth-sub {{
            font-family: {FONTS['mono']};
            font-size: 10px;
            letter-spacing: 0.25em;
            color: {TM};
            text-align: center;
            margin-bottom: 2rem;
        }}
        .stTabs [data-baseweb="tab-list"] {{
            background: {BG};
            border-radius: 8px;
            padding: 4px;
            gap: 4px;
            border: 1px solid {BRDG};
        }}
        .stTabs [data-baseweb="tab"] {{
            font-family: {FONTS['mono']};
            font-size: 12px;
            color: {TS};
            border-radius: 6px;
            padding: 6px 20px;
        }}
        .stTabs [aria-selected="true"] {{
            background: {GOLD} !important;
            color: {BG} !important;
            font-weight: 700;
        }}
        .stTabs [data-baseweb="tab-highlight"] {{ display: none; }}
        .stTextInput input {{
            background: {BGT} !important;
            border: 1px solid {BRD} !important;
            border-radius: 8px !important;
            color: {TP} !important;
            font-family: {FONTS['mono']};
            font-size: 13px !important;
        }}
        .stTextInput input:focus {{
            border-color: {GOLD} !important;
            box-shadow: 0 0 0 2px {GOLD}33 !important;
        }}
        .stTextInput label {{
            color: {TS} !important;
            font-family: {FONTS['mono']};
            font-size: 11px !important;
        }}
        .stButton > button {{
            width: 100%;
            background: linear-gradient(135deg, {GOLD}cc, {GOLDL}cc) !important;
            color: {BG} !important;
            font-family: {FONTS['display']};
            font-size: 15px !important;
            letter-spacing: 0.15em;
            border: none !important;
            border-radius: 8px !important;
            padding: 0.6rem 0 !important;
            margin-top: 0.5rem;
            box-shadow: 0 0 16px {GOLD}44;
        }}
        .stButton > button:hover {{
            background: linear-gradient(135deg, {GOLDL}, {GOLD}) !important;
            box-shadow: 0 0 24px {GOLD}66 !important;
        }}
        .stAlert {{ border-radius: 8px !important; font-family: {FONTS['mono']}; font-size: 12px !important; }}
        .stella-divider {{
            height: 1px;
            background: linear-gradient(to right, transparent, {GOLD}, transparent);
            opacity: 0.3;
            margin: 1.5rem 0;
        }}
    </style>
    """, unsafe_allow_html=True)


def _render_login_form():
    with st.form("login_form", clear_on_submit=False):
        username = st.text_input("아이디", placeholder="username")
        password = st.text_input("비밀번호", type="password", placeholder="••••••")
        submitted = st.form_submit_button("LOGIN")
    if submitted:
        try:
            sign_in(username, password)
            st.success("로그인 성공!")
            st.rerun()
        except AuthError as e:
            st.error(str(e))


def _render_signup_form():
    with st.form("signup_form", clear_on_submit=False):
        username         = st.text_input("아이디", placeholder="영문자 + 숫자, 3자 이상")
        password         = st.text_input("비밀번호", type="password", placeholder="6~12자, 특수문자 포함")
        password_confirm = st.text_input("비밀번호 확인", type="password", placeholder="••••••")
        submitted        = st.form_submit_button("JOIN")
    if submitted:
        try:
            sign_up(username, password, password_confirm)
            st.success("가입 완료! 환영합니다 ✦")
            st.rerun()
        except AuthError as e:
            st.error(str(e))


def render_auth_page():
    _inject_auth_styles()
    st.markdown('<div class="auth-wrap">', unsafe_allow_html=True)
    st.markdown('<div class="auth-logo">✦ STELLALIVELIVE MUSIC</div>', unsafe_allow_html=True)
    st.markdown('<div class="auth-sub">YOUR PERSONAL STELLALIVE THEATER</div>', unsafe_allow_html=True)
    st.markdown('<div class="stella-divider"></div>', unsafe_allow_html=True)
    tab_login, tab_signup = st.tabs(["로그인", "회원가입"])
    with tab_login:
        _render_login_form()
    with tab_signup:
        _render_signup_form()
    st.markdown('</div>', unsafe_allow_html=True)


def render_logout_button():
    st.markdown('<div class="stella-divider"></div>', unsafe_allow_html=True)
    if st.button("로그아웃", key="logout_btn"):
        logout_session()
        st.rerun()