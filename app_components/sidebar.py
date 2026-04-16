# ─────────────────────────────────────────
#  components/sidebar.py
#  사이드바 — 플레이리스트 선택 · 트랙 추가 · 삭제
# ─────────────────────────────────────────

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
from app_config.settings import THEME, FONTS, GOOGLE_FONTS_URL
from app_utils.auth_utils import get_current_user
from app_utils.youtube import is_valid_youtube_url, extract_video_id, get_thumbnail_url
from app_utils.data_manager import (
    get_playlist_names, get_playlist, create_playlist, delete_playlist,
    rename_playlist, add_track, remove_track, playlist_exists,
)
from app_components.auth import render_logout_button

GOLD = THEME['gold_primary']
GOLDL= THEME['gold_light']
BG   = THEME['bg_primary']
BGS  = THEME['bg_secondary']
BGT  = THEME['bg_tertiary']
TP   = THEME['text_primary']
TS   = THEME['text_secondary']
TM   = THEME['text_muted']
BRD  = THEME['border']
BRDG = THEME['border_gold']

def _inject_sidebar_styles():
    st.markdown(f"""
    <link href="{GOOGLE_FONTS_URL}" rel="stylesheet">
    <style>
    [data-testid="stSidebar"] {{ background:{BGS} !important; border-right:1px solid {BRDG}; }}
    [data-testid="stSidebar"] * {{ color:{TP} !important; }}
    [data-testid="stSidebar"] .sidebar-logo {{
        font-family:{FONTS['display']}; font-size:22px; letter-spacing:0.2em;
        color:{GOLD} !important; text-align:center; padding:0.5rem 0 0.2rem;
        text-shadow:0 0 16px {GOLD}66;
    }}
    [data-testid="stSidebar"] .sidebar-user {{
        font-family:{FONTS['mono']}; font-size:11px; letter-spacing:0.15em;
        color:{TM} !important; text-align:center; margin-bottom:1rem;
    }}
    [data-testid="stSidebar"] .section-label {{
        font-family:{FONTS['mono']}; font-size:10px; letter-spacing:0.2em;
        color:{TM} !important; margin-bottom:6px;
    }}
    [data-testid="stSidebar"] input,
    [data-testid="stSidebar"] textarea {{
        background:{BGT} !important; border:1px solid {BRD} !important;
        color:{TP} !important; border-radius:8px !important;
        font-family:{FONTS['mono']} !important; font-size:12px !important;
    }}
    [data-testid="stSidebar"] input:focus {{ border-color:{GOLD} !important; box-shadow:0 0 0 2px {GOLD}33 !important; }}
    [data-testid="stSidebar"] .stSelectbox > div > div {{
        background:{BGT} !important; border:1px solid {BRD} !important;
        color:{TP} !important; border-radius:8px !important;
    }}
    [data-testid="stSidebar"] .stButton > button {{
        width:100%; background:none !important; border:1px solid {BRDG} !important;
        color:{TP} !important; font-family:{FONTS['mono']} !important;
        font-size:12px !important; border-radius:8px !important;
        letter-spacing:0.05em; transition:all 0.2s;
    }}
    [data-testid="stSidebar"] .stButton > button:hover {{
        background:{GOLD}22 !important; border-color:{GOLD} !important;
        box-shadow:0 0 10px {GOLD}33;
    }}
    [data-testid="stSidebar"] .stButton > button[kind="primary"] {{
        background:linear-gradient(135deg,{GOLD}cc,{GOLDL}cc) !important;
        border-color:{GOLD} !important; color:{BG} !important; font-weight:700;
        box-shadow:0 0 12px {GOLD}44;
    }}
    [data-testid="stSidebar"] hr {{ border-color:{BRD} !important; margin:0.8rem 0 !important; }}
    [data-testid="stSidebar"] .stella-divider {{
        height:1px; background:linear-gradient(to right,transparent,{GOLD},transparent);
        opacity:0.25; margin:0.8rem 0;
    }}
    </style>
    """, unsafe_allow_html=True)

def _section_playlist_select(username):
    names = get_playlist_names(username)
    st.markdown('<div class="section-label">✦ PLAYLIST</div>', unsafe_allow_html=True)
    if not names:
        st.caption("플레이리스트가 없습니다.")
        return None
    if "selected_playlist" not in st.session_state or st.session_state.selected_playlist not in names:
        st.session_state.selected_playlist = names[0]
    selected = st.selectbox("플레이리스트", options=names, index=names.index(st.session_state.selected_playlist), key="playlist_selector", label_visibility="collapsed")
    st.session_state.selected_playlist = selected
    st.caption(f"트랙 {len(get_playlist(username, selected))}개")
    return selected

def _section_playlist_manage(username):
    with st.expander("플레이리스트 관리", expanded=False):
        new_name = st.text_input("새 플레이리스트 이름", placeholder="My Playlist", key="new_pl_name")
        if st.button("만들기", key="btn_create_pl"):
            name = new_name.strip()
            if not name:
                st.error("이름을 입력해주세요.")
            elif playlist_exists(username, name):
                st.error("이미 존재합니다.")
            else:
                create_playlist(username, name)
                st.session_state.selected_playlist = name
                st.success(f"'{name}' 생성 완료!")
                st.rerun()
        st.divider()
        names = get_playlist_names(username)
        if names:
            target = st.selectbox("이름 변경", names, key="rename_target")
            new_n  = st.text_input("새 이름", key="rename_new")
            if st.button("이름 변경", key="btn_rename"):
                if not new_n.strip():
                    st.error("새 이름을 입력해주세요.")
                elif rename_playlist(username, target, new_n.strip()):
                    st.session_state.selected_playlist = new_n.strip()
                    st.success("변경 완료!")
                    st.rerun()
                else:
                    st.error("이미 존재하는 이름입니다.")
            st.divider()
            del_target = st.selectbox("삭제", names, key="del_target")
            if st.button("삭제", key="btn_del_pl"):
                delete_playlist(username, del_target)
                st.session_state.pop("selected_playlist", None)
                st.success("삭제 완료!")
                st.rerun()

def _section_add_track(username, playlist_name):
    st.markdown('<div class="section-label">✦ TRACK 추가</div>', unsafe_allow_html=True)
    if playlist_name is None:
        st.caption("먼저 플레이리스트를 만들어주세요.")
        return
    with st.form("add_track_form", clear_on_submit=True):
        title = st.text_input("제목 *", placeholder="곡 제목")
        desc  = st.text_input("아티스트 / 설명", placeholder="Artist name")
        url   = st.text_input("YouTube URL *", placeholder="https://youtu.be/...")
        img   = st.text_input("포스터 이미지 URL", placeholder="비워두면 YT 썸네일 자동")
        submitted = st.form_submit_button("추가하기", type="primary")
    if submitted:
        title = title.strip(); url = url.strip(); img = img.strip()
        if not title:
            st.error("제목을 입력해주세요.")
            return
        if not url or not is_valid_youtube_url(url):
            st.error("유효한 YouTube URL을 입력해주세요.")
            return
        if not img:
            vid = extract_video_id(url)
            img = get_thumbnail_url(vid, quality="hq") if vid else ""
        add_track(username, playlist_name, {"title": title, "desc": desc.strip(), "url": url, "img": img})
        st.success(f"'{title}' 추가 완료! ✦")
        st.rerun()

def _section_remove_track(username, playlist_name):
    if playlist_name is None:
        return
    tracks = get_playlist(username, playlist_name)
    if not tracks:
        return
    with st.expander("트랙 삭제", expanded=False):
        options  = [f"{i+1}. {t['title']}" for i, t in enumerate(tracks)]
        selected = st.selectbox("삭제할 트랙", options, key="del_track_sel", label_visibility="collapsed")
        if st.button("삭제", key="btn_del_track"):
            idx = options.index(selected)
            remove_track(username, playlist_name, idx)
            if st.session_state.get("current_track_idx") == idx:
                st.session_state.pop("current_track", None)
                st.session_state.pop("current_track_idx", None)
            st.success("삭제 완료!")
            st.rerun()

def render_sidebar():
    username = get_current_user()
    with st.sidebar:
        _inject_sidebar_styles()
        st.markdown('<div class="sidebar-logo">✦ STELLA</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="sidebar-user">👤 {username}</div>', unsafe_allow_html=True)
        st.markdown('<div class="stella-divider"></div>', unsafe_allow_html=True)
        selected_pl = _section_playlist_select(username)
        st.divider()
        _section_playlist_manage(username)
        st.divider()
        _section_add_track(username, selected_pl)
        st.divider()
        _section_remove_track(username, selected_pl)
        render_logout_button()
    tracks = get_playlist(username, selected_pl) if selected_pl else []
    return selected_pl, tracks