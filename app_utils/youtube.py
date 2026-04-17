# ─────────────────────────────────────────
#  utils/youtube.py
#  YouTube URL → video ID 파싱 · 썸네일 URL 생성
# ─────────────────────────────────────────

import re
from urllib.parse import urlparse, parse_qs
from app_config.settings import YOUTUBE


def extract_video_id(url: str) -> str | None:
    """
    다양한 YouTube URL 형식에서 video ID를 추출한다.

    지원 형식:
      - https://www.youtube.com/watch?v=VIDEO_ID
      - https://youtu.be/VIDEO_ID
      - https://youtube.com/embed/VIDEO_ID
      - https://youtube.com/shorts/VIDEO_ID
      - https://music.youtube.com/watch?v=VIDEO_ID
    """
    if not url or not isinstance(url, str):
        return None

    url = url.strip()

    try:
        parsed = urlparse(url)
        hostname = parsed.hostname or ""

        # youtu.be 단축 URL
        if hostname == "youtu.be":
            vid = parsed.path.lstrip("/").split("?")[0]
            return vid if _is_valid_id(vid) else None

        # youtube.com / music.youtube.com
        if "youtube.com" in hostname:
            # /watch?v=...
            if parsed.path == "/watch":
                vid = parse_qs(parsed.query).get("v", [None])[0]
                return vid if vid and _is_valid_id(vid) else None

            # /embed/VIDEO_ID  또는  /shorts/VIDEO_ID
            match = re.match(r"^/(embed|shorts|v)/([^/?&]+)", parsed.path)
            if match:
                vid = match.group(2)
                return vid if _is_valid_id(vid) else None

    except Exception:
        pass

    # 최후 수단: 정규식으로 11자리 ID 탐색
    match = re.search(r"(?:v=|youtu\.be/|embed/|shorts/)([A-Za-z0-9_-]{11})", url)
    if match:
        return match.group(1)

    return None


def _is_valid_id(vid: str) -> bool:
    """YouTube video ID는 11자리 영숫자 + 하이픈 + 언더스코어."""
    return bool(re.fullmatch(r"[A-Za-z0-9_-]{11}", vid))


def get_thumbnail_url(video_id: str, quality: str = "max") -> str:
    """
    video_id로 썸네일 URL을 반환한다.

    quality:
      - "max"  → maxresdefault (1280×720, 없을 수 있음)
      - "hq"   → hqdefault     (480×360, 항상 존재)
    """
    if quality == "max":
        return YOUTUBE["thumbnail_base"].format(video_id=video_id)
    return YOUTUBE["thumbnail_hq"].format(video_id=video_id)


def get_embed_url(video_id: str, autoplay: bool = True) -> str:
    """임베드용 URL을 반환한다."""
    base = YOUTUBE["embed_base"] + video_id
    params = []
    if autoplay:
        params.append("autoplay=1")
    return f"{base}?{'&'.join(params)}" if params else base


def is_valid_youtube_url(url: str) -> bool:
    """URL이 유효한 YouTube 링크인지 확인한다."""
    return extract_video_id(url) is not None


# ── 이미지 URL 도메인 허용 목록 ──────────────
ALLOWED_IMG_DOMAINS = {
    "img.youtube.com",
    "i.ytimg.com",
    "images.unsplash.com",
    "i.imgur.com",
    "cdn.discordapp.com",
    "media.discordapp.net",
    "pbs.twimg.com",          # 트위터/X 이미지
    "upload.wikimedia.org",
}


def is_valid_img_url(url: str) -> bool:
    """
    이미지 URL이 허용된 도메인인지 확인한다.
    빈 문자열은 허용 (썸네일 자동 사용).
    """
    if not url:
        return True
    try:
        from urllib.parse import urlparse
        hostname = urlparse(url).hostname or ""
        # 서브도메인 포함 체크 (예: cdn2.i.imgur.com)
        return any(hostname == d or hostname.endswith(f".{d}") for d in ALLOWED_IMG_DOMAINS)
    except Exception:
        return False