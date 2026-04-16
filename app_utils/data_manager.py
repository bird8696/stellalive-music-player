# ─────────────────────────────────────────
#  app_utils/data_manager.py
#  Supabase 기반 CRUD (JSON 파일 대체)
# ─────────────────────────────────────────

from app_utils.db import get_client


# ══════════════════════════════════════════
#  Users
# ══════════════════════════════════════════

def get_all_users() -> dict:
    db   = get_client()
    rows = db.table("users").select("*").execute().data
    return {r["username"]: r for r in rows}


def get_user(username: str) -> dict | None:
    db  = get_client()
    res = db.table("users").select("*").eq("username", username).execute().data
    return res[0] if res else None


def user_exists(username: str) -> bool:
    return get_user(username) is not None


def create_user(username: str, password_hash: str) -> bool:
    if user_exists(username):
        return False
    db = get_client()
    db.table("users").insert({
        "username"     : username,
        "password_hash": password_hash,
    }).execute()
    return True


def delete_user(username: str) -> bool:
    if not user_exists(username):
        return False
    db = get_client()
    db.table("users").delete().eq("username", username).execute()
    delete_all_playlists(username)
    return True


# ══════════════════════════════════════════
#  Playlists
# ══════════════════════════════════════════

def _get_playlist_row(username: str, name: str) -> dict | None:
    db  = get_client()
    res = db.table("playlists") \
            .select("*") \
            .eq("username", username) \
            .eq("name", name) \
            .execute().data
    return res[0] if res else None


def get_playlist_names(username: str) -> list[str]:
    db  = get_client()
    res = db.table("playlists") \
            .select("name") \
            .eq("username", username) \
            .order("created_at") \
            .execute().data
    return [r["name"] for r in res]


def get_playlist(username: str, playlist_name: str) -> list[dict]:
    row = _get_playlist_row(username, playlist_name)
    if not row:
        return []
    db  = get_client()
    res = db.table("tracks") \
            .select("*") \
            .eq("playlist_id", row["id"]) \
            .order("position") \
            .execute().data
    return [
        {
            "title": r["title"],
            "desc" : r["description"],
            "url"  : r["url"],
            "img"  : r["img"],
            "_id"  : r["id"],
        }
        for r in res
    ]


def playlist_exists(username: str, name: str) -> bool:
    return _get_playlist_row(username, name) is not None


def get_user_playlists(username: str) -> dict:
    names = get_playlist_names(username)
    return {n: get_playlist(username, n) for n in names}


def create_playlist(username: str, name: str) -> bool:
    if playlist_exists(username, name):
        return False
    db = get_client()
    db.table("playlists").insert({
        "username": username,
        "name"    : name,
    }).execute()
    return True


def rename_playlist(username: str, old_name: str, new_name: str) -> bool:
    row = _get_playlist_row(username, old_name)
    if not row or playlist_exists(username, new_name):
        return False
    db = get_client()
    db.table("playlists").update({"name": new_name}).eq("id", row["id"]).execute()
    return True


def delete_playlist(username: str, name: str) -> bool:
    row = _get_playlist_row(username, name)
    if not row:
        return False
    db = get_client()
    db.table("playlists").delete().eq("id", row["id"]).execute()
    return True


def delete_all_playlists(username: str) -> None:
    db = get_client()
    db.table("playlists").delete().eq("username", username).execute()


# ══════════════════════════════════════════
#  Tracks
# ══════════════════════════════════════════

def add_track(username: str, playlist_name: str, track: dict) -> bool:
    row = _get_playlist_row(username, playlist_name)
    if not row:
        create_playlist(username, playlist_name)
        row = _get_playlist_row(username, playlist_name)

    db       = get_client()
    count    = db.table("tracks").select("id", count="exact").eq("playlist_id", row["id"]).execute().count or 0

    db.table("tracks").insert({
        "playlist_id" : row["id"],
        "username"    : username,
        "title"       : track.get("title", ""),
        "description" : track.get("desc", ""),
        "url"         : track.get("url", ""),
        "img"         : track.get("img", ""),
        "position"    : count,
    }).execute()
    return True


def remove_track(username: str, playlist_name: str, track_index: int) -> bool:
    tracks = get_playlist(username, playlist_name)
    if track_index < 0 or track_index >= len(tracks):
        return False
    db = get_client()
    db.table("tracks").delete().eq("id", tracks[track_index]["_id"]).execute()
    return True


def update_track(username: str, playlist_name: str, track_index: int, updated: dict) -> bool:
    tracks = get_playlist(username, playlist_name)
    if track_index < 0 or track_index >= len(tracks):
        return False
    db = get_client()
    db.table("tracks").update({
        "title"      : updated.get("title", tracks[track_index]["title"]),
        "description": updated.get("desc",  tracks[track_index]["desc"]),
        "url"        : updated.get("url",   tracks[track_index]["url"]),
        "img"        : updated.get("img",   tracks[track_index]["img"]),
    }).eq("id", tracks[track_index]["_id"]).execute()
    return True


# ── Explore 페이지용 전체 트랙 조회 ──
def _read_playlists() -> dict:
    """모든 유저 플레이리스트 데이터 반환 (Explore 페이지 호환)."""
    db    = get_client()
    pls   = db.table("playlists").select("*").execute().data
    trks  = db.table("tracks").select("*").order("position").execute().data

    result: dict = {}
    for pl in pls:
        uname = pl["username"]
        pname = pl["name"]
        pid   = pl["id"]
        result.setdefault(uname, {})
        result[uname][pname] = [
            {
                "title": t["title"],
                "desc" : t["description"],
                "url"  : t["url"],
                "img"  : t["img"],
                "_id"  : t["id"],
            }
            for t in trks if t["playlist_id"] == pid
        ]
    return result