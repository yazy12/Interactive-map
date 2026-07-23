import os
import pandas as pd
import requests
import streamlit as st
from streamlit_folium import st_folium
import folium
import xml.etree.ElementTree as ET


# Configure wide responsive page alignment matching full-width web frame
st.set_page_config(
    layout="wide",
    page_title="Freedom in Education - School Districts Explorer",
    page_icon="🎓",
)

