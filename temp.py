import os
import pandas as pd
import requests
import streamlit as st
from streamlit_folium import st_folium
import folium
import xml.etree.ElementTree as ET
import altair as alt

# --- FREEDOMINED.ORG BRAND DESIGN TOKENS ---
COLOR_PRIMARY = "#0B2240"        # Deep Navy
COLOR_PRIMARY_LIGHT = "#3164A5"  # Lighter navy for unselected bars
COLOR_ACCENT = "#B91C1C"         # Brand Red for selected/highlighted bar
COLOR_ACCENT_SOFT = "#FEE2E2"    # Soft red tint
COLOR_CARD_BG = "#F8FAFC"        # Light slate background
COLOR_PAGE_BG = "#FFFFFF"        # Page background
COLOR_BORDER = "#E2E8F0"         # Soft gray border
COLOR_TEXT_DARK = "#0F172A"      # Body text
COLOR_TEXT_MUTED = "#64748B"     # Secondary / muted text

# Configure wide responsive page alignment matching full-width web frame
st.set_page_config(
    layout="wide",
    page_title="Freedom in Education - School Districts Explorer",
    page_icon="🎓",
)

# =====================================================================
# GLOBAL STYLES
# =====================================================================
st.markdown(f"""
    <style>
    /* ---------- Base typography ---------- */
    html, body, [class*="css"] {{
        font-family: "Inter", "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
    }}
    [data-testid="stWidgetLabel"], .stMarkdown, p, h1, h2, h3 {{
        color: {COLOR_TEXT_DARK};
    }}
    .block-container {{
        padding-top: 1.5rem;
        padding-bottom: 3rem;
        max-width: 1300px;
    }}

    /* ---------- Header styles ---------- */
    .brand-header {{
        color: {COLOR_PRIMARY};
        font-weight: 700;
        font-size: 19px;
        margin-bottom: 12px;
        padding-bottom: 8px;
        border-bottom: 1px solid {COLOR_BORDER};
    }}

    /* ---------- Breadcrumb / selection tracker ---------- */
    .brand-path-tracker {{
        background: linear-gradient(90deg, {COLOR_PRIMARY} 0%, {COLOR_PRIMARY_LIGHT} 100%);
        color: #FFFFFF;
        padding: 12px 18px;
        border-radius: 8px;
        font-weight: 600;
        font-size: 14px;
        margin-bottom: 20px;
        letter-spacing: 0.2px;
    }}

    /* ---------- Metric / info cards ---------- */
    .info-card-block {{
        background-color: {COLOR_CARD_BG};
        border: 1px solid {COLOR_BORDER};
        border-top: 3px solid {COLOR_PRIMARY};
        padding: 18px 18px 20px 18px;
        border-radius: 8px;
        color: {COLOR_TEXT_DARK};
        min-height: 175px;
        transition: box-shadow 0.15s ease, transform 0.15s ease;
    }}
    .info-card-block:hover {{
        box-shadow: 0 6px 16px rgba(15, 23, 42, 0.08);
        transform: translateY(-1px);
    }}
    .info-card-block .block-title {{
        font-weight: 700;
        color: {COLOR_PRIMARY};
        margin-bottom: 10px;
        font-size: 13px;
        text-transform: uppercase;
        letter-spacing: 0.6px;
    }}
    .info-card-block .block-subtitle {{
        font-weight: 600;
        color: {COLOR_PRIMARY_LIGHT};
        margin-bottom: 8px;
        font-size: 12px;
    }}
    .info-card-block .block-body {{
        font-size: 14px;
        line-height: 1.7;
        color: {COLOR_TEXT_DARK};
    }}
    .info-card-block .block-empty {{
        font-size: 13px;
        color: {COLOR_TEXT_MUTED};
        font-style: italic;
    }}

    /* ---------- News cards ---------- */
    .news-card {{
        display: block;
        background-color: {COLOR_PAGE_BG};
        border: 1px solid {COLOR_BORDER};
        border-radius: 8px;
        padding: 14px 16px;
        margin-bottom: 10px;
        text-decoration: none !important;
        transition: box-shadow 0.15s ease, border-color 0.15s ease;
    }}
    .news-card:hover {{
        border-color: {COLOR_PRIMARY};
        box-shadow: 0 4px 12px rgba(15, 23, 42, 0.06);
    }}
    .news-card .news-title {{
        color: {COLOR_TEXT_DARK};
        font-weight: 600;
        font-size: 14.5px;
        line-height: 1.5;
    }}
    .news-tag {{
        display: inline-block;
        background-color: {COLOR_ACCENT_SOFT};
        color: {COLOR_ACCENT};
        font-size: 11px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.4px;
        padding: 2px 8px;
        border-radius: 999px;
        margin-right: 8px;
    }}

    /* ---------- Streamlit widget polish ---------- */
    div[data-baseweb="select"] > div {{
        border-radius: 6px !important;
        border-color: {COLOR_BORDER} !important;
    }}
    hr {{
        border-color: {COLOR_BORDER} !important;
        margin: 28px 0 !important;
    }}
    </style>
""", unsafe_allow_html=True)


# =====================================================================
# DATA INGESTION
# =====================================================================
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
        "Hawaii": "assets/School_Districts_Hawaii.csv",
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
def load_grades_methodology():
    filename = "map_grades_methodology.csv"
    if os.path.exists(filename):
        return pd.read_csv(filename)
    return pd.DataFrame()


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
    return []


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


# Helper to clean numeric values from CSV strings
def parse_numeric(val):
    try:
        if pd.isna(val):
            return None
        clean_str = str(val).replace(",", "").replace("%", "").replace("$", "").strip()
        return float(clean_str)
    except (ValueError, TypeError):
        return None


# =====================================================================
# LOAD DATA
# =====================================================================
data, stats_data, report_cards_data = load_all_school_data()
methodology_df = load_grades_methodology()

# =====================================================================
# HEADER
# =====================================================================
with st.container():
    log_col, title_col = st.columns([1, 12])
    
    with title_col:
        st.markdown(
            f'<h1 style="color:{COLOR_PRIMARY}; margin:0; font-weight:800; font-size:30px; letter-spacing:-0.5px;">'
            f'Freedom in Education</h1>'
            f'<p style="color:{COLOR_TEXT_MUTED}; margin:2px 0 0 0; font-size:15px; font-weight:500;">'
            f'Building Academic Excellence in America\'s Classrooms</p>',
            unsafe_allow_html=True,
        )

st.divider()

if data.empty:
    st.warning("No school district data files were found in the `assets/` folder. Add the source CSVs to populate the explorer.")

# =====================================================================
# SEARCH + MAP PANELS
# =====================================================================
col_left, col_right = st.columns([4, 3], gap="large")

with col_left:
    with st.container(border=True):
        st.markdown('<div class="brand-header">🔍 School Districts Explorer Search</div>', unsafe_allow_html=True)

        state_list = sorted(data["State"].unique()) if not data.empty else []
        selected_state = st.selectbox("State", ["-- Choose a State --"] + state_list)

        county_list = []
        if selected_state != "-- Choose a State --":
            county_list = sorted(data[data["State"] == selected_state]["County"].unique())
        selected_county = st.selectbox(
            "County", ["-- Choose a County --"] + county_list,
            disabled=(selected_state == "-- Choose a State --"),
        )

        district_list = []
        if selected_county != "-- Choose a County --":
            district_list = sorted(
                data[(data["State"] == selected_state) & (data["County"] == selected_county)]["School District"].unique()
            )
        selected_district = st.selectbox(
            "School District", ["-- Choose a District --"] + district_list,
            disabled=(selected_county == "-- Choose a County --"),
        )

with col_right:
    with st.container(border=True):
        st.markdown('<div class="brand-header">🗺️ Interactive Regional Map</div>', unsafe_allow_html=True)

        map_lat, map_lon = 40.0, -84.5
        zoom_lvl = 5
        geojson_layer = None
        marker_label = None
        outline_color = COLOR_PRIMARY
        weight_thickness = 3

        with st.spinner("Loading map region..."):
            if selected_district != "-- Choose a District --":
                row = data[
                    (data["State"] == selected_state)
                    & (data["County"] == selected_county)
                    & (data["School District"] == selected_district)
                ]
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

        m = folium.Map(location=[map_lat, map_lon], zoom_start=zoom_lvl, control_scale=True, tiles="CartoDB positron")

        if geojson_layer:
            folium.GeoJson(
                geojson_layer,
                style_function=lambda x, color=outline_color, wt=weight_thickness: {
                    "fillColor": "transparent",
                    "color": color,
                    "weight": wt,
                    "fillOpacity": 0.0,
                },
            ).add_to(m)

        if marker_label:
            folium.Marker([map_lat, map_lon], popup=marker_label, tooltip=marker_label, icon=folium.Icon(color="red", icon="info-sign")).add_to(m)

        st_folium(m, width="100%", height=320, key="folium_map")

# =====================================================================
# ANALYTICS DASHBOARD
# =====================================================================
path_text = "Select a state, county, and district to visualize administrative metrics."
grade_note = None
finance_note = None
testing_note = None
summary_note = None

if selected_state != "-- Choose a State --":
    path_text = f"Selected Region: {selected_state}"
    if selected_county != "-- Choose a County --":
        path_text += f"  •  County: {selected_county}"
    if selected_district != "-- Choose a District --":
        row = data[
            (data["State"] == selected_state)
            & (data["County"] == selected_county)
            & (data["School District"] == selected_district)
        ]
        if not row.empty:
            path_text = (
                f"District: {selected_district}  •  City: {row.iloc[0]['City']}  •  "
                f"County: {selected_county}  •  State: {selected_state}"
            )

    if not stats_data.empty:
        st_row = stats_data[stats_data["State"] == selected_state]
        if not st_row.empty:
            raw_stats_row = st_row.iloc[0]
            finance_note = (
                f"• Students: {raw_stats_row.get('Number of students', 'N/A')}<br>"
                f"• Spending/Pupil: {raw_stats_row.get('Per-pupil spending', 'N/A')}<br>"
                f"• Grad Rate: {raw_stats_row.get('Graduation rate', 'N/A')}"
            )
            testing_note = (
                f"• 8th Math Score: {raw_stats_row.get('Average scale score (8th math)', 'N/A')}<br>"
                f"• 4th Reading Score: {raw_stats_row.get('Average scale score (4th reading)', 'N/A')}<br>"
                f"• Avg SAT Score: {raw_stats_row.get('Average SAT score', 'N/A')}<br>"
                f"• Avg ACT Score: {raw_stats_row.get('Average ACT score', 'N/A')}"
            )

    if not report_cards_data.empty:
        rc_row = report_cards_data[report_cards_data["State"] == selected_state]
        if not rc_row.empty:
            rc = rc_row.iloc[0]
            grade_note = (
                f"• Math Performance: {rc.get('Math Grade', 'N/A')}<br>"
                f"• English Performance: {rc.get('English Grade', 'N/A')}<br>"
                f"• College Readiness: {rc.get('College Readiness Grade', 'N/A')}<br>"
                f"• Parental Rights: {rc.get('Parental Rights', 'N/A')}"
            )
            summary_note = f"{rc.get('Description', 'N/A')}"


def render_card(title, body_html, subtitle=None):
    subtitle_html = f'<div class="block-subtitle">{subtitle}</div>' if subtitle else ""
    if body_html:
        inner = f'{subtitle_html}<div class="block-body">{body_html}</div>'
    else:
        inner = '<div class="block-empty">No data available for this selection yet.</div>'
    return (
        '<div style="flex: 1; min-width: 240px;" class="info-card-block">'
        f'<div class="block-title">{title}</div>{inner}'
        '</div>'
    )


with st.container(border=True):
    st.markdown('<div class="brand-header">📊 District Analytics Dashboard</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="brand-path-tracker">📍 {path_text}</div>', unsafe_allow_html=True)
    
    # 4 Metric Cards Layout
    st.markdown(
        f"""
        <div style="display: flex; gap: 16px; flex-wrap: wrap; margin-bottom: 16px;">
            {render_card("Academic Grades", grade_note)}
            {render_card("Enrollment &amp; Finance", finance_note)}
            {render_card("Testing Metrics", testing_note)}
            {render_card("Analysis Summary", summary_note)}
        </div>
        """,
        unsafe_allow_html=True,
    )

    # --- DASHBOARD TOGGLES ---
    toggle_col1, toggle_col2 = st.columns(2)
    
    with toggle_col1:
        show_graphs = st.toggle("📈 View All-States Comparative Charts", disabled=(selected_state == "-- Choose a State --"))
    
    with toggle_col2:
        show_methodology = st.toggle("📋 View Academic Grades Methodology")

    # --- ACADEMIC GRADES METHODOLOGY PANEL ---
    if show_methodology:
        st.markdown("<hr style='margin: 16px 0 !important;'>", unsafe_allow_html=True)
        st.subheader("📋 Academic Grades Methodology")
        st.caption("How performance, readiness, and policy grades are standardized and evaluated across states.")

        if not methodology_df.empty:
            cards_html = []
            cols = list(methodology_df.columns)
            for col in cols:
                sub_label = str(methodology_df[col].iloc[0]) if len(methodology_df) > 0 else ""
                desc = str(methodology_df[col].iloc[1]) if len(methodology_df) > 1 else ""
                cards_html.append(render_card(col, desc, subtitle=sub_label))

            st.markdown(
                f"""
                <div style="display: flex; gap: 16px; flex-wrap: wrap; margin-top: 12px;">
                    {"".join(cards_html)}
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            st.info("Methodology file `map_grades_methodology.csv` not found or empty.")

    # --- ALL-STATES BAR GRAPH COMPARISON ---
    if show_graphs and not stats_data.empty:
        st.markdown("<hr style='margin: 16px 0 !important;'>", unsafe_allow_html=True)
        st.subheader("📊 State-by-State Educational Comparisons")
        st.caption(f"All state metrics plotted below. **{selected_state}** is highlighted in **Red**.")

        # Prepare dataset for chart rendering
        chart_df = stats_data.copy()
        
        metrics = {
            "Average scale score (8th math)": "8th Grade Math Score",
            "Average scale score (4th reading)": "4th Grade Reading Score",
            "Average SAT score": "Average SAT Score",
            "Average ACT score": "Average ACT Score"
        }

        # Select target metric to view
        selected_metric_col = st.selectbox("Select Benchmark Metric to Plot", list(metrics.keys()), format_func=lambda x: metrics[x])

        # Clean values for selected metric
        chart_df["Value"] = chart_df[selected_metric_col].apply(parse_numeric)
        chart_df = chart_df.dropna(subset=["Value"])

        if not chart_df.empty:
            # Highlight Logic in Altair
            bar_chart = (
                alt.Chart(chart_df)
                .mark_bar()
                .encode(
                    x=alt.X("State:N", sort="-y", title="State"),
                    y=alt.Y("Value:Q", title=metrics[selected_metric_col]),
                    color=alt.condition(
                        alt.datum.State == selected_state,
                        alt.value(COLOR_ACCENT),       # Highlight selected state in Red
                        alt.value(COLOR_PRIMARY_LIGHT)  # Default all other states to Navy Blue
                    ),
                    tooltip=["State", alt.Tooltip("Value:Q", title=metrics[selected_metric_col])]
                )
                .properties(height=380)
            )

            st.altair_chart(bar_chart, use_container_width=True)
        else:
            st.info("No valid numeric data found across states for this metric.")

# =====================================================================
# NEWS / FIELD REPORTS
# =====================================================================
with st.container(border=True):
    st.markdown('<div class="brand-header">📰 Local Education Headlines &amp; Field Reports</div>', unsafe_allow_html=True)

    if selected_state != "-- Choose a State --":
        with st.spinner("Fetching recent headlines..."):
            headlines = fetch_news_headlines(selected_state)
        if headlines:
            for h in headlines:
                st.markdown(
                    f'<a class="news-card" href="{h["link"]}" target="_blank">'
                    f'<span class="news-tag">{selected_state}</span>'
                    f'<span class="news-title">{h["title"]}</span>'
                    f'</a>',
                    unsafe_allow_html=True,
                )
        else:
            st.markdown('<div class="block-empty">No recent local education articles found for this state.</div>', unsafe_allow_html=True)
    else:
        st.info("Select a state above to pull recent education headlines for that region.")