# ─────────────────────────────────────────
#  app_config/settings.py  —  Stella Theme
# ─────────────────────────────────────────

APP_TITLE       = "✦ STELLA MUSIC"
APP_ICON        = "✦"
APP_DESCRIPTION = "나만의 스텔라 뮤직 씨어터"

DATA_DIR        = "data"
USERS_FILE      = f"{DATA_DIR}/users.json"
PLAYLISTS_FILE  = f"{DATA_DIR}/playlists.json"

# ── Stella 테마 (딥 네이비 + 소프트 퍼플 + 별빛) ──
THEME = {
    "bg_primary"    : "#06080f",   # 깊은 우주 블랙
    "bg_secondary"  : "#0d1120",   # 네이비 카드 배경
    "bg_tertiary"   : "#141828",   # 입력창 배경
    "gold_primary"  : "#a78bfa",   # 스텔라 퍼플 (메인 액센트)
    "gold_light"    : "#c4b5fd",   # 밝은 퍼플 (호버)
    "gold_dark"     : "#7c5cbf",   # 어두운 퍼플 (눌림)
    "text_primary"  : "#e8e4f8",   # 별빛 흰색 텍스트
    "text_secondary": "#9d8fc0",   # 흐린 라벤더
    "text_muted"    : "#3d3560",   # 아주 흐린 퍼플
    "border"        : "#1a1830",   # 기본 테두리
    "border_gold"   : "#2a2448",   # 퍼플 계열 테두리
}

FONTS = {
    "display" : "'Cinzel', serif",
    "body"    : "'Crimson Pro', serif",
    "mono"    : "'Space Mono', monospace",
}

GOOGLE_FONTS_URL = (
    "https://fonts.googleapis.com/css2?"
    "family=Cinzel:wght@400;600;700&"
    "family=Crimson+Pro:ital,wght@0,400;0,600;1,400&"
    "family=Space+Mono&display=swap"
)

POSTER = {
    "min_width"  : 160,
    "gap"        : 18,
    "aspect"     : "2/3",
}

YOUTUBE = {
    "embed_base"    : "https://www.youtube.com/embed/",
    "thumbnail_base": "https://img.youtube.com/vi/{video_id}/maxresdefault.jpg",
    "thumbnail_hq"  : "https://img.youtube.com/vi/{video_id}/hqdefault.jpg",
}

AUTH = {
    "session_key"   : "current_user",
    "min_pw_length" : 6,
    "bcrypt_rounds" : 12,
}

PAGE_CONFIG = {
    "page_title"            : APP_TITLE,
    "page_icon"             : APP_ICON,
    "layout"                : "wide",
    "initial_sidebar_state" : "expanded",
}