import streamlit as st
import folium
from streamlit_folium import st_folium
import json
import os
import base64
from pathlib import Path

# ─── Page Config ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="HIVE · Acoustic Heritage Atlas",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─── CSS ────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap');

/* ── Reset & Base ── */
#MainMenu, footer, header { visibility: hidden; }
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.block-container { padding: 1.5rem 2rem 0rem 2rem; max-width: 100%; }

/* ── Background ── */
.stApp { background: #05081a; }

/* ── Top header bar ── */
.hive-header {
    display: flex; align-items: center; justify-content: space-between;
    padding: 10px 0 14px 0; border-bottom: 1px solid #101c38; margin-bottom: 18px;
}
.hive-brand { display: flex; align-items: center; gap: 10px; }
.hive-dot { width: 10px; height: 10px; border-radius: 50%; background: #1DB584;
    animation: pulse 2.2s ease-in-out infinite; flex-shrink: 0; }
@keyframes pulse { 0%,100%{opacity:1} 50%{opacity:.35} }
.hive-title { font-size: 17px; font-weight: 600; color: #c8ddf8; letter-spacing: -.02em; }
.hive-sub   { font-size: 12px; color: #1e3050; margin-left: 4px; }
.hive-stats { display: flex; gap: 24px; }
.hstat { text-align: right; }
.hstat-n { font-size: 20px; font-weight: 500; color: #8aaec8; line-height: 1; }
.hstat-l { font-size: 9px; color: #1e3050; text-transform: uppercase; letter-spacing: .07em; margin-top: 2px; }

/* ── Filter pills ── */
.filter-row { display: flex; gap: 6px; margin-bottom: 14px; flex-wrap: wrap; }
.fpill { display: inline-block; font-size: 10px; padding: 4px 12px;
    border-radius: 12px; border: 1px solid #101c38; color: #243858;
    cursor: pointer; transition: all .15s; }
.fpill.active { background: #0a1a32; color: #4a8cd4; border-color: #1a3870; }

/* ── Map panel ── */
.map-wrap { border-radius: 12px; overflow: hidden; border: 1px solid #101c38; }
.map-label { font-size: 10px; color: #1e3050; text-transform: uppercase;
    letter-spacing: .07em; margin-bottom: 8px; }

/* ── Right panel ── */
.rpanel {
    background: #06091e; border-radius: 12px;
    border: 1px solid #101c38; overflow: hidden; height: 100%;
}
.rp-empty {
    display: flex; flex-direction: column; align-items: center;
    justify-content: center; height: 400px; gap: 12px;
}
.rp-empty-icon { font-size: 32px; opacity: .3; }
.rp-empty-text { font-size: 12px; color: #1e3050; text-align: center; line-height: 1.6; }

/* ── Location detail card ── */
.loc-era { font-size: 9px; text-transform: uppercase; letter-spacing: .1em;
    font-weight: 600; margin-bottom: 6px; }
.loc-name { font-size: 22px; font-weight: 300; color: #d0e8ff;
    letter-spacing: -.025em; line-height: 1.15; margin: 0 0 4px; }
.loc-region { font-size: 11px; color: #1e3050; margin: 0 0 10px; }
.loc-desc { font-size: 12px; color: #2e4a6a; line-height: 1.6; margin: 0 0 14px; }

/* ── Soundmarks list ── */
.sm-label { font-size: 9px; text-transform: uppercase; letter-spacing: .07em;
    color: #172438; margin: 0 0 8px; font-weight: 500; }
.sm-item { display: flex; align-items: center; gap: 8px;
    padding: 6px 0; border-bottom: 1px solid #0a1428; }
.sm-item:last-child { border-bottom: none; }
.sm-bar { width: 3px; height: 12px; border-radius: 2px; flex-shrink: 0; }
.sm-text { font-size: 11px; color: #243858; }
.sm-text.gone { color: #172438; text-decoration: line-through; font-style: italic; }
.sm-gone-bar { opacity: .2; }

/* ── Waveform ── */
.wf-label { font-size: 9px; text-transform: uppercase; letter-spacing: .07em;
    color: #172438; margin-bottom: 8px; font-weight: 500; }
.wf-bars { display: flex; align-items: flex-end; gap: 2px; height: 44px;
    padding: 0 2px; margin-bottom: 10px; }
.wf-bar { flex: 1; border-radius: 2px 2px 0 0; opacity: .7; }

/* ── Era tabs ── */
.era-label { font-size: 9px; text-transform: uppercase; letter-spacing: .07em;
    color: #172438; margin-bottom: 7px; }
.era-row { display: flex; gap: 4px; margin-bottom: 14px; }
.era-tab { flex: 1; text-align: center; padding: 5px 0; font-size: 10px;
    border-radius: 6px; border: 1px solid #0e1830; color: #1e3050;
    cursor: pointer; transition: all .15s; }
.era-tab.active { background: #0e1830; color: #8aaac8; border-color: #1a2e50; }

/* ── Play row ── */
.play-row { display: flex; align-items: center; gap: 10px;
    padding: 12px 0 4px; border-top: 1px solid #0a1428; margin-top: 10px; }
.play-btn { width: 34px; height: 34px; border-radius: 50%; display: flex;
    align-items: center; justify-content: center; flex-shrink: 0; }
.play-info .ptitle { font-size: 11px; color: #4a6880; font-weight: 500; }
.play-info .psub   { font-size: 10px; color: #1e3050; margin-top: 2px; }
.pdur { font-size: 10px; color: #1e3050; }

/* ── Upload tab ── */
.upload-coord { font-size: 12px; color: #4a8cd4; margin-bottom: 12px;
    padding: 8px 12px; background: #040714; border-radius: 8px;
    border: 1px solid #0a1428; font-family: monospace; }
.upload-info { font-size: 11px; color: #1e3050; text-align: center;
    padding: 16px; line-height: 1.7; }

/* ── Streamlit overrides for dark theme ── */
.stTabs [data-baseweb="tab-list"] {
    background: #040714 !important; border-bottom: 1px solid #101c38 !important;
    gap: 0; padding: 0 16px;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important; color: #1e3050 !important;
    border-bottom: 2px solid transparent !important;
    font-size: 12px !important; padding: 10px 16px !important;
}
.stTabs [aria-selected="true"] {
    color: #8aaac8 !important; border-bottom-color: #4a8cd4 !important;
    background: transparent !important;
}
.stTabs [data-baseweb="tab-panel"] {
    background: #06091e !important; padding: 16px !important;
}

/* ── Inputs dark ── */
.stTextInput input, .stTextArea textarea, .stSelectbox select {
    background: #040714 !important; border: 1px solid #101c38 !important;
    color: #8aaac8 !important; border-radius: 8px !important;
}
.stTextInput label, .stTextArea label, .stSelectbox label,
.stFileUploader label { color: #243858 !important; font-size: 11px !important; }

/* ── Submit button ── */
div.stButton > button {
    background: #E8A020 !important; color: #05081a !important;
    border: none !important; border-radius: 8px !important;
    font-weight: 600 !important; font-size: 12px !important;
    width: 100%; padding: 10px !important; transition: all .15s !important;
}
div.stButton > button:hover {
    background: #d4901a !important; transform: scale(1.01) !important;
}
div.stFormSubmitButton > button {
    background: #1DB584 !important; color: #04342C !important;
    border: none !important; border-radius: 8px !important;
    font-weight: 600 !important; font-size: 12px !important;
    width: 100%; padding: 10px !important;
}

/* ── Audio player ── */
audio { width: 100%; border-radius: 8px; margin-top: 8px; }
audio::-webkit-media-controls-panel { background: #040714 !important; }

/* ── Success/info messages ── */
.stSuccess { background: #041a10 !important; border: 1px solid #1D9E75 !important;
    color: #4ecf9a !important; border-radius: 8px !important; }
.stInfo { background: #04102a !important; border: 1px solid #1a3870 !important;
    color: #4a8cd4 !important; border-radius: 8px !important; }
.stWarning { background: #1a1000 !important; border: 1px solid #E8A020 !important;
    color: #E8A020 !important; border-radius: 8px !important; }

/* ── Divider ── */
hr { border-color: #101c38 !important; margin: 0.8rem 0 !important; }

/* ── Metric cards ── */
[data-testid="metric-container"] {
    background: #06091e; border: 1px solid #101c38;
    border-radius: 10px; padding: 14px 16px;
}
[data-testid="metric-container"] label { color: #1e3050 !important; font-size: 10px !important; text-transform: uppercase; letter-spacing: .07em; }
[data-testid="metric-container"] [data-testid="stMetricValue"] { color: #8aaac8 !important; font-size: 22px !important; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: #05081a; }
::-webkit-scrollbar-thumb { background: #101c38; border-radius: 2px; }

/* ── Toast ── */
.stToast { background: #06091e !important; border: 1px solid #1D9E75 !important; color: #4ecf9a !important; }
</style>
""", unsafe_allow_html=True)

# ─── Data Setup ─────────────────────────────────────────────────────────────
os.makedirs("data/audio", exist_ok=True)

SAMPLE_DATA = [
    {
        "id": "varanasi",
        "region": "Varanasi Ghats",
        "country": "India",
        "latitude": 25.31,
        "longitude": 83.01,
        "category": "heritage",
        "use_case": "Acoustic time-travel tourism",
        "era": "1990s",
        "description": "Dawn aarti, Sanskrit chanting, and boatmen's calls on the Ganga. The world's oldest living city's sonic soul — 94 soundmarks documented, 7 historically extinct.",
        "soundmarks": [
            {"text": "Ganga aarti chant — Dashashwamedh Ghat, pre-dawn", "alive": True},
            {"text": "Boatman's call — Nauvat Ghara dialect, near-extinct", "alive": True},
            {"text": "Dhrupad vocal — Hanuman Ghat, morning riyaz", "alive": True},
            {"text": "Steam whistle — Manduadih railway, removed 1987", "alive": False},
        ],
        "color": "#E8A020",
        "audio_path": None,
        "archive_ref": "Rajan Mishra Archive · All India Radio · 1992",
        "coords_display": "25.31°N  83.01°E",
    },
    {
        "id": "suzhou",
        "region": "Suzhou Old Town",
        "country": "China",
        "latitude": 31.30,
        "longitude": 120.62,
        "category": "dialect",
        "use_case": "Living dialect capture",
        "era": "2000s",
        "description": "Endangered Wu dialect and ancient water-town sounds — canals, silk merchants, Suzhou opera drifting from tea houses. 6x increase in AI soundscape projects 2018–2023.",
        "soundmarks": [
            {"text": "Wu dialect street vendors — canal-side morning market", "alive": True},
            {"text": "Suzhou Kunqu opera — Humble Administrator's Garden", "alive": True},
            {"text": "Silk-loom rhythm — Shantang Street workshops", "alive": False},
            {"text": "Night-soil collector's call — pre-modernisation", "alive": False},
        ],
        "color": "#1DB584",
        "audio_path": None,
        "archive_ref": "Suzhou Cultural Bureau · Wu Dialect Institute · 2004",
        "coords_display": "31.30°N  120.62°E",
    },
    {
        "id": "sanaa",
        "region": "Sana'a Old City",
        "country": "Yemen",
        "latitude": 15.35,
        "longitude": 44.21,
        "category": "conflict",
        "use_case": "War trauma relief",
        "era": "Pre-2011",
        "description": "Pre-conflict acoustic environments of the UNESCO-listed Old City. For displaced Yemeni families in European shelters — familiar sound as a non-pharmacological therapeutic tool.",
        "soundmarks": [
            {"text": "Muezzin call — Great Mosque of Sana'a, dawn azan", "alive": True},
            {"text": "Qat market — Al-Milh souk, afternoon chatter", "alive": False},
            {"text": "Brassware hammering — metalworkers' quarter", "alive": False},
            {"text": "Children's play — Al-Talh neighbourhood, 2009", "alive": False},
        ],
        "color": "#E05A3A",
        "audio_path": None,
        "archive_ref": "Yemen Heritage Documentation Project · 2008",
        "coords_display": "15.35°N  44.21°E",
    },
    {
        "id": "bundelkhand",
        "region": "Bundelkhand Villages",
        "country": "India",
        "latitude": 25.20,
        "longitude": 78.50,
        "category": "language",
        "use_case": "Dialect-native voice AI",
        "era": "Living",
        "description": "Rural Bundelkhandi communities excluded from standard Hindi AI systems. One of India's most expressive dialects — tonal patterns and vocabulary with no AI representation.",
        "soundmarks": [
            {"text": "Bundelkhandi folk song — rai dance, Panna district", "alive": True},
            {"text": "Elder oral narrative — seasonal farming cycle", "alive": True},
            {"text": "Bullock-cart driver's call — distinct tonal marker", "alive": True},
            {"text": "Weekly haat (market) ambient — Tikamgarh", "alive": True},
        ],
        "color": "#8B7FE8",
        "audio_path": None,
        "archive_ref": "Community Archive · Bundelkhand University Fieldwork",
        "coords_display": "25.20°N  78.50°E",
    },
    {
        "id": "damascus",
        "region": "Damascus Old City",
        "country": "Syria",
        "latitude": 33.51,
        "longitude": 36.29,
        "category": "conflict",
        "use_case": "War trauma relief",
        "era": "Pre-2011",
        "description": "Pre-war soundscape of the oldest continuously inhabited city — the Hamidiyeh souk, the Umayyad Mosque courtyard echoes, neighbourhood tea-house radio.",
        "soundmarks": [
            {"text": "Hamidiyeh souk — textile merchant calls, pre-2011", "alive": False},
            {"text": "Umayyad Mosque azan — distinctive maqam", "alive": True},
            {"text": "Barada river ambient — now largely dry", "alive": False},
            {"text": "Ice-cream seller — Boza cart bell, Al-Midan district", "alive": False},
        ],
        "color": "#E05A3A",
        "audio_path": None,
        "archive_ref": "Syrian Archive · AMAR Foundation · 2009",
        "coords_display": "33.51°N  36.29°E",
    },
    {
        "id": "nagaland",
        "region": "Nagaland Hills",
        "country": "India",
        "latitude": 26.15,
        "longitude": 94.56,
        "category": "language",
        "use_case": "Endangered language school",
        "era": "Living",
        "description": "Dozens of Naga tribal dialects at risk from AI standardisation. Community elders hold phonetic knowledge no institution has documented — each village a distinct acoustic world.",
        "soundmarks": [
            {"text": "Angami war chant — ceremonial rhythm, Kohima", "alive": True},
            {"text": "Lotha harvest song — Wokha district, elder chorus", "alive": True},
            {"text": "Naga woodpecker signal — inter-village communication", "alive": False},
            {"text": "Morung night storytelling — traditional longhouse", "alive": True},
        ],
        "color": "#8B7FE8",
        "audio_path": None,
        "archive_ref": "Tyndale-Biscoe Archive · Nagaland Cultural Society",
        "coords_display": "26.15°N  94.56°E",
    },
    {
        "id": "kyiv",
        "region": "Kyiv Podil",
        "country": "Ukraine",
        "latitude": 50.46,
        "longitude": 30.52,
        "category": "conflict",
        "use_case": "War trauma relief",
        "era": "Pre-2022",
        "description": "Pre-war Podil neighbourhood sounds, Maidan trams, and the ambient life of a city millions had to flee overnight. The most recently archived soundscape on the platform.",
        "soundmarks": [
            {"text": "Tram line 19 — Kontraktova Ploshcha, morning", "alive": False},
            {"text": "Street musician — bandurist near St. Andrew's Church", "alive": False},
            {"text": "Dnipro river ambient — Poshtova Ploshcha, summer", "alive": True},
            {"text": "Kyiv market — Zhytniy Rynok, vendor calls, 2021", "alive": False},
        ],
        "color": "#E05A3A",
        "audio_path": None,
        "archive_ref": "Звукова Спадщина (Sound Heritage) Ukraine · 2021",
        "coords_display": "50.46°N  30.52°E",
    },
    {
        "id": "casablanca",
        "region": "Casablanca Medina",
        "country": "Morocco",
        "latitude": 33.59,
        "longitude": -7.61,
        "category": "diaspora",
        "use_case": "Diaspora reconnection",
        "era": "1990s",
        "description": "Darija-speaking diaspora across France, Spain, and the Netherlands — reconnecting with medina sounds, souk rhythms, and the Call to Prayer cadences of childhood.",
        "soundmarks": [
            {"text": "Medina souk — spice quarter, Derb Omar district", "alive": True},
            {"text": "Gnawa musicians — Jemaa al-Fna adjacent gathering", "alive": True},
            {"text": "Farrouj seller's cart bell — neighbourhood streets", "alive": False},
            {"text": "Oud repair workshop — Rue Nationale, 1990s", "alive": False},
        ],
        "color": "#D4537E",
        "audio_path": None,
        "archive_ref": "Institut Royal de la Culture Amazighe · IRCAM · 1998",
        "coords_display": "33.59°N  7.61°W",
    },
]

CATEGORY_COLORS = {
    "heritage":  "#E8A020",
    "dialect":   "#1DB584",
    "conflict":  "#E05A3A",
    "language":  "#8B7FE8",
    "diaspora":  "#D4537E",
}

CATEGORY_LABELS = {
    "heritage":  "Heritage soundscape",
    "dialect":   "Living dialect capture",
    "conflict":  "Conflict trauma relief",
    "language":  "Endangered language",
    "diaspora":  "Diaspora reconnection",
}

WAVEFORM_HEIGHTS = [12,22,36,16,30,44,20,40,14,38,46,18,40,28,16,44,24,38,14,32,44,22,36,12,40,28,20,44,24,36,14,42,18,34,46,10,30,44]

# ─── Session State ───────────────────────────────────────────────────────────
if "metadata" not in st.session_state:
    if os.path.exists("data/metadata.json"):
        with open("data/metadata.json") as f:
            saved = json.load(f)
        existing_ids = {d["id"] for d in saved}
        merged = SAMPLE_DATA + [d for d in saved if d["id"] not in {s["id"] for s in SAMPLE_DATA}]
        st.session_state.metadata = merged
    else:
        st.session_state.metadata = SAMPLE_DATA.copy()

if "selected_id" not in st.session_state:
    st.session_state.selected_id = "varanasi"

if "active_filter" not in st.session_state:
    st.session_state.active_filter = "all"

# ─── Header ─────────────────────────────────────────────────────────────────
total = len(st.session_state.metadata)
with_audio = sum(1 for d in st.session_state.metadata if d.get("audio_path"))
conflict_count = sum(1 for d in st.session_state.metadata if d.get("category") == "conflict")
lang_count = sum(1 for d in st.session_state.metadata if d.get("category") in ("language","dialect"))

c1, c2, c3, c4, c5 = st.columns([3, 1, 1, 1, 1])
with c1:
    st.markdown("""
    <div style="display:flex;align-items:center;gap:10px;padding:6px 0 14px 0;border-bottom:1px solid #101c38">
        <div style="width:10px;height:10px;border-radius:50%;background:#1DB584;animation:pulse 2.2s infinite;flex-shrink:0"></div>
        <span style="font-size:18px;font-weight:600;color:#c8ddf8;letter-spacing:-.02em">HIVE</span>
        <span style="font-size:12px;color:#243858;margin-left:2px">· Acoustic Heritage Atlas</span>
    </div>""", unsafe_allow_html=True)

for col, val, label in zip(
    [c2, c3, c4, c5],
    [total, with_audio, conflict_count, lang_count],
    ["Regions", "Soundscapes", "Conflict zones", "Languages"],
):
    with col:
        st.metric(label, val)

st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)

# ─── Filter bar ─────────────────────────────────────────────────────────────
filters = {"all": "All regions", "heritage": "Heritage sites", "conflict": "Conflict relief",
           "language": "Endangered languages", "dialect": "Living dialects", "diaspora": "Diaspora"}

cols = st.columns(len(filters))
for col, (k, v) in zip(cols, filters.items()):
    with col:
        active = st.session_state.active_filter == k
        if st.button(v, key=f"filter_{k}", type="primary" if active else "secondary",
                     use_container_width=True):
            st.session_state.active_filter = k
            st.rerun()

st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)

# ─── Build Map ───────────────────────────────────────────────────────────────
active_filter = st.session_state.active_filter
visible = [d for d in st.session_state.metadata
           if active_filter == "all" or d.get("category") == active_filter]

m = folium.Map(
    location=[25.0, 50.0],
    zoom_start=2,
    tiles="CartoDB dark_matter",
    prefer_canvas=True,
)

for item in visible:
    color = CATEGORY_COLORS.get(item.get("category", "heritage"), "#E8A020")
    is_sel = item["id"] == st.session_state.selected_id
    has_audio = bool(item.get("audio_path"))

    # Outer pulse ring
    folium.CircleMarker(
        location=[item["latitude"], item["longitude"]],
        radius=18 if is_sel else 14,
        color=color,
        fill=True,
        fill_color=color,
        fill_opacity=0.06,
        weight=0,
    ).add_to(m)

    # Mid ring
    folium.CircleMarker(
        location=[item["latitude"], item["longitude"]],
        radius=10 if is_sel else 7,
        color=color,
        fill=True,
        fill_color=color,
        fill_opacity=0.12,
        weight=0,
    ).add_to(m)

    # Main dot
    folium.CircleMarker(
        location=[item["latitude"], item["longitude"]],
        radius=7 if is_sel else 5,
        color="#fff" if is_sel else color,
        fill=True,
        fill_color=color,
        fill_opacity=1.0,
        weight=2 if is_sel else 0,
        tooltip=folium.Tooltip(
            f"<div style='font-family:Inter,sans-serif;background:#06091e;color:#c8ddf8;"
            f"padding:8px 12px;border-radius:8px;border:1px solid #101c38;"
            f"font-size:12px;min-width:140px'>"
            f"<div style='font-weight:600;margin-bottom:2px'>{item['region']}</div>"
            f"<div style='color:#1e3050;font-size:10px'>{item.get('country','')}</div>"
            f"<div style='margin-top:5px;font-size:10px;color:{color}'>"
            f"{CATEGORY_LABELS.get(item.get('category',''),'')}</div>"
            f"{'<div style=\"margin-top:4px;font-size:10px;color:#1DB584\">▶ Soundscape available</div>' if has_audio else ''}"
            f"</div>",
            sticky=False,
        ),
        popup=folium.Popup(item["id"], parse_html=False),
    ).add_to(m)

# ─── Layout: Map + Panel ─────────────────────────────────────────────────────
map_col, panel_col = st.columns([3, 1.6], gap="medium")

with map_col:
    st.markdown("<div class='map-label'>📍 Click any pin to explore · Click empty ocean to add a location</div>",
                unsafe_allow_html=True)
    map_result = st_folium(m, width="100%", height=500, returned_objects=["last_object_clicked_popup", "last_clicked"])

# ─── Handle map click ───────────────────────────────────────────────────────
if map_result:
    clicked_popup = map_result.get("last_object_clicked_popup")
    if clicked_popup and clicked_popup != st.session_state.selected_id:
        st.session_state.selected_id = clicked_popup
        st.rerun()

# ─── Right panel ─────────────────────────────────────────────────────────────
selected = next((d for d in st.session_state.metadata if d["id"] == st.session_state.selected_id), None)
map_click_coords = map_result.get("last_clicked") if map_result else None

with panel_col:
    tab_listen, tab_add = st.tabs(["  🎧  Listen  ", "  ➕  Add location  "])

    with tab_listen:
        if selected:
            color = CATEGORY_COLORS.get(selected.get("category", "heritage"), "#E8A020")
            cat_label = CATEGORY_LABELS.get(selected.get("category",""), "")

            st.markdown(f"""
            <div style='padding:0'>
              <div style='font-size:9px;text-transform:uppercase;letter-spacing:.1em;
                  color:{color};font-weight:600;margin-bottom:5px'>{cat_label} · {selected.get("era","")}</div>
              <div style='font-size:20px;font-weight:300;color:#d0e8ff;letter-spacing:-.02em;
                  line-height:1.15;margin:0 0 3px'>{selected["region"]}</div>
              <div style='font-size:11px;color:#1e3050;margin:0 0 10px'>
                  {selected["country"]} &nbsp;·&nbsp; {selected.get("coords_display","")}</div>
              <div style='font-size:11.5px;color:#2e4a6a;line-height:1.6;margin:0 0 14px'>
                  {selected["description"]}</div>
            </div>""", unsafe_allow_html=True)

            # Waveform viz
            wf_colors = [color] * len(WAVEFORM_HEIGHTS)
            bars_html = "".join(
                f"<div style='flex:1;height:{h}px;background:{color};border-radius:2px 2px 0 0;opacity:{0.3 + (h/46)*0.65}'></div>"
                for h in WAVEFORM_HEIGHTS
            )
            st.markdown(f"""
            <div style='margin-bottom:4px'>
              <div style='font-size:9px;text-transform:uppercase;letter-spacing:.07em;
                  color:#172438;margin-bottom:6px;font-weight:500'>Acoustic waveform archive</div>
              <div style='display:flex;align-items:flex-end;gap:2px;height:44px;
                  padding:0 2px;margin-bottom:4px;overflow:hidden'>{bars_html}</div>
              <div style='font-size:9px;color:#172438'>{selected.get("archive_ref","")}</div>
            </div>""", unsafe_allow_html=True)

            st.divider()

            # Soundmarks
            if selected.get("soundmarks"):
                st.markdown("<div style='font-size:9px;text-transform:uppercase;letter-spacing:.07em;color:#172438;font-weight:500;margin-bottom:6px'>Documented soundmarks</div>",
                            unsafe_allow_html=True)
                for sm in selected["soundmarks"]:
                    alive = sm.get("alive", True)
                    bar_opacity = "0.9" if alive else "0.15"
                    txt_style = "color:#243858" if alive else "color:#172438;text-decoration:line-through;font-style:italic"
                    st.markdown(f"""
                    <div style='display:flex;align-items:center;gap:8px;
                        padding:5px 0;border-bottom:1px solid #0a1428'>
                      <div style='width:3px;height:12px;border-radius:2px;
                          background:{color};opacity:{bar_opacity};flex-shrink:0'></div>
                      <div style='font-size:11px;{txt_style};line-height:1.4'>{sm["text"]}</div>
                    </div>""", unsafe_allow_html=True)

            st.divider()

            # Audio player
            if selected.get("audio_path") and os.path.exists(selected["audio_path"]):
                st.markdown(f"<div style='font-size:9px;text-transform:uppercase;letter-spacing:.07em;color:{color};font-weight:500;margin-bottom:6px'>▶  Soundscape available</div>",
                            unsafe_allow_html=True)
                st.audio(selected["audio_path"])
            else:
                st.markdown(f"""
                <div style='background:#040714;border:1px dashed #101c38;border-radius:8px;
                    padding:14px;text-align:center;margin-top:4px'>
                  <div style='font-size:18px;margin-bottom:6px;opacity:.4'>🎙️</div>
                  <div style='font-size:11px;color:#172438;line-height:1.6'>
                      No audio file yet.<br>
                      <span style='color:{color}'>Switch to Add location</span> to upload one.
                  </div>
                </div>""", unsafe_allow_html=True)

        else:
            st.markdown("""
            <div style='display:flex;flex-direction:column;align-items:center;
                justify-content:center;height:380px;gap:10px;text-align:center'>
              <div style='font-size:28px;opacity:.25'>🌍</div>
              <div style='font-size:12px;color:#1e3050;line-height:1.7'>
                  Click any glowing pin on the map<br>to load its acoustic profile.
              </div>
            </div>""", unsafe_allow_html=True)

    with tab_add:
        # Upload audio to existing selected location
        if selected:
            st.markdown(f"""
            <div style='background:#040714;border:1px solid #101c38;border-radius:8px;
                padding:8px 12px;margin-bottom:12px'>
              <div style='font-size:9px;color:#1e3050;text-transform:uppercase;
                  letter-spacing:.06em;margin-bottom:2px'>Adding audio to selected location</div>
              <div style='font-size:13px;font-weight:500;color:#8aaac8'>{selected["region"]}</div>
            </div>""", unsafe_allow_html=True)

            uploaded = st.file_uploader("Upload soundscape file", type=["mp3","wav","ogg","m4a"],
                                         label_visibility="collapsed",
                                         key="upload_existing")
            if uploaded:
                save_path = f"data/audio/{selected['id']}_{uploaded.name}"
                with open(save_path, "wb") as f:
                    f.write(uploaded.getbuffer())
                for d in st.session_state.metadata:
                    if d["id"] == selected["id"]:
                        d["audio_path"] = save_path
                        break
                with open("data/metadata.json", "w") as f:
                    json.dump([d for d in st.session_state.metadata if d["id"] not in {s["id"] for s in SAMPLE_DATA}], f, indent=2)
                st.success(f"Soundscape uploaded for {selected['region']}")
                st.rerun()

        st.divider()

        # Add new pin from map click
        st.markdown("<div style='font-size:10px;color:#1e3050;margin-bottom:8px'>Or click empty ocean/land on the map to place a new pin, then fill details:</div>",
                    unsafe_allow_html=True)

        if map_click_coords and not map_result.get("last_object_clicked_popup"):
            lat = map_click_coords.get("lat", 0)
            lng = map_click_coords.get("lng", 0)
            st.markdown(f"""
            <div style='background:#040714;border:1px solid #1a3870;border-radius:8px;
                padding:8px 12px;margin-bottom:12px;font-family:monospace;
                font-size:12px;color:#4a8cd4'>
                📍 {lat:.4f}°, {lng:.4f}°
            </div>""", unsafe_allow_html=True)

            with st.form("add_new_form", clear_on_submit=True):
                new_name = st.text_input("Location name", placeholder="e.g. Jaisalmer Fort")
                new_country = st.text_input("Country", placeholder="e.g. India")
                new_cat = st.selectbox("Category",
                    options=list(CATEGORY_COLORS.keys()),
                    format_func=lambda x: CATEGORY_LABELS[x])
                new_desc = st.text_area("Description", placeholder="What sounds define this place?",
                                         height=80)
                new_audio = st.file_uploader("Audio file (optional)", type=["mp3","wav","ogg","m4a"])

                submitted = st.form_submit_button("Add to atlas")
                if submitted and new_name:
                    new_id = f"user_{len(st.session_state.metadata)+1}"
                    audio_path = None
                    if new_audio:
                        audio_path = f"data/audio/{new_id}_{new_audio.name}"
                        with open(audio_path, "wb") as f:
                            f.write(new_audio.getbuffer())

                    new_entry = {
                        "id": new_id,
                        "region": new_name,
                        "country": new_country,
                        "latitude": lat,
                        "longitude": lng,
                        "category": new_cat,
                        "use_case": CATEGORY_LABELS[new_cat],
                        "era": "Present",
                        "description": new_desc,
                        "soundmarks": [],
                        "color": CATEGORY_COLORS[new_cat],
                        "audio_path": audio_path,
                        "archive_ref": "Community contribution",
                        "coords_display": f"{lat:.2f}°N  {abs(lng):.2f}°{'E' if lng>=0 else 'W'}",
                    }
                    st.session_state.metadata.append(new_entry)
                    st.session_state.selected_id = new_id
                    user_entries = [d for d in st.session_state.metadata
                                    if d["id"] not in {s["id"] for s in SAMPLE_DATA}]
                    with open("data/metadata.json", "w") as f:
                        json.dump(user_entries, f, indent=2)
                    st.toast(f"Added {new_name} to the atlas!", icon="🌍")
                    st.rerun()
        else:
            st.markdown("""
            <div style='display:flex;flex-direction:column;align-items:center;
                justify-content:center;height:200px;gap:8px;text-align:center'>
              <div style='font-size:24px;opacity:.25'>🗺️</div>
              <div style='font-size:11px;color:#172438;line-height:1.7'>
                  Click on any empty area of the map<br>to drop a new pin here.
              </div>
            </div>""", unsafe_allow_html=True)

# ─── Bottom: region chips ────────────────────────────────────────────────────
st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
st.markdown("<div style='font-size:9px;text-transform:uppercase;letter-spacing:.07em;color:#101c38;margin-bottom:8px'>All locations in atlas</div>",
            unsafe_allow_html=True)

chips = st.columns(min(len(visible), 8))
for i, item in enumerate(visible[:8]):
    col_idx = i % len(chips)
    color = CATEGORY_COLORS.get(item.get("category","heritage"), "#E8A020")
    with chips[col_idx]:
        is_sel = item["id"] == st.session_state.selected_id
        border = f"1.5px solid {color}" if is_sel else "1px solid #101c38"
        bg = "#040714" if is_sel else "transparent"
        if st.button(
            item["region"],
            key=f"chip_{item['id']}",
            use_container_width=True,
        ):
            st.session_state.selected_id = item["id"]
            st.rerun()
