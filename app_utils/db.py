# ─────────────────────────────────────────
#  app_utils/db.py
#  Supabase 클라이언트 싱글톤
# ─────────────────────────────────────────

import streamlit as st
from supabase import create_client, Client

@st.cache_resource
def get_client() -> Client:
    url = st.secrets["supabase"]["url"]
    key = st.secrets["supabase"]["key"]
    return create_client(url, key)