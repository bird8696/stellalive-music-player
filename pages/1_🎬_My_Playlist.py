import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
from app_config.settings import PAGE_CONFIG, THEME, FONTS, GOOGLE_FONTS_URL
from app_utils.data_manager import get_playlist
from app_components.player import render_player
from app_components.poster_wall import render_poster_wall
from app_components.sidebar import render_sidebar

st.set_page_config(**PAGE_CONFIG)

BG    = THEME['bg_primary']
GOLD  = THEME['gold_primary']
MUTED = THEME['text_muted']
TP    = THEME['text_primary']
BRD   = THEME['border']
DISP  = FONTS['display']
MONO  = FONTS['mono']


def _inject_styles():
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
                radial-gradient(1px 1px at 55% 85%, #a78bfa55 0%, transparent 100%);
            pointer-events: none;
            z-index: 0;
        }}
        .block-container {{
            padding-top: 2rem !important;
            max-width: 1100px;
            position: relative;
            z-index: 1;
        }}
        #MainMenu, footer {{ visibility: hidden; }}
        header[data-testid="stHeader"] {{
            background: transparent !important;
            backdrop-filter: none !important;
        }}
        [data-testid="stDecoration"] {{ display: none !important; }}


        .page-title {{
            font-family: {DISP};
            font-size: 28px;
            letter-spacing: 0.18em;
            color: {GOLD};
            text-shadow: 0 0 20px {GOLD}55;
            margin-bottom: 4px;
        }}
        .gold-divider {{
            height: 1px;
            background: linear-gradient(to right, transparent, {GOLD}, transparent);
            opacity: 0.35;
            margin: 0.8rem 0 1.4rem;
        }}
        .track-count {{
            font-family: {MONO};
            font-size: 11px;
            letter-spacing: 0.2em;
            color: {MUTED};
        }}
        .tracklist-label {{
            font-family: {MONO};
            font-size: 10px;
            letter-spacing: 0.25em;
            color: {MUTED};
            margin-bottom: 10px;
        }}
        .track-row {{
            display: flex;
            align-items: center;
            gap: 14px;
            padding: 9px 0;
            border-bottom: 1px solid {BRD};
            font-family: {MONO};
            font-size: 12px;
            cursor: default;
        }}
        .track-row:hover {{ background: #a78bfa08; }}
        ::-webkit-scrollbar {{ width: 5px; }}
        ::-webkit-scrollbar-track {{ background: {BG}; }}
        ::-webkit-scrollbar-thumb {{ background: #2a2448; border-radius: 3px; }}
        ::-webkit-scrollbar-thumb:hover {{ background: {GOLD}; }}
    </style>
    """, unsafe_allow_html=True)


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

    # 로그인 체크
    if "current_user" not in st.session_state:
        st.markdown(
            f'<div style="text-align:center;padding:4rem;font-family:{MONO};font-size:13px;color:{MUTED}">'
            f'<div style="font-size:32px;margin-bottom:1rem">✦</div>'
            f'로그인이 필요합니다<br>'
            f'<a href="/" style="color:{GOLD};text-decoration:none;letter-spacing:0.1em">→ 메인으로 이동</a>'
            f'</div>',
            unsafe_allow_html=True,
        )
        st.stop()

    playlist_name, tracks = render_sidebar()
    _handle_track_selection(tracks)

    current_track     = st.session_state.get("current_track")
    current_track_idx = st.session_state.get("current_track_idx")

    pl_label = playlist_name or "플레이리스트 없음"
    st.markdown(
        f'<div class="page-title">✦ {pl_label}</div>'
        f'<div class="track-count">TOTAL {len(tracks)} TRACKS</div>'
        f'<div class="gold-divider"></div>',
        unsafe_allow_html=True,
    )

    if not tracks:
        st.info("사이드바에서 트랙을 추가해보세요.", icon="✦")
        return

    if current_track:
        col_p, col_w = st.columns([5, 7], gap="large")
        with col_p:
            render_player(current_track, track_idx=current_track_idx or 0, total_tracks=len(tracks))
        with col_w:
            render_poster_wall(tracks, playing_idx=current_track_idx)
    else:
        render_player(None)
        st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
        render_poster_wall(tracks)

    # 트랙리스트
    st.markdown("<div class='gold-divider'></div>", unsafe_allow_html=True)
    st.markdown("<div class='tracklist-label'>✦ TRACKLIST</div>", unsafe_allow_html=True)

    for i, t in enumerate(tracks):
        is_playing = i == current_track_idx
        dot   = "▶" if is_playing else f"{i+1:02d}"
        color = GOLD if is_playing else MUTED
        st.markdown(
            f'<div class="track-row">'
            f'<span style="color:{color};min-width:22px;font-size:11px">{dot}</span>'
            f'<span style="color:{TP};flex:1">{t.get("title","")}</span>'
            f'<span style="color:{MUTED}">{t.get("desc","")}</span>'
            f'</div>',
            unsafe_allow_html=True,
        )


main()