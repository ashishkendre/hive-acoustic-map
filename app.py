import streamlit as st
import folium
from streamlit_folium import st_folium
import json
import os

# --- 1. Page Configuration & Custom CSS ---
st.set_page_config(page_title="HIVE | Acoustic Heritage Platform", page_icon="🎙️", layout="wide")

st.markdown("""
    <style>
    /* Clean up default Streamlit clutter */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .block-container { padding-top: 2rem; padding-bottom: 0rem; }
    
    /* Button styling */
    div.stButton > button:first-child {
        background-color: #FFC107;
        color: #000000;
        border-radius: 8px;
        border: none;
        font-weight: bold;
        transition: all 0.3s ease-in-out;
    }
    div.stButton > button:first-child:hover {
        background-color: #FFA000;
        transform: scale(1.02);
    }
    
    /* Upload form styling */
    [data-testid="stForm"] {
        background-color: #F8F9FA;
        border-radius: 10px;
        padding: 20px;
        border: 1px solid #E0E0E0;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🎙️ HIVE: Global Acoustic Map")
st.markdown("_Mapping and preserving humanity's oral histories, dialects, and tonal diversity._")
st.markdown("---")

AUDIO_DIR = "data/audio/"
os.makedirs(AUDIO_DIR, exist_ok=True)

# --- 2. Load Data ---
@st.cache_data(show_spinner=False)
def load_data():
    if not os.path.exists("data/metadata.json"):
        return []
    with open("data/metadata.json", "r") as f:
        return json.load(f)

metadata = load_data()

# --- 3. UI Layout ---
col1, col2 = st.columns([2.5, 1], gap="large")

with col1:
    st.markdown("##### 📍 Interactive Explorer")
    m = folium.Map(location=[25.0, 50.0], zoom_start=3, tiles="CartoDB dark_matter")

    for item in metadata:
        folium.CircleMarker(
            location=[item["latitude"], item["longitude"]],
            radius=9,
            color="#FFA000",
            fill=True,
            fill_color="#FFC107",
            fill_opacity=0.8,
            tooltip=f"<b style='font-size:14px;'>{item['region']}</b>",
            popup=item["id"] 
        ).add_to(m)

    map_data = st_folium(m, width=800, height=550)

with col2:
    # --- The Fix: Using Tabs ---
    tab1, tab2 = st.tabs(["🎧 Listen", "➕ Contribute"])
    
    # Capture map interactions safely
    marker_click = map_data.get("last_object_clicked_popup") if map_data else None
    map_click = map_data.get("last_clicked") if map_data else None

    # TAB 1: Listening to Existing Data
    with tab1:
        if marker_click:
            selected_data = next((item for item in metadata if item["id"] == marker_click), None)
            if selected_data:
                st.success(f"**Region Loaded:** {selected_data['region']}")
                st.markdown(f"> *{selected_data['description']}*")
                st.audio(selected_data["audio_path"], format="audio/mp3")
        else:
            st.info("👈 Select a golden marker on the map to listen to a soundscape.")

    # TAB 2: Uploading New Data
    with tab2:
        if map_click:
            lat, lng = map_click["lat"], map_click["lng"]
            st.write(f"**Selected Coordinates:** {lat:.4f}, {lng:.4f}")
            
            with st.form("upload_form", clear_on_submit=True):
                new_region = st.text_input("Region Name (e.g., Kyoto, Japan)")
                new_desc = st.text_area("Description of Dialect/Tonality")
                uploaded_file = st.file_uploader("Upload Regional Audio (.mp3, .wav)", type=["mp3", "wav"])
                
                submit_button = st.form_submit_button("Deploy to Network")
                
                if submit_button and uploaded_file and new_region:
                    file_path = os.path.join(AUDIO_DIR, uploaded_file.name)
                    with open(file_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    
                    new_entry = {
                        "id": f"upload_{len(metadata)+1}",
                        "region": new_region,
                        "latitude": lat,
                        "longitude": lng,
                        "description": new_desc,
                        "audio_path": file_path
                    }
                    metadata.append(new_entry)
                    
                    with open("data/metadata.json", "w") as f:
                        json.dump(metadata, f, indent=4)
                        
                    st.toast(f"Successfully added {new_region}!", icon="🎉")
                    st.cache_data.clear()
                    st.rerun()
        else:
            st.info("👈 Click anywhere on the empty map to get coordinates and unlock the upload form.")