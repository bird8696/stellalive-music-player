import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
from app_config.settings import PAGE_CONFIG, THEME, FONTS, GOOGLE_FONTS_URL
from app_utils.auth_utils import require_login
from app_utils.data_manager import _read_playlists, add_track, get_playlist_names, create_playlist
from app_components.player import render_player
from app_components.poster_wall import render_poster_wall

st.set_page_config(**PAGE_CONFIG)

BG    = THEME['bg_primary']
BGS   = THEME['bg_secondary']
BGT   = THEME['bg_tertiary']
GOLD  = THEME['gold_primary']
GOLDL = THEME['gold_light']
TP    = THEME['text_primary']
TS    = THEME['text_secondary']
MUTED = THEME['text_muted']
BGOLD = THEME['border_gold']
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
            max-width: 1200px;
            position: relative;
            z-index: 1;
        }}
        #MainMenu, footer {{ visibility: hidden; }}
        header[data-testid="stHeader"] {{
            background: transparent !important;
            backdrop-filter: none !important;
        }}
        [data-testid="stDecoration"] {{ display: none !important; }}

        .stDeployButton {{ display: none; }}

        /* 헤더 */
        .page-title {{
            font-family: {DISP};
            font-size: 28px;
            letter-spacing: 0.18em;
            color: {GOLD};
            text-shadow: 0 0 20px {GOLD}55;
        }}
        .gold-divider {{
            height: 1px;
            background: linear-gradient(to right, transparent, {GOLD}, transparent);
            opacity: 0.35;
            margin: 0.8rem 0 1.2rem;
        }}

        /* 검색창 */
        .stTextInput input {{
            background: {BGS} !important;
            border: 1px solid {BGOLD} !important;
            border-radius: 20px !important;
            color: {TP} !important;
            font-family: {MONO} !important;
            font-size: 13px !important;
            padding: 0.5rem 1rem !important;
        }}
        .stTextInput input:focus {{
            border-color: {GOLD} !important;
            box-shadow: 0 0 12px {GOLD}33 !important;
        }}
        .stTextInput label {{ display: none; }}

        /* 필터 탭 */
        .stTabs [data-baseweb="tab-list"] {{
            background: {BGS};
            border-radius: 8px;
            padding: 3px;
            border: 1px solid {BGOLD};
            gap: 3px;
        }}
        .stTabs [data-baseweb="tab"] {{
            font-family: {MONO};
            font-size: 11px;
            color: {TS};
            border-radius: 6px;
            letter-spacing: 0.1em;
        }}
        .stTabs [aria-selected="true"] {{
            background: {GOLD} !important;
            color: {BG} !important;
            font-weight: 700;
        }}
        .stTabs [data-baseweb="tab-highlight"] {{ display: none; }}

        /* 트랙 카드 패널 */
        .track-panel {{
            background: {BGS};
            border: 1px solid {BGOLD};
            border-radius: 12px;
            padding: 1.2rem 1.4rem;
            box-shadow: 0 0 24px {GOLD}12;
        }}
        .track-panel-title {{
            font-family: {DISP};
            font-size: 18px;
            letter-spacing: 0.1em;
            color: {GOLD};
            margin-bottom: 4px;
            text-shadow: 0 0 10px {GOLD}44;
        }}
        .track-panel-desc {{
            font-family: {MONO};
            font-size: 11px;
            color: {TS};
            margin-bottom: 12px;
        }}
        .owner-badge {{
            display: inline-flex;
            align-items: center;
            gap: 5px;
            font-family: {MONO};
            font-size: 10px;
            letter-spacing: 0.08em;
            color: {MUTED};
            background: {BG};
            border: 1px solid {BRD};
            border-radius: 20px;
            padding: 3px 10px;
            margin-bottom: 12px;
        }}

        /* 추가 버튼 */
        .stButton > button {{
            background: none !important;
            border: 1px solid {BGOLD} !important;
            color: {TP} !important;
            font-family: {MONO} !important;
            font-size: 12px !important;
            border-radius: 8px !important;
            transition: all 0.2s;
        }}
        .stButton > button:hover {{
            background: {GOLD}22 !important;
            border-color: {GOLD} !important;
        }}
        .stButton > button[kind="primary"] {{
            background: {GOLD} !important;
            color: {BG} !important;
            border-color: {GOLD} !important;
            font-weight: 700;
            box-shadow: 0 0 12px {GOLD}44;
        }}

        /* 스탯 */
        .stat-row {{
            display: flex;
            gap: 1.5rem;
            margin-bottom: 1rem;
        }}
        .stat-item {{
            font-family: {MONO};
            font-size: 10px;
            letter-spacing: 0.15em;
            color: {MUTED};
        }}
        .stat-item span {{
            display: block;
            font-size: 18px;
            color: {GOLD};
            font-weight: 500;
            letter-spacing: 0;
            margin-bottom: 2px;
        }}

        /* 셀렉트박스 */
        .stSelectbox > div > div {{
            background: {BGT} !important;
            border: 1px solid {BRD} !important;
            color: {TP} !important;
            border-radius: 8px !important;
        }}

        ::-webkit-scrollbar {{ width: 5px; }}
        ::-webkit-scrollbar-track {{ background: {BG}; }}
        ::-webkit-scrollbar-thumb {{ background: #2a2448; border-radius: 3px; }}
        ::-webkit-scrollbar-thumb:hover {{ background: {GOLD}; }}
    </style>
    """, unsafe_allow_html=True)


def _get_all_tracks() -> list[dict]:
    """모든 유저 플레이리스트에서 트랙 수집."""
    result = []
    for username, playlists in _read_playlists().items():
        for pl_name, tracks in playlists.items():
            for track in tracks:
                result.append({**track, "_owner": username, "_playlist": pl_name})
    return result


def _handle_track_selection(tracks):
    raw = st.query_params.get("selected_track")
    if raw is None:
        return
    try:
        idx = int(raw)
        if 0 <= idx < len(tracks):
            st.session_state["explore_track"]     = tracks[idx]
            st.session_state["explore_track_idx"] = idx
    except (ValueError, TypeError):
        pass
    st.query_params.clear()


def main():
    _inject_styles()
    # 비로그인 시 메인 페이지로 안내
    if "current_user" not in st.session_state:
        st.markdown(
            f'''<div style="text-align:center;padding:4rem;font-family:{MONO};
            font-size:13px;color:{MUTED}">
            <div style="font-size:32px;margin-bottom:1rem">✦</div>
            로그인이 필요합니다<br>
            <a href="/" style="color:{GOLD};text-decoration:none;letter-spacing:0.1em">
            → 메인으로 이동</a></div>''',
            unsafe_allow_html=True,
        )
        st.stop()
    username = st.session_state["current_user"]

    # ── 헤더 ──
    st.markdown(
        '<div class="page-title">✦ EXPLORE</div>'
        '<div class="gold-divider"></div>',
        unsafe_allow_html=True,
    )

    all_tracks = _get_all_tracks()

    if not all_tracks:
        st.info("아직 등록된 트랙이 없어요. 내 플레이리스트에서 먼저 추가해보세요!", icon="✦")
        return

    # ── 통계 ──
    owners = list({t["_owner"] for t in all_tracks})
    st.markdown(
        f'<div class="stat-row">'
        f'<div class="stat-item"><span>{len(all_tracks)}</span>TRACKS</div>'
        f'<div class="stat-item"><span>{len(owners)}</span>USERS</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

    # ── 검색 + 필터 ──
    col_search, col_filter = st.columns([3, 1], gap="small")
    with col_search:
        search = st.text_input("검색", placeholder="🔍  제목 또는 아티스트 검색...")
    with col_filter:
        filter_owner = st.selectbox(
            "유저 필터",
            ["전체"] + owners,
            key="explore_filter_owner",
            label_visibility="collapsed",
        )

    filtered = all_tracks
    if search:
        q = search.lower()
        filtered = [t for t in filtered if q in t.get("title","").lower() or q in t.get("desc","").lower()]
    if filter_owner != "전체":
        filtered = [t for t in filtered if t["_owner"] == filter_owner]

    if not filtered:
        st.warning("검색 결과가 없어요.", icon="✦")
        return

    if search or filter_owner != "전체":
        st.caption(f"✦ {len(filtered)}개 트랙")

    # ── 트랙 선택 처리 ──
    _handle_track_selection(filtered)
    current_track = st.session_state.get("explore_track")
    current_idx   = st.session_state.get("explore_track_idx")

    # ── 레이아웃 ──
    if current_track:
        col_left, col_right = st.columns([4, 7], gap="large")

        with col_left:
            # 플레이어
            render_player(current_track, track_idx=current_idx or 0, total_tracks=len(filtered))

            st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)

            # 트랙 정보 패널
            owner = current_track.get("_owner", "")
            pl    = current_track.get("_playlist", "")
            st.markdown(
                f'<div class="track-panel">'
                f'<div class="track-panel-title">{current_track.get("title","")}</div>'
                f'<div class="track-panel-desc">{current_track.get("desc","")}</div>'
                f'<div class="owner-badge">👤 {owner}  ·  {pl}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

            st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

            # 내 플레이리스트에 추가
            st.markdown(
                f'<div style="font-family:{MONO};font-size:10px;letter-spacing:0.2em;color:{MUTED};margin-bottom:6px">내 플레이리스트에 추가</div>',
                unsafe_allow_html=True,
            )
            my_pls = get_playlist_names(username)
            if my_pls:
                col_sel, col_btn = st.columns([3, 1], gap="small")
                with col_sel:
                    target_pl = st.selectbox(
                        "플레이리스트", my_pls,
                        label_visibility="collapsed",
                        key="explore_target_pl",
                    )
                with col_btn:
                    if st.button("✦ 추가", key="btn_explore_add", type="primary"):
                        track_to_add = {k: v for k, v in current_track.items() if not k.startswith("_")}
                        add_track(username, target_pl, track_to_add)
                        st.success("추가 완료! ✦")
            else:
                st.caption("내 플레이리스트가 없어요.")
                if st.button("플레이리스트 만들기", key="btn_make_pl"):
                    create_playlist(username, "My Playlist")
                    st.rerun()

        with col_right:
            render_poster_wall(filtered, playing_idx=current_idx)

    else:
        render_poster_wall(filtered)


main()