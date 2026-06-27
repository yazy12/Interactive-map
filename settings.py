import os
import threading
import pandas as pd
import tkinter as tk
from tkinter import messagebox, ttk
import tkintermapview
from geopy.geocoders import Nominatim
from PIL import Image, ImageTk
import requests
import xml.etree.ElementTree as ET  # <-- Added for RSS parsing
import webbrowser                  # <-- Added to let users click and read full articles

# Branding Hex Colors - Freedom in Education Theme
COLOR_PRIMARY = "#0B2240"     # Deep Navy
COLOR_SECONDARY = "#C8102E"   # Bright Crimson Accent
COLOR_BG_LIGHT = "#F4F6F8"    # Soft Off-White
COLOR_TEXT_DARK = "#1E293B"   # Charcoal Slate
COLOR_LIST_BG = "#FFFFFF"     # Clean White Canvas
COLOR_SELECT_BG = "#E2E8F0"   # Soft Gray Focus Highlight
