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

UNSPLASH_ACCESS_KEY = "C1EfwcEnIZxz9pNqnTbQG1TU21Aj9QGmxaTuT8s6YJw"