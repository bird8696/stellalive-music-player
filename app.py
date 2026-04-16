import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import streamlit as st
from app_config.settings import PAGE_CONFIG, THEME, FONTS, GOOGLE_FONTS_URL
from app_utils.auth_utils import is_logged_in, get_current_user, logout_session
from app_utils.youtube import is_valid_youtube_url, extract_video_id, get_thumbnail_url
from app_utils.data_manager import (
    get_playlist_names, get_playlist, create_playlist,
    delete_playlist, add_track, remove_track, playlist_exists,
)
from app_components.auth import render_auth_page
from app_components.player import render_player
from app_components.poster_wall import render_poster_wall

st.set_page_config(**PAGE_CONFIG)

BG    = THEME['bg_primary']
GOLD  = THEME['gold_primary']
MUTED = THEME['text_muted']
DISP  = FONTS['display']
MONO  = FONTS['mono']


def _inject_styles() -> None:
    # 사이드바 관련 CSS 완전 제거 — config.toml이 처리
    st.markdown(f"""
    <link href="{GOOGLE_FONTS_URL}" rel="stylesheet">
    <style>
        .stApp {{
            background-color: {BG};
            background-image:
                radial-gradient(ellipse at 20% 20%, #1a1040 0%, transparent 50%),
                radial-gradient(ellipse at 80% 80%, #0a0d2a 0%, transparent 50%);
        }}
        .stApp::before {{
            content: '';
            position: fixed;
            inset: 0;
            background-image:
                radial-gradient(1px 1px at 15% 25%, #a78bfa66 0%, transparent 100%),
                radial-gradient(1px 1px at 40% 10%, #c4b5fdaa 0%, transparent 100%),
                radial-gradient(1.5px 1.5px at 65% 35%, #a78bfa88 0%, transparent 100%),
                radial-gradient(1px 1px at 80% 15%, #e8e4f855 0%, transparent 100%),
                radial-gradient(1px 1px at 55% 85%, #a78bfa55 0%, transparent 100%),
                radial-gradient(1px 1px at 10% 90%, #e8e4f833 0%, transparent 100%);
            pointer-events: none;
            z-index: 0;
        }}
        .block-container {{
            padding-top: 2rem !important;
            padding-bottom: 2rem !important;
            max-width: 1100px;
            position: relative;
            z-index: 1;
        }}
        .page-header {{ display:flex; align-items:baseline; gap:16px; margin-bottom:6px; }}
        .page-title {{
            font-family: {DISP};
            font-size: 30px;
            letter-spacing: 0.18em;
            color: {GOLD};
            text-shadow: 0 0 20px {GOLD}55;
        }}
        .page-playlist-name {{
            font-family: {MONO};
            font-size: 11px;
            letter-spacing: 0.2em;
            color: {MUTED};
        }}
        .gold-divider {{
            height: 1px;
            background: linear-gradient(to right, transparent, {GOLD}, transparent);
            opacity: 0.4;
            margin: 1rem 0 1.4rem;
        }}
        #MainMenu, footer {{ visibility: hidden; }}
        header[data-testid="stHeader"] {{
            background: transparent !important;
            backdrop-filter: none !important;
        }}
        [data-testid="stDecoration"] {{ display: none !important; }}
        /* 상단 툴바 숨김 (사이드바 토글은 유지) */

        .stDeployButton {{ display: none; }}
        ::-webkit-scrollbar {{ width: 5px; }}
        ::-webkit-scrollbar-track {{ background: {BG}; }}
        ::-webkit-scrollbar-thumb {{ background: #2a2448; border-radius: 3px; }}
        ::-webkit-scrollbar-thumb:hover {{ background: {GOLD}; }}
    </style>
    """, unsafe_allow_html=True)


def _render_sidebar(username: str):
    with st.sidebar:
        st.markdown(f"## ✦ STELLA")
        st.caption(f"👤 {username}")
        st.divider()

        # 플레이리스트 선택
        st.markdown("**PLAYLIST**")
        names = get_playlist_names(username)
        selected_pl = None

        if names:
            if "selected_playlist" not in st.session_state or \
               st.session_state.selected_playlist not in names:
                st.session_state.selected_playlist = names[0]
            selected_pl = st.selectbox("플레이리스트", names,
                index=names.index(st.session_state.selected_playlist),
                key="playlist_selector", label_visibility="collapsed")
            st.session_state.selected_playlist = selected_pl
            st.caption(f"트랙 {len(get_playlist(username, selected_pl))}개")
        else:
            st.caption("플레이리스트가 없습니다.")

        st.divider()

        # 플레이리스트 관리
        with st.expander("📁 플레이리스트 관리"):
            new_name = st.text_input("새 이름", placeholder="My Playlist", key="new_pl_name")
            if st.button("만들기", key="btn_create_pl"):
                n = new_name.strip()
                if not n:
                    st.error("이름을 입력해주세요.")
                elif playlist_exists(username, n):
                    st.error("이미 존재합니다.")
                else:
                    create_playlist(username, n)
                    st.session_state.selected_playlist = n
                    st.success(f"'{n}' 생성!")
                    st.rerun()
            if names:
                st.divider()
                del_target = st.selectbox("삭제", names, key="del_pl_target")
                if st.button("삭제", key="btn_del_pl"):
                    delete_playlist(username, del_target)
                    st.session_state.pop("selected_playlist", None)
                    st.rerun()

        st.divider()

        # 트랙 추가
        st.markdown("**✦ TRACK 추가**")
        if selected_pl:
            with st.form("add_track_form", clear_on_submit=True):
                title = st.text_input("제목 *", placeholder="곡 제목")
                desc  = st.text_input("아티스트", placeholder="Artist")
                url   = st.text_input("YouTube URL *", placeholder="https://youtu.be/...")
                img   = st.text_input("포스터 이미지 URL", placeholder="비워두면 YT 썸네일 자동")
                ok    = st.form_submit_button("추가하기", type="primary")
            if ok:
                title = title.strip(); url = url.strip()
                if not title:
                    st.error("제목을 입력해주세요.")
                elif not is_valid_youtube_url(url):
                    st.error("유효한 YouTube URL을 입력해주세요.")
                else:
                    if not img.strip():
                        vid = extract_video_id(url)
                        img = get_thumbnail_url(vid, quality="hq") if vid else ""
                    add_track(username, selected_pl, {
                        "title": title, "desc": desc.strip(), "url": url, "img": img
                    })
                    st.success(f"'{title}' 추가! ✦")
                    st.rerun()
        else:
            st.caption("먼저 플레이리스트를 만들어주세요.")

        # 트랙 삭제
        if selected_pl:
            tracks_now = get_playlist(username, selected_pl)
            if tracks_now:
                with st.expander("🗑 트랙 삭제"):
                    opts = [f"{i+1}. {t['title']}" for i, t in enumerate(tracks_now)]
                    sel  = st.selectbox("삭제", opts, key="del_trk", label_visibility="collapsed")
                    if st.button("삭제", key="btn_del_trk"):
                        idx = opts.index(sel)
                        remove_track(username, selected_pl, idx)
                        if st.session_state.get("current_track_idx") == idx:
                            st.session_state.pop("current_track", None)
                            st.session_state.pop("current_track_idx", None)
                        st.rerun()

        st.divider()
        if st.button("로그아웃"):
            logout_session()
            st.rerun()

    tracks = get_playlist(username, selected_pl) if selected_pl else []
    return selected_pl, tracks


def _handle_track_selection(tracks):
    raw = st.query_params.get("selected_track")
    if raw is None:
        return
    try:
        idx = int(raw)
        if 0 <= idx < len(tracks):
            st.session_state["current_track"]     = tracks[idx]
            st.session_state["current_track_idx"] = idx
    except (ValueError, TypeError):
        pass
    st.query_params.clear()


def main():
    _inject_styles()

    if not is_logged_in():
        render_auth_page()
        return

    username = get_current_user()
    playlist_name, tracks = _render_sidebar(username)
    _handle_track_selection(tracks)

    current_track     = st.session_state.get("current_track")
    current_track_idx = st.session_state.get("current_track_idx")

    pl_label = f"✦ {playlist_name}" if playlist_name else "NO PLAYLIST"
    st.markdown(
        f'<div class="page-header">'
        f'<span class="page-title">✦ STELLA MUSIC</span>'
        f'<span class="page-playlist-name">{pl_label}</span>'
        f'</div>'
        f'<div class="gold-divider"></div>',
        unsafe_allow_html=True,
    )

    if current_track:
        col_player, col_wall = st.columns([5, 7], gap="large")
        with col_player:
            render_player(current_track, track_idx=current_track_idx or 0, total_tracks=len(tracks))
        with col_wall:
            render_poster_wall(tracks, playing_idx=current_track_idx)
    else:
        render_player(None, track_idx=0, total_tracks=len(tracks))
        st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
        render_poster_wall(tracks, playing_idx=None)


main()