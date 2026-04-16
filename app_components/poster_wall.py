# ─────────────────────────────────────────
#  components/poster_wall.py
#  시네마 포스터 벽 HTML 컴포넌트
#  클릭 시 st.session_state에 선택 트랙 저장
# ─────────────────────────────────────────

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
import streamlit as st
from streamlit.components.v1 import html as st_html
from app_config.settings import THEME, FONTS, GOOGLE_FONTS_URL, POSTER

def _calc_height(track_count):
    cols     = max(1, 600 // (POSTER["min_width"] + POSTER["gap"]))
    rows     = max(1, -(-track_count // cols))
    poster_h = int(POSTER["min_width"] * 1.5)
    return poster_h * rows + POSTER["gap"] * rows + 60

def _build_html(tracks, playing_idx):
    tracks_json  = json.dumps(tracks, ensure_ascii=False)
    playing_json = json.dumps(playing_idx)
    GOLD = THEME['gold_primary']
    GOLDL= THEME['gold_light']
    BG   = THEME['bg_primary']
    BGS  = THEME['bg_secondary']
    TP   = THEME['text_primary']
    TM   = THEME['text_muted']
    BRD  = THEME['border']

    return f"""<!DOCTYPE html><html><head><meta charset="utf-8">
<link href="{GOOGLE_FONTS_URL}" rel="stylesheet">
<style>
*,*::before,*::after{{box-sizing:border-box;margin:0;padding:0;}}
body{{background:transparent;font-family:{FONTS['mono']};}}
.wall-label{{font-family:{FONTS['mono']};font-size:10px;letter-spacing:0.25em;color:{TM};margin-bottom:14px;padding-bottom:10px;border-bottom:1px solid {BRD};}}
.wall{{display:grid;grid-template-columns:repeat(auto-fill,minmax({POSTER['min_width']}px,1fr));gap:{POSTER['gap']}px;}}
.poster{{position:relative;cursor:pointer;border-radius:10px;overflow:hidden;aspect-ratio:{POSTER['aspect']};background:{BGS};border:1px solid {BRD};transition:transform 0.3s ease,border-color 0.3s ease,box-shadow 0.3s ease;}}
.poster:hover{{transform:translateY(-6px) scale(1.02);border-color:{GOLD};box-shadow:0 8px 30px {GOLD}33;}}
.poster.playing{{border-color:{GOLD};box-shadow:0 0 25px {GOLD}44;}}
.poster img{{width:100%;height:100%;object-fit:cover;display:block;transition:filter 0.3s;}}
.poster:hover img,.poster.playing img{{filter:brightness(0.4);}}
.no-img{{width:100%;height:100%;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:10px;background:{BGS};}}
.no-img svg{{width:36px;height:36px;opacity:0.2;}}
.no-img span{{font-size:11px;color:{TM};text-align:center;padding:0 10px;}}
.overlay{{position:absolute;inset:0;display:flex;flex-direction:column;justify-content:flex-end;padding:14px;background:linear-gradient(to top,rgba(6,8,15,0.95) 0%,rgba(6,8,15,0) 55%);opacity:0;transition:opacity 0.25s;}}
.poster:hover .overlay,.poster.playing .overlay{{opacity:1;}}
.play-ring{{position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);width:52px;height:52px;border-radius:50%;border:2px solid {GOLD};background:rgba(6,8,15,0.5);display:flex;align-items:center;justify-content:center;opacity:0;transition:opacity 0.25s;box-shadow:0 0 16px {GOLD}55;}}
.play-ring svg{{width:20px;height:20px;fill:{GOLD};margin-left:4px;}}
.poster:hover .play-ring,.poster.playing .play-ring{{opacity:1;}}
.eq{{display:none;gap:2px;align-items:flex-end;height:14px;margin-bottom:6px;}}
.poster.playing .eq{{display:flex;}}
.eq span{{display:block;width:3px;background:{GOLD};border-radius:1px;animation:eq-bar 0.8s ease-in-out infinite alternate;}}
.eq span:nth-child(1){{height:6px;animation-delay:0s;}}
.eq span:nth-child(2){{height:12px;animation-delay:0.15s;}}
.eq span:nth-child(3){{height:8px;animation-delay:0.3s;}}
.eq span:nth-child(4){{height:14px;animation-delay:0.1s;}}
@keyframes eq-bar{{from{{transform:scaleY(0.4);}}to{{transform:scaleY(1);}}}}
.poster-title{{font-family:{FONTS['display']};font-size:15px;letter-spacing:0.08em;color:{TP};line-height:1.15;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;text-shadow:0 0 10px {GOLD}55;}}
.poster-desc{{font-family:{FONTS['mono']};font-size:10px;color:{GOLD};margin-top:4px;letter-spacing:0.05em;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;}}
.empty{{text-align:center;padding:4rem 1rem;color:{TM};font-size:12px;border:1px dashed {BRD};border-radius:10px;letter-spacing:0.1em;}}
</style></head><body>
<div class="wall-label" id="wall-label">✦ NOW SHOWING</div>
<div class="wall" id="wall"></div>
<script>
const tracks={tracks_json};
let playingIdx={playing_json};
function render(){{
  const label=document.getElementById('wall-label');
  label.textContent='✦ NOW SHOWING — '+tracks.length+' TRACKS';
  const wall=document.getElementById('wall');
  if(!tracks.length){{wall.innerHTML='<div class="empty">사이드바에서 트랙을 추가해보세요</div>';return;}}
  wall.innerHTML=tracks.map((t,i)=>{{
    const isPlaying=i===playingIdx;
    const thumb=t.img?`<img src="${{t.img}}" alt="${{t.title}}" onerror="this.style.display='none';this.nextElementSibling.style.display='flex'">`:'';
    const ph=`<div class="no-img" style="${{t.img?'display:none':''}}"><svg viewBox="0 0 24 24" fill="none" stroke="{GOLD}" stroke-width="1.5"><circle cx="12" cy="12" r="10"/><polygon points="10,8 16,12 10,16" fill="{GOLD}" stroke="none"/></svg><span>${{t.title}}</span></div>`;
    return `<div class="poster ${{isPlaying?'playing':''}}" onclick="selectTrack(${{i}})">${{thumb}}${{ph}}<div class="play-ring"><svg viewBox="0 0 24 24"><polygon points="5,3 19,12 5,21"/></svg></div><div class="overlay"><div class="eq"><span></span><span></span><span></span><span></span></div><div class="poster-title">${{t.title}}</div>${{t.desc?`<div class="poster-desc">${{t.desc}}</div>`:''}}</div></div>`;
  }}).join('');
}}
function selectTrack(idx){{
  const url=new URL(window.parent.location.href);
  url.searchParams.set('selected_track',idx);
  window.parent.history.replaceState(null,'',url.toString());
  playingIdx=idx;render();
  window.parent.dispatchEvent(new Event('popstate'));
}}
render();
</script></body></html>"""

def render_poster_wall(tracks, playing_idx=None):
    if not isinstance(tracks, list):
        tracks = []
    height   = _calc_height(len(tracks)) if tracks else 160
    st_html(_build_html(tracks, playing_idx), height=height, scrolling=False)