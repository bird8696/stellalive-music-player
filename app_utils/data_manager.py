# ─────────────────────────────────────────
#  utils/data_manager.py
#  users.json · playlists.json CRUD 전담
# ─────────────────────────────────────────

import json
import os
from typing import Any
from app_config.settings import USERS_FILE, PLAYLISTS_FILE, DATA_DIR


# ══════════════════════════════════════════
#  내부 헬퍼
# ══════════════════════════════════════════

def _ensure_data_dir() -> None:
    """data/ 디렉터리가 없으면 생성한다."""
    os.makedirs(DATA_DIR, exist_ok=True)


def _read(filepath: str) -> dict:
    """JSON 파일을 읽어 dict로 반환. 없으면 빈 dict."""
    _ensure_data_dir()
    if not os.path.exists(filepath):
        return {}
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return {}


def _write(filepath: str, data: dict) -> None:
    """dict를 JSON 파일에 저장한다."""
    _ensure_data_dir()
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# ══════════════════════════════════════════
#  Users  (users.json)
#
#  구조:
#  {
#    "username": {
#      "password_hash": "...",
#      "created_at": "2024-01-01T00:00:00"
#    },
#    ...
#  }
# ══════════════════════════════════════════

def get_all_users() -> dict:
    """전체 유저 데이터를 반환한다."""
    return _read(USERS_FILE)


def get_user(username: str) -> dict | None:
    """username에 해당하는 유저 정보를 반환. 없으면 None."""
    users = get_all_users()
    return users.get(username)


def user_exists(username: str) -> bool:
    """해당 username이 이미 존재하는지 확인한다."""
    return username in get_all_users()


def create_user(username: str, password_hash: str) -> bool:
    """
    새 유저를 생성한다.
    이미 존재하면 False를 반환.
    """
    users = get_all_users()
    if username in users:
        return False

    from datetime import datetime
    users[username] = {
        "password_hash": password_hash,
        "created_at": datetime.now().isoformat(),
    }
    _write(USERS_FILE, users)
    return True


def delete_user(username: str) -> bool:
    """유저를 삭제한다. 존재하지 않으면 False."""
    users = get_all_users()
    if username not in users:
        return False
    del users[username]
    _write(USERS_FILE, users)

    # 해당 유저의 플레이리스트도 함께 삭제
    delete_all_playlists(username)
    return True


# ══════════════════════════════════════════
#  Playlists  (playlists.json)
#
#  구조:
#  {
#    "username": {
#      "playlist_name": [
#        {
#          "title"  : "곡 제목",
#          "desc"   : "아티스트 / 설명",
#          "url"    : "https://youtu.be/...",
#          "img"    : "https://...",
#          "added_at": "2024-01-01T00:00:00"
#        },
#        ...
#      ]
#    },
#    ...
#  }
# ══════════════════════════════════════════

def _read_playlists() -> dict:
    return _read(PLAYLISTS_FILE)


def _write_playlists(data: dict) -> None:
    _write(PLAYLISTS_FILE, data)


# ── 플레이리스트 목록 ─────────────────────

def get_user_playlists(username: str) -> dict:
    """유저의 모든 플레이리스트 {이름: [트랙, ...]} 반환."""
    all_data = _read_playlists()
    return all_data.get(username, {})


def get_playlist_names(username: str) -> list[str]:
    """유저의 플레이리스트 이름 목록을 반환한다."""
    return list(get_user_playlists(username).keys())


def get_playlist(username: str, playlist_name: str) -> list[dict]:
    """특정 플레이리스트의 트랙 목록을 반환. 없으면 빈 리스트."""
    return get_user_playlists(username).get(playlist_name, [])


def playlist_exists(username: str, playlist_name: str) -> bool:
    return playlist_name in get_user_playlists(username)


# ── 플레이리스트 CRUD ─────────────────────

def create_playlist(username: str, playlist_name: str) -> bool:
    """
    새 플레이리스트를 생성한다.
    이미 존재하면 False.
    """
    all_data = _read_playlists()
    user_data = all_data.setdefault(username, {})

    if playlist_name in user_data:
        return False

    user_data[playlist_name] = []
    _write_playlists(all_data)
    return True


def rename_playlist(username: str, old_name: str, new_name: str) -> bool:
    """플레이리스트 이름을 변경한다."""
    all_data = _read_playlists()
    user_data = all_data.get(username, {})

    if old_name not in user_data or new_name in user_data:
        return False

    user_data[new_name] = user_data.pop(old_name)
    _write_playlists(all_data)
    return True


def delete_playlist(username: str, playlist_name: str) -> bool:
    """플레이리스트를 삭제한다."""
    all_data = _read_playlists()
    user_data = all_data.get(username, {})

    if playlist_name not in user_data:
        return False

    del user_data[playlist_name]
    _write_playlists(all_data)
    return True


def delete_all_playlists(username: str) -> None:
    """유저의 모든 플레이리스트를 삭제한다."""
    all_data = _read_playlists()
    all_data.pop(username, None)
    _write_playlists(all_data)


# ── 트랙 CRUD ─────────────────────────────

def add_track(username: str, playlist_name: str, track: dict) -> bool:
    """
    플레이리스트에 트랙을 추가한다.
    플레이리스트가 없으면 자동 생성.

    track 필수 키: title, url
    track 선택 키: desc, img
    """
    from datetime import datetime

    all_data = _read_playlists()
    user_data = all_data.setdefault(username, {})
    playlist  = user_data.setdefault(playlist_name, [])

    new_track: dict[str, Any] = {
        "title"   : track.get("title", "제목 없음"),
        "desc"    : track.get("desc", ""),
        "url"     : track.get("url", ""),
        "img"     : track.get("img", ""),
        "added_at": datetime.now().isoformat(),
    }
    playlist.append(new_track)
    _write_playlists(all_data)
    return True


def remove_track(username: str, playlist_name: str, track_index: int) -> bool:
    """인덱스로 트랙을 삭제한다."""
    all_data = _read_playlists()
    playlist = all_data.get(username, {}).get(playlist_name, [])

    if track_index < 0 or track_index >= len(playlist):
        return False

    playlist.pop(track_index)
    _write_playlists(all_data)
    return True


def update_track(username: str, playlist_name: str, track_index: int, updated: dict) -> bool:
    """트랙 정보를 수정한다."""
    all_data = _read_playlists()
    playlist = all_data.get(username, {}).get(playlist_name, [])

    if track_index < 0 or track_index >= len(playlist):
        return False

    playlist[track_index].update({
        k: v for k, v in updated.items()
        if k in ("title", "desc", "url", "img")
    })
    _write_playlists(all_data)
    return True


def reorder_tracks(username: str, playlist_name: str, new_order: list[int]) -> bool:
    """
    트랙 순서를 변경한다.
    new_order: 기존 인덱스의 새 순서 리스트 (예: [2, 0, 1])
    """
    all_data  = _read_playlists()
    user_data = all_data.get(username, {})
    playlist  = user_data.get(playlist_name, [])

    if sorted(new_order) != list(range(len(playlist))):
        return False

    user_data[playlist_name] = [playlist[i] for i in new_order]
    _write_playlists(all_data)
    return True