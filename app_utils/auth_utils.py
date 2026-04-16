# ─────────────────────────────────────────
#  utils/auth_utils.py
#  비밀번호 해싱 · 검증 · 세션 관리
# ─────────────────────────────────────────

import bcrypt
import streamlit as st
from app_config.settings import AUTH
from app_utils.data_manager import (
    get_user,
    user_exists,
    create_user,
)


# ══════════════════════════════════════════
#  비밀번호 해싱
# ══════════════════════════════════════════

def hash_password(plain: str) -> str:
    """평문 비밀번호를 bcrypt 해시로 반환한다."""
    rounds = AUTH["bcrypt_rounds"]
    hashed = bcrypt.hashpw(plain.encode("utf-8"), bcrypt.gensalt(rounds))
    return hashed.decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    """평문 비밀번호와 저장된 해시를 비교한다."""
    try:
        return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))
    except Exception:
        return False


# ══════════════════════════════════════════
#  세션 관리
# ══════════════════════════════════════════

SESSION_KEY = AUTH["session_key"]


def get_current_user() -> str | None:
    """현재 로그인된 유저명을 반환. 비로그인 시 None."""
    return st.session_state.get(SESSION_KEY)


def is_logged_in() -> bool:
    """로그인 상태 여부를 반환한다."""
    return get_current_user() is not None


def login_session(username: str) -> None:
    """세션에 유저명을 저장한다."""
    st.session_state[SESSION_KEY] = username


def logout_session() -> None:
    """세션에서 유저 정보를 제거한다."""
    st.session_state.pop(SESSION_KEY, None)
    # 재생 중인 트랙 정보도 초기화
    st.session_state.pop("current_track", None)
    st.session_state.pop("current_playlist", None)


# ══════════════════════════════════════════
#  회원가입 · 로그인 로직
# ══════════════════════════════════════════

class AuthError(Exception):
    """인증 관련 예외."""
    pass


def sign_up(username: str, password: str, password_confirm: str) -> None:
    """
    회원가입을 처리한다.
    실패 시 AuthError를 raise.
    성공 시 자동으로 세션에 로그인.
    """
    username = username.strip()
    min_pw   = AUTH["min_pw_length"]

    # ── 유효성 검사 ──
    if not username:
        raise AuthError("아이디를 입력해주세요.")
    if len(username) < 3:
        raise AuthError("아이디는 3자 이상이어야 합니다.")
    if not username.isalnum():
        raise AuthError("아이디는 영문자와 숫자만 사용할 수 있습니다.")
    if not password:
        raise AuthError("비밀번호를 입력해주세요.")
    if len(password) < min_pw:
        raise AuthError(f"비밀번호는 {min_pw}자 이상이어야 합니다.")
    if password != password_confirm:
        raise AuthError("비밀번호가 일치하지 않습니다.")
    if user_exists(username):
        raise AuthError("이미 사용 중인 아이디입니다.")

    # ── 저장 ──
    pw_hash = hash_password(password)
    success = create_user(username, pw_hash)
    if not success:
        raise AuthError("회원가입 중 오류가 발생했습니다. 다시 시도해주세요.")

    login_session(username)


def sign_in(username: str, password: str) -> None:
    """
    로그인을 처리한다.
    실패 시 AuthError를 raise.
    성공 시 세션에 로그인.
    """
    username = username.strip()

    if not username or not password:
        raise AuthError("아이디와 비밀번호를 모두 입력해주세요.")

    user = get_user(username)
    if user is None:
        raise AuthError("존재하지 않는 아이디입니다.")

    if not verify_password(password, user["password_hash"]):
        raise AuthError("비밀번호가 올바르지 않습니다.")

    login_session(username)


def require_login() -> str:
    """
    로그인이 필요한 페이지에서 호출.
    비로그인 상태면 st.stop()으로 렌더링을 중단.
    로그인 상태면 현재 유저명을 반환.
    """
    user = get_current_user()
    if user is None:
        st.warning("로그인이 필요한 페이지입니다.")
        st.stop()
    return user