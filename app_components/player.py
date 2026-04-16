# ─────────────────────────────────────────
#  components/player.py
#  YouTube 플레이어 임베드 컴포넌트
# ─────────────────────────────────────────

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
from streamlit.components.v1 import html as st_html
from app_utils.youtube import extract_video_id, get_embed_url
from app_config.settings import THEME, FONTS

GOLD = THEME['gold_primary']
BG   = THEME['bg_primary']
BGS  = THEME['bg_secondary']
TS   = THEME['text_secondary']
TM   = THEME['text_muted']
BRD  = THEME['border']
BRDG = THEME['border_gold']


def _build_player_html(track: dict, video_id: str, track_idx: int, total_tracks: int) -> str:
    title    = track.get("title", "")
    desc     = track.get("desc", "")
    desc_html = f"<div class='player-desc'>{desc}</div>" if desc else ""
    next_idx  = track_idx + 1 if track_idx + 1 < total_tracks else -1

    return f"""<!DOCTYPE html><html><head><meta charset="utf-8">
<style>
*,*::before,*::after{{box-sizing:border-box;margin:0;padding:0;}}
body{{background:transparent;font-family:{FONTS['mono']};}}
.player-wrap{{background:{BGS};border:1px solid {BRDG};border-radius:12px;overflow:hidden;box-shadow:0 0 30px {GOLD}18;}}
.player-bar{{display:flex;align-items:center;justify-content:space-between;padding:12px 18px;background:{BG};border-bottom:1px solid {BRD};}}
.player-info{{flex:1;min-width:0;}}
.player-title{{font-family:{FONTS['display']};font-size:20px;letter-spacing:0.1em;color:{GOLD};white-space:nowrap;overflow:hidden;text-overflow:ellipsis;text-shadow:0 0 12px {GOLD}55;}}
.player-desc{{font-size:11px;color:{TS};margin-top:3px;letter-spacing:0.05em;}}
.eq{{display:flex;gap:2px;align-items:flex-end;height:16px;margin-right:16px;flex-shrink:0;}}
.eq span{{display:block;width:3px;background:{GOLD};border-radius:1px;animation:eq-bar 0.8s ease-in-out infinite alternate;box-shadow:0 0 4px {GOLD}88;}}
.eq span:nth-child(1){{height:7px;animation-delay:0s;}}
.eq span:nth-child(2){{height:14px;animation-delay:0.15s;}}
.eq span:nth-child(3){{height:9px;animation-delay:0.3s;}}
.eq span:nth-child(4){{height:16px;animation-delay:0.1s;}}
.eq span:nth-child(5){{height:6px;animation-delay:0.2s;}}
@keyframes eq-bar{{from{{transform:scaleY(0.35);}}to{{transform:scaleY(1);}}}}
#yt-player{{width:100%;aspect-ratio:16/9;display:block;border:none;}}
.player-meta{{display:flex;align-items:center;justify-content:space-between;padding:8px 18px;background:{BG};border-top:1px solid {BRD};}}
.player-meta-left{{font-size:10px;letter-spacing:0.2em;color:{TM};}}
.meta-right{{display:flex;align-items:center;gap:12px;}}
.next-btn{{font-size:10px;color:{GOLD};background:none;border:1px solid {BRDG};border-radius:4px;padding:3px 10px;cursor:pointer;letter-spacing:0.08em;transition:all 0.2s;display:{'' if next_idx >= 0 else 'none'};}}
.next-btn:hover{{background:{GOLD}22;border-color:{GOLD};}}
.yt-link{{font-size:10px;color:{TM};text-decoration:none;letter-spacing:0.1em;transition:color 0.2s;}}
.yt-link:hover{{color:{GOLD};}}
</style>
</head>
<body>
<div class="player-wrap">
  <div class="player-bar">
    <div class="eq"><span></span><span></span><span></span><span></span><span></span></div>
    <div class="player-info">
      <div class="player-title">{title}</div>
      {desc_html}
    </div>
  </div>
  <div id="yt-player"></div>
  <div class="player-meta">
    <span class="player-meta-left">✦ NOW PLAYING {track_idx + 1} / {total_tracks}</span>
    <div class="meta-right">
      <button class="next-btn" onclick="goNext()">NEXT ▶▶</button>
      <a class="yt-link" href="{track.get('url','')}" target="_blank" rel="noopener noreferrer">YOUTUBE ↗</a>
    </div>
  </div>
</div>

<script>
const NEXT_IDX = {next_idx};

function goNext() {{
  if (NEXT_IDX < 0) return;
  const url = new URL(window.parent.location.href);
  url.searchParams.set('selected_track', NEXT_IDX);
  window.parent.history.replaceState(null, '', url.toString());
  window.parent.dispatchEvent(new Event('popstate'));
}}

// YouTube IFrame API
var tag = document.createElement('script');
tag.src = "https://www.youtube.com/iframe_api";
document.head.appendChild(tag);

var player;
function onYouTubeIframeAPIReady() {{
  player = new YT.Player('yt-player', {{
    videoId: '{video_id}',
    playerVars: {{
      autoplay: 1,
      rel: 0,
      modestbranding: 1,
    }},
    events: {{
      onStateChange: function(e) {{
        // 영상 끝나면 (state=0) 다음 트랙으로
        if (e.data === YT.PlayerState.ENDED) {{
          goNext();
        }}
      }}
    }}
  }});
}}
</script>
</body></html>"""


def _build_empty_html() -> str:
    return f"""<!DOCTYPE html><html><head><meta charset="utf-8">
<style>
body{{background:transparent;margin:0;font-family:{FONTS['mono']};}}
.placeholder{{display:flex;flex-direction:column;align-items:center;justify-content:center;
  height:120px;border:1px dashed {BRDG};border-radius:12px;color:{TM};
  font-size:12px;letter-spacing:0.15em;gap:10px;}}
.placeholder svg{{width:28px;height:28px;opacity:0.25;}}
</style></head><body>
<div class="placeholder">
  <svg viewBox="0 0 24 24" fill="none" stroke="{GOLD}" stroke-width="1.5">
    <circle cx="12" cy="12" r="10"/>
    <polygon points="10,8 16,12 10,16" fill="{GOLD}" stroke="none"/>
  </svg>
  포스터를 클릭하면 여기서 재생됩니다
</div>
</body></html>"""


def render_player(track: dict | None, track_idx: int = 0, total_tracks: int = 0) -> None:
    if track is None:
        st_html(_build_empty_html(), height=135, scrolling=False)
        return

    video_id = extract_video_id(track.get("url", ""))
    if not video_id:
        st.warning("⚠️ 유효하지 않은 YouTube URL입니다.")
        return

    player_height = int(600 * (9 / 16)) + 90
    st_html(
        _build_player_html(track, video_id, track_idx, total_tracks),
        height=player_height,
        scrolling=False
    )