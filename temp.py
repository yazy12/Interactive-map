import os
import pandas as pd
import requests
import streamlit as st
from streamlit_folium import st_folium
import folium
import xml.etree.ElementTree as ET

# Configure wide responsive page alignment matching full-width web frame
st.set_page_config(layout="wide", page_title="Freedom in Education - School Districts Explorer")

# --- FREEDOMINED.ORG BRAND COLOR PALETTE ARCHITECTURE ---
COLOR_PRIMARY = "#0B2240"       # Official Deep Navy Hex Blue
COLOR_ACCENT = "#B91C1C"        # Brand Red Core Accent
COLOR_CARD_BG = "#F8FAFC"       # Light Slate Clean Background Canvas
COLOR_BORDER = "#E2E8F0"        # Soft Gray Border Line Accent
COLOR_TEXT_DARK = "#0F172A"     # Deep Onyx Body Text

# --- UNIVERSAL FREEDOM IN EDUCATION WEBSITE STYLE OVERRIDES ---
st.markdown(f"""
    <style>
    /* Universal Font Stack Rule */
    html, body, [data-testid="stWidgetLabel"], .stSelectbox, .stMarkdown, p, h1, h2, h3 {{
        font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif !important;
        color: {COLOR_TEXT_DARK};
    }}
    
    /* Modernized Corporate Content Row Card Frame */
    .brand-board {{
        background-color: #FFFFFF;
        border: 1px solid {COLOR_BORDER};
        padding: 24px;
        border-radius: 6px;
        margin-bottom: 25px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
    }}
    
    /* Segment Title Header matching freedomined.org */
    .brand-header {{
        text-align: left;
        color: {COLOR_PRIMARY};
        font-weight: 700;
        font-size: 22px;
        margin-bottom: 20px;
        border-bottom: 2px solid {COLOR_ACCENT};
        padding-bottom: 8px;
    }}
    
    /* Individual Modernized Flat Informational Metrics blocks */
    .info-card-block {{
        background-color: {COLOR_CARD_BG};
        border-left: 4px solid {COLOR_PRIMARY};
        border-top: 1px solid {COLOR_BORDER};
        border-right: 1px solid {COLOR_BORDER};
        border-bottom: 1px solid {COLOR_BORDER};
        padding: 16px;
        border-radius: 0px 4px 4px 0px;
        color: {COLOR_TEXT_DARK};
        min-height: 190px;
    }}
    
    /* Primary Selection Horizontal Tracker String */
    .brand-path-tracker {{
        background-color: {COLOR_PRIMARY};
        color: #FFFFFF !important;
        padding: 12px 16px;
        border-radius: 4px;
        font-weight: 600;
        font-size: 14px;
        margin-bottom: 20px;
    }}
    
    .block-title {{
        font-weight: 700;
        color: {COLOR_PRIMARY};
        margin-bottom: 10px;
        font-size: 15px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }}
    </style>
""", unsafe_allow_html=True)

UNSPLASH_ACCESS_KEY = "C1EfwcEnIZxz9pNqnTbQG1TU21Aj9QGmxaTuT8s6YJw"

# --- CACHED DATA INGESTION ENGINE ---
@st.cache_data
def load_all_school_data():
    files = {
        "Indiana": "assets/School_Districts_Indiana.csv",
        "Ohio": "assets/School_Districts_Ohio.csv",
        "Illinois": "assets/School_Districts_Illinois.csv",
        "Iowa": "assets/School_Districts_Iowa.csv",
        "Wisconsin": "assets/School_Districts_Wisconsin.csv",
        "Minnesota": "assets/School_Districts_Minnesota.csv",
        "Michigan": "assets/School_Districts_Michigan.csv",
        "Kentucky": "assets/School_Districts_Kentucky.csv",
        "Georgia": "assets/School_Districts_Georgia.csv",
        "Missouri": "assets/School_Districts_Missouri.csv",
        "South Carolina": "assets/School_Districts_South Carolina.csv",
        "North Carolina": "assets/School_Districts_North Carolina.csv",
        "Mississippi": "assets/School_Districts_Mississippi.csv",
        "Alabama": "assets/School_Districts_Alabamia.csv",
        "North Dakota": "assets/School_Districts_North Dakota.csv",
        "South Dakota": "assets/School_Districts_South Dakota.csv",
        "Florida": "assets/School_Districts_Florida.csv",
        "West Virginia": "assets/School_Districts_West Virginia.csv",
        "Maryland": "assets/School_Districts_Maryland.csv",
        "Virginia": "assets/School_Districts_Virginia.csv",
        "Nebraska": "assets/School_Districts_Nebraska.csv",
        "Louisiana": "assets/School_Districts_Louisiana.csv",
        "Tennessee": "assets/School_Districts_Tennessee.csv",
        "Texas": "assets/School_Districts_Texas.csv",
        "New Mexico": "assets/School_Districts_New Mexico.csv",
        "Delaware": "assets/School_Districts_Delaware.csv",
        "New Jersey": "assets/School_Districts_New Jersey.csv",
        "Oklahoma": "assets/School_Districts_Oklahoma copy.csv",
        "Kansas": "assets/School_Districts_Kansas.csv",
        "Pennsylvania": "assets/School_Districts_Pennsylvania.csv",
        "New York State": "assets/School_Districts_New York.csv",
        "Maine": "assets/School_Districts_Maine.csv",
        "Vermont": "assets/School_Districts_Vermont.csv",
        "New Hampshire": "assets/School_Districts_New Hampshire.csv",
        "Massachusetts": "assets/School_Districts_Massachusetts.csv",
        "Alaska": "assets/School_Districts_Alaska.csv",
        "Rhode Island": "assets/School_Districts_Rhode Island.csv",
        "Connecticut": "assets/School_Districts_Connecticut.csv",
        "Arizona": "assets/School_Districts_Arizona.csv",
        "Montana": "assets/School_Districts_Montana.csv",
        "Nevada": "assets/School_Districts_Nevada.csv",
        "Idaho": "assets/School_Districts_Idaho.csv",
        "Oregon": "assets/School_Districts_Oregon.csv",
        "Wyoming": "assets/School_Districts_Wyoming.csv",
        "Washington State": "assets/School_Districts_Washington.csv",
        "Utah": "assets/School_Districts_Utah.csv",
        "Colorado": "assets/School_Districts_Colorado.csv",
        "Arkansas": "assets/School_Districts_Arkansas.csv",
        "California": "assets/School_Districts_California.csv",
        "Hawaii": "assets/School_Districts_Hawaii.csv"
    }
    
    frames = []
    for state, filename in files.items():
        if os.path.exists(filename):
            df = pd.read_csv(filename)
            df["State"] = state
            frames.append(df)
            
    if frames:
        data = pd.concat(frames, ignore_index=True)
    else:
        data = pd.DataFrame(columns=["School District", "City", "County", "State"])
        
    for col in data.columns:
        if data[col].dtype == "object":
            data[col] = data[col].str.strip()
            
    stats_data = pd.read_csv("State EDU Stats.csv") if os.path.exists("State EDU Stats.csv") else pd.DataFrame()
    if not stats_data.empty and "State" in stats_data.columns:
        stats_data["State"] = stats_data["State"].str.strip()
        
    report_cards_data = pd.read_csv("State Report Cards.csv") if os.path.exists("State Report Cards.csv") else pd.DataFrame()
    if not report_cards_data.empty and "State" in report_cards_data.columns:
        report_cards_data["State"] = report_cards_data["State"].str.strip()
        report_cards_data.columns = report_cards_data.columns.str.strip()
        
    return data, stats_data, report_cards_data

@st.cache_data
def fetch_news_headlines(state_name):
    try:
        query = f"K-12 Education {state_name}"
        url = f"https://news.google.com/rss/search?q={query}&hl=en-US&gl=US&ceid=US:en"
        response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=5)
        if response.status_code == 200:
            root_xml = ET.fromstring(response.content)
            items = []
            for item in root_xml.findall(".//item")[:8]:
                title = item.find("title").text
                link = item.find("link").text
                if " - " in title:
                    title = title.rsplit(" - ", 1)[0]
                items.append({"title": title, "link": link})
            return items
    except Exception:
        pass
    return [{"title": "No recent local education articles found.", "link": "#"}]

@st.cache_data
def fetch_unsplash_image(state_name):
    try:
        url = f"https://api.unsplash.com/search/photos?query={state_name} K-12 schools&per_page=1"
        headers = {"Authorization": f"Client-ID {UNSPLASH_ACCESS_KEY}"}
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code == 200:
            results = response.json().get("results")
            if results:
                return results[0]["urls"]["regular"]
    except Exception:
        pass
    return None

@st.cache_data
def fetch_boundary_data(query):
    try:
        url = f"https://nominatim.openstreetmap.org/search?q={query}&format=json&polygon_geojson=1&limit=1"
        headers = {"User-Agent": "freedom_in_education_explorer_web_v4"}
        res = requests.get(url, headers=headers, timeout=5).json()
        if res:
            lat = float(res[0].get("lat"))
            lon = float(res[0].get("lon"))
            geojson = res[0].get("geojson", None)
            return lat, lon, geojson
    except Exception:
        pass
    return 40.0, -84.5, None

# --- EXECUTE INGESTION ---
data, stats_data, report_cards_data = load_all_school_data()

# --- TOP HEADER BANNER ---
log_col, title_col = st.columns([1, 6])
with log_col:
    logo_filename = "FIE_LOGO-WHITE-1.png"
    if os.path.exists(logo_filename):
        st.image(logo_filename, width=130)
with title_col:
    st.markdown(
        f'<h1 style="color:{COLOR_PRIMARY}; margin:0; padding-top:12px; font-weight:700; font-size:34px;">Freedom in Education</h1>'
        f'<p style="color:#64748B; margin:2px 0 0 0; font-size:16px; font-weight: 500;">Building Academic Excellence in America\'s Classrooms</p>',
        unsafe_allow_html=True
    )

st.write("---")

# --- WORKSPACE SIDE-BY-SIDE PANELS ---
col_left, col_right = st.columns([4, 3])

with col_left:
    st.markdown(f'<div class="brand-header">School Districts Explorer Search</div>', unsafe_allow_html=True)
    
    # Select State Dropdown
    state_list = sorted(data["State"].unique()) if not data.empty else []
    selected_state = st.selectbox("1. SELECT STATE", ["-- Choose a State --"] + state_list)
    
    # Select County Dropdown
    county_list = []
    if selected_state != "-- Choose a State --":
        county_list = sorted(data[data["State"] == selected_state]["County"].unique())
    selected_county = st.selectbox("2. SELECT COUNTY", ["-- Choose a County --"] + county_list, disabled=(selected_state == "-- Choose a State --"))
    
    # Select District Dropdown
    district_list = []
    if selected_county != "-- Choose a County --":
        district_list = sorted(data[(data["State"] == selected_state) & (data["County"] == selected_county)]["School District"].unique())
    selected_district = st.selectbox("3. SCHOOL DISTRICTS", ["-- Choose a District --"] + district_list, disabled=(selected_county == "-- Choose a County --"))

with col_right:
    st.markdown(f'<div class="brand-header">Interactive Regional Map</div>', unsafe_allow_html=True)
    
    # Center Targets Map configurations
    map_lat, map_lon = 40.0, -84.5
    zoom_lvl = 5
    geojson_layer = None
    marker_label = None
    outline_color = COLOR_PRIMARY
    weight_thickness = 3
    
    if selected_district != "-- Choose a District --":
        row = data[(data["State"] == selected_state) & (data["County"] == selected_county) & (data["School District"] == selected_district)]
        if not row.empty:
            city_name = row.iloc[0]["City"]
            map_lat, map_lon, _ = fetch_boundary_data(f"{city_name}, {selected_state}, USA")
            zoom_lvl = 11
            marker_label = f"{selected_district} ({city_name})"
    elif selected_county != "-- Choose a County --":
        map_lat, map_lon, geojson_layer = fetch_boundary_data(f"{selected_county} County, {selected_state}, USA")
        zoom_lvl = 9
        outline_color = COLOR_ACCENT
        weight_thickness = 2
    elif selected_state != "-- Choose a State --":
        map_lat, map_lon, geojson_layer = fetch_boundary_data(f"{selected_state}, USA")
        zoom_lvl = 6
        outline_color = COLOR_PRIMARY
        weight_thickness = 3

    m = folium.Map(location=[map_lat, map_lon], zoom_start=zoom_lvl, control_scale=True)
    
    # Dynamically project outline boundaries matching original feature set
    if geojson_layer:
        folium.GeoJson(
            geojson_layer,
            style_function=lambda x, color=outline_color, wt=weight_thickness: {
                "fillColor": "transparent",
                "color": color,
                "weight": wt,
                "fillOpacity": 0.0
            }
        ).add_to(m)
        
    if marker_label:
        folium.Marker([map_lat, map_lon], popup=marker_label, tooltip=marker_label).add_to(m)
        
    st_folium(m, width="100%", height=320, key="folium_map")

# --- CENTRAL ANALYSIS PANEL SYSTEM ---
st.write("---")

path_text = "Select a state, county, and district to visualize administrative metrics."
grade_note = "No state selected yet."
finance_note = "No state selected yet."
testing_note = "No state selected yet."
summary_note = "No state selected yet."

if selected_state != "-- Choose a State --":
    path_text = f"Selected Region: {selected_state}"
    if selected_county != "-- Choose a County --":
        path_text += f"   •   County: {selected_county}"
    if selected_district != "-- Choose a District --":
        row = data[(data["State"] == selected_state) & (data["County"] == selected_county) & (data["School District"] == selected_district)]
        if not row.empty:
            path_text = f"District: {selected_district}   •   City: {row.iloc[0]['City']}   •   County: {selected_county}   •   State: {selected_state}"

    if not stats_data.empty:
        st_row = stats_data[stats_data["State"] == selected_state]
        if not st_row.empty:
            r = st_row.iloc[0]
            finance_note = f"• Students: {r.get('Number of students', 'N/A')}<br>• Spending/Pupil: {r.get('Per-pupil spending', 'N/A')}<br>• Grad Rate: {r.get('Graduation rate', 'N/A')}"
            testing_note = f"• 8th Math Score: {r.get('Average scale score (8th math)', 'N/A')}<br>• 4th Reading Score: {r.get('Average scale score (4th reading)', 'N/A')}<br>• Avg SAT Score: {r.get('Average SAT score', 'N/A')}<br>• Avg ACT Score: {r.get('Average ACT score', 'N/A')}"

    if not report_cards_data.empty:
        rc_row = report_cards_data[report_cards_data["State"] == selected_state]
        if not rc_row.empty:
            rc = rc_row.iloc[0]
            grade_note = f"• Math Performance: {rc.get('Math Grade', 'N/A')}<br>• English / Lang: {rc.get('English Grade', 'N/A')}<br>• College Readiness: {rc.get('College Readiness Grade', 'N/A')}<br>• Parental Rights: {rc.get('Parental Rights', 'N/A')}"
            summary_note = f"{rc.get('Description', 'N/A')}"

# Render modern clean structure corresponding to Freedom in Education presentation parameters
st.markdown(f"""
    <div class="brand-board">
        <div class="brand-header">District Analytics Dashboard</div>
        <div class="brand-path-tracker">📍 {path_text}</div>
        <div style="display: flex; gap: 16px; flex-wrap: wrap;">
            <div style="flex: 1; min-width: 240px;" class="info-card-block">
                <div class="block-title">Academic Grades</div>
                <div style="font-size: 14px; line-height: 1.6;">{grade_note}</div>
            </div>
            <div style="flex: 1; min-width: 240px;" class="info-card-block">
                <div class="block-title">Enrollment & Finance</div>
                <div style="font-size: 14px; line-height: 1.6;">{finance_note}</div>
            </div>
            <div style="flex: 1; min-width: 240px;" class="info-card-block">
                <div class="block-title">Testing Metrics</div>
                <div style="font-size: 14px; line-height: 1.6;">{testing_note}</div>
            </div>
            <div style="flex: 1; min-width: 240px;" class="info-card-block">
                <div class="block-title">Analysis Summary</div>
                <div style="font-size: 14px; line-height: 1.5;">{summary_note}</div>
            </div>
        </div>
    </div>
""", unsafe_allow_html=True)

if selected_state != "-- Choose a State --":
    img_url = fetch_unsplash_image(selected_state)
    if img_url:
        st.image(img_url, width=520, caption=f"Regional Snapshot Representation: {selected_state}")

# --- RSS TIMELINE NEWS TIMELINE ---
st.write("---")
st.markdown(f'<div class="brand-header">Local Education Headlines & Field Reports</div>', unsafe_allow_html=True)

if selected_state != "-- Choose a State --":
    headlines = fetch_news_headlines(selected_state)
    for h in headlines:
        st.markdown(f"📰 **[{h['title']}]({h['link']})**")
else:
    st.info("Select an active administrative state map filter above to pull recent education notifications.")