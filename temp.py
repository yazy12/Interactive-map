from settings import *

class ModernSchoolArchiveApp:

    def __init__(self, root):
        self.root = root
        self.root.title("Freedom in Education - School Districts Explorer")
        self.root.geometry("1280x950")  # Bumped height slightly to gracefully host the news card
        self.root.configure(bg=COLOR_BG_LIGHT)

        # Configure Universal Style Architecture
        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.configure_styles()

        # Initialize geolocator for finding lat/lon of cities
        self.geolocator = Nominatim(user_agent="freedom_in_education_explorer_v4")

        # --- LOCAL PERFORMANCE CACHE SYSTEM ---
        self.boundary_cache = {}  
        self.marker_cache = {}    

        # Track active map geometry elements to clear them on new selections
        self.current_marker = None
        self.current_polygon = None
        self.news_urls = []  # <-- Tracks raw web links matching listbox indices

        # Load data from CSVs
        self.load_data()

        # Create Layout
        self.create_widgets()

    def configure_styles(self):
        """Builds custom flattened layouts to eradicate 90s style beveling."""
        self.style.configure(".", background=COLOR_BG_LIGHT, foreground=COLOR_TEXT_DARK)
        
        # Label Frames
        self.style.configure(
            "TLabelframe", 
            background=COLOR_LIST_BG, 
            relief="flat", 
            borderwidth=1, 
            bordercolor="#CBD5E1"
        )
        self.style.configure(
            "TLabelframe.Label", 
            font=("Segoe UI", 10, "bold"), 
            foreground=COLOR_PRIMARY, 
            background=COLOR_LIST_BG
        )

        # Scrollbars
        self.style.configure(
            "Vertical.TScrollbar", 
            gripcount=0, 
            background="#CBD5E1", 
            troughcolor=COLOR_BG_LIGHT, 
            borderwidth=0, 
            arrowsize=12
        )
        
        # Custom Button Style for Clear/Deselect action
        self.style.configure(
            "Clear.TButton",
            font=("Segoe UI Semibold", 9),
            background=COLOR_BG_LIGHT,
            foreground=COLOR_TEXT_DARK,
            borderwidth=1,
            relief="flat",
            padding=5
        )
        self.style.map(
            "Clear.TButton",
            background=[("active", COLOR_SELECT_BG), ("pressed", "#CBD5E1")],
            foreground=[("active", COLOR_PRIMARY)]
        )

    def load_data(self):
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
            else:
                print(f"Warning: {filename} was not found in the current folder.")

        if frames:
            self.data = pd.concat(frames, ignore_index=True)
        else:
            self.data = pd.DataFrame(columns=["School District", "City", "County", "State"])

        for col in self.data.columns:
            if self.data[col].dtype == "object":
                self.data[col] = self.data[col].str.strip()

        stats_file = "State EDU Stats.csv"
        if os.path.exists(stats_file):
            self.stats_data = pd.read_csv(stats_file)
            if "State" in self.stats_data.columns:
                self.stats_data["State"] = self.stats_data["State"].str.strip()
        else:
            self.stats_data = pd.DataFrame()
            print("Warning: State EDU Stats.csv was not found in the current folder.")

        # Load Report Cards Data
        report_cards_file = "State Report Cards.csv"
        if os.path.exists(report_cards_file):
            self.report_cards_data = pd.read_csv(report_cards_file)
            if "State" in self.report_cards_data.columns:
                self.report_cards_data["State"] = self.report_cards_data["State"].str.strip()
            # Clean up potential leading/trailing spaces in the column headers
            self.report_cards_data.columns = self.report_cards_data.columns.str.strip()
        else:
            self.report_cards_data = pd.DataFrame()
            print("Warning: State Report Cards.csv was not found in the current folder.")

    def create_widgets(self):
        # --- TOP HEADER BANNER ---
        header_frame = tk.Frame(self.root, bg=COLOR_PRIMARY, height=130)
        header_frame.pack(fill=tk.X, side=tk.TOP)
        header_frame.pack_propagate(False)

        center_container = tk.Frame(header_frame, bg=COLOR_PRIMARY)
        center_container.pack(side=tk.LEFT, fill=tk.Y, padx=30)

        logo_filename = "FIE_LOGO-WHITE-1.png"
        if os.path.exists(logo_filename):
            try:
                raw_img = Image.open(logo_filename)
                raw_img.thumbnail((110, 110), Image.Resampling.LANCZOS)
                self.logo_img = ImageTk.PhotoImage(raw_img)
                logo_label = tk.Label(center_container, image=self.logo_img, bg=COLOR_PRIMARY)
                logo_label.pack(side=tk.LEFT, pady=10)
            except Exception as e:
                print(f"Could not render logo image file: {e}")
        
        subtitle_label = tk.Label(
            center_container,
            text="K-12 School Districts Archive & Explorer Map",
            font=("Segoe UI Light", 25),
            fg="#94A3B8",
            bg=COLOR_PRIMARY
        )
        subtitle_label.pack(side=tk.LEFT, padx=(25, 0), pady=(10, 0))

        # --- GLOBAL SCROLL ARCHITECTURE ---
        scroll_container = tk.Frame(self.root, bg=COLOR_BG_LIGHT)
        scroll_container.pack(fill=tk.BOTH, expand=True)

        canvas = tk.Canvas(scroll_container, borderwidth=0, highlightthickness=0, bg=COLOR_BG_LIGHT)
        v_scrollbar = ttk.Scrollbar(scroll_container, orient=tk.VERTICAL, command=canvas.yview)
        canvas.configure(yscrollcommand=v_scrollbar.set)

        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollable_frame = tk.Frame(canvas, bg=COLOR_BG_LIGHT)
        canvas_frame_id = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

        def _on_frame_configure(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
        scrollable_frame.bind("<Configure>", _on_frame_configure)

        def _on_canvas_configure(event):
            canvas.itemconfig(canvas_frame_id, width=event.width)
        canvas.bind("<Configure>", _on_canvas_configure)

        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)

        # --- MAIN WORKSPACE CONTAINER ---
        main_content = ttk.Frame(scrollable_frame, padding=20, height=670)
        main_content.pack(fill=tk.X, side=tk.TOP)
        main_content.pack_propagate(False) 

        master_pane = ttk.PanedWindow(main_content, orient=tk.HORIZONTAL)
        master_pane.pack(fill=tk.BOTH, expand=True)

        left_side_panel = ttk.Frame(master_pane)
        control_strip = ttk.Frame(left_side_panel, padding=(0, 0, 0, 10))
        control_strip.pack(fill=tk.X, side=tk.TOP)
        
        self.deselect_btn = ttk.Button(
            control_strip, 
            text="✕  Deselect All", 
            style="Clear.TButton", 
            command=self.clear_all_selections
        )
        self.deselect_btn.pack(side=tk.LEFT)

        left_explorer_pane = ttk.PanedWindow(left_side_panel, orient=tk.HORIZONTAL)
        left_explorer_pane.pack(fill=tk.BOTH, expand=True)

        listbox_config = {
            "font": ("Segoe UI", 10),
            "bg": COLOR_LIST_BG,
            "fg": COLOR_TEXT_DARK,
            "selectbackground": COLOR_SELECT_BG,
            "selectforeground": COLOR_PRIMARY,
            "activestyle": "none",
            "borderwidth": 0,
            "highlightthickness": 0,
            "exportselection": False
        }

        # State Listbox
        state_frame = ttk.LabelFrame(left_explorer_pane, text="  1. SELECT STATE  ", padding=8)
        self.state_listbox = tk.Listbox(state_frame, **listbox_config)
        self.state_listbox.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
        state_scroll = ttk.Scrollbar(state_frame, orient=tk.VERTICAL, command=self.state_listbox.yview)
        state_scroll.pack(fill=tk.Y, side=tk.RIGHT)
        self.state_listbox.config(yscrollcommand=state_scroll.set)
        left_explorer_pane.add(state_frame, weight=1)

        # County Listbox
        county_frame = ttk.LabelFrame(left_explorer_pane, text="  2. SELECT COUNTY  ", padding=8)
        self.county_listbox = tk.Listbox(county_frame, **listbox_config)
        self.county_listbox.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
        county_scroll = ttk.Scrollbar(county_frame, orient=tk.VERTICAL, command=self.county_listbox.yview)
        county_scroll.pack(fill=tk.Y, side=tk.RIGHT)
        self.county_listbox.config(yscrollcommand=county_scroll.set)
        left_explorer_pane.add(county_frame, weight=1)

        # District Listbox
        district_frame = ttk.LabelFrame(left_explorer_pane, text="  3. SCHOOL DISTRICTS  ", padding=8)
        self.district_listbox = tk.Listbox(district_frame, **listbox_config)
        self.district_listbox.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
        district_scroll = ttk.Scrollbar(district_frame, orient=tk.VERTICAL, command=self.district_listbox.yview)
        district_scroll.pack(fill=tk.Y, side=tk.RIGHT)
        self.district_listbox.config(yscrollcommand=district_scroll.set)
        left_explorer_pane.add(district_frame, weight=2)

        master_pane.add(left_side_panel, weight=4)

        # MAP
        map_container = ttk.LabelFrame(master_pane, text="  INTERACTIVE REGIONAL MAP  ", padding=2)
        master_pane.add(map_container, weight=3)

        self.map_widget = tkintermapview.TkinterMapView(map_container, corner_radius=6)
        self.map_widget.pack(fill=tk.BOTH, expand=True)
        self.map_widget.set_position(40.0, -84.5)
        self.map_widget.set_zoom(6)

        # --- DUAL ROW FOOTER ARCHITECTURE ---
        self.detail_card = tk.Frame(scrollable_frame, bg="#FFFFFF", highlightbackground="#E2E8F0", highlightthickness=1)
        self.detail_card.pack(fill=tk.X, side=tk.TOP, padx=20, pady=(10, 10))

        accent_bar = tk.Frame(self.detail_card, bg=COLOR_SECONDARY, width=5)
        accent_bar.pack(fill=tk.Y, side=tk.LEFT)

        # Line 1: Hierarchical Selection Path
        self.detail_var = tk.StringVar(value="Select a state, county, and district to visualize administrative metrics.")
        self.detail_label = tk.Label(
            self.detail_card, textvariable=self.detail_var,
            font=("Segoe UI Semibold", 11), fg=COLOR_TEXT_DARK, bg="#FFFFFF",
            justify=tk.LEFT, anchor=tk.W, padx=15, pady=2
        )
        self.detail_label.pack(fill=tk.X, pady=(12, 4))

        # Line 2: Comprehensive State Statistics Row (uses a fixed-width type font for structured table display)
        self.stats_var = tk.StringVar(value="State Educational Stats: Select a state to view comprehensive performance metrics.")
        self.stats_label = tk.Label(
            self.detail_card, textvariable=self.stats_var,
            font=("Courier New", 10), fg="#334155", bg="#FFFFFF",
            justify=tk.LEFT, anchor=tk.W, padx=15, pady=2,
            wraplength=1220
        )
        self.stats_label.pack(fill=tk.X, pady=(4, 12))

        # --- STATE EDUCATION NEWS FEED PANEL ---
        news_frame = ttk.LabelFrame(scrollable_frame, text="  4. LOCAL EDUCATION HEADLINES (Double-Click to Read)  ", padding=10)
        news_frame.pack(fill=tk.X, side=tk.TOP, padx=20, pady=(10, 30))

        self.news_listbox = tk.Listbox(
            news_frame, 
            font=("Segoe UI", 10), 
            bg=COLOR_LIST_BG, 
            fg=COLOR_TEXT_DARK,
            selectbackground=COLOR_SELECT_BG,
            selectforeground=COLOR_PRIMARY,
            height=6, 
            borderwidth=0, 
            highlightthickness=0, 
            activestyle="none"
        )
        self.news_listbox.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
        
        news_scroll = ttk.Scrollbar(news_frame, orient=tk.VERTICAL, command=self.news_listbox.yview)
        news_scroll.pack(fill=tk.Y, side=tk.RIGHT)
        self.news_listbox.config(yscrollcommand=news_scroll.set)
        
        # Open matching URL when headline is double-clicked
        self.news_listbox.bind("<Double-Button-1>", self.open_headline_link)

        self.state_listbox.bind("<<ListboxSelect>>", self.on_state_select)
        self.county_listbox.bind("<<ListboxSelect>>", self.on_county_select)
        self.district_listbox.bind("<<ListboxSelect>>", self.on_district_select)

        self.populate_states()

    def populate_states(self):
        self.state_listbox.delete(0, tk.END)
        if not self.data.empty:
            for state in sorted(self.data["State"].unique()):
                self.state_listbox.insert(tk.END, f"  {state}")
        else:
            messagebox.showerror("Error", "Could not map database records. Verify CSV paths.")

    def clear_all_selections(self):
        self.state_listbox.selection_clear(0, tk.END)
        self.county_listbox.delete(0, tk.END)
        self.district_listbox.delete(0, tk.END)
        self.news_listbox.delete(0, tk.END)
        self.news_urls = []
        self.detail_var.set("Select a state, county, and district to visualize administrative metrics.")
        self.stats_var.set("State Educational Stats: Select a state to view comprehensive performance metrics.")
        
        if self.current_marker:
            self.current_marker.delete()
            self.current_marker = None
        if self.current_polygon:
            self.current_polygon.delete()
            self.current_polygon = None
            
        self.map_widget.set_position(40.0, -84.5)
        self.map_widget.set_zoom(6)

    def update_state_stats(self, state_name):
        stats_text = ""
        
        # 1. Base statistical metrics row from State EDU Stats.csv
        if hasattr(self, 'stats_data') and not self.stats_data.empty:
            state_row = self.stats_data[self.stats_data["State"] == state_name]
            if not state_row.empty:
                row = state_row.iloc[0]
                stats_text = (
                    f"📊 State Metrics ({state_name}) —\n"
                    f"Students: {row.get('Number of students', 'N/A')}  |  "
                    f"Grad Rate: {row.get('Graduation rate', 'N/A')}  |  "
                    f"Spending/Pupil: {row.get('Per-pupil spending', 'N/A')}  |  "
                    f"8th Math: {row.get('Average scale score (8th math)', 'N/A')}  |  "
                    f"4th Reading: {row.get('Average scale score (4th reading)', 'N/A')}  |  "
                    f"Avg SAT: {row.get('Average SAT score', 'N/A')}  |  "
                    f"Avg ACT: {row.get('Average ACT score', 'N/A')}\n\n"
                )
        
        # 2. Append report card grades structured as a clean text grid table from State Report Cards.csv
        if hasattr(self, 'report_cards_data') and not self.report_cards_data.empty:
            card_row = self.report_cards_data[self.report_cards_data["State"] == state_name]
            if not card_row.empty:
                rc = card_row.iloc[0]
                
                # Build an aligned structured table block
                table_header = "┌─────────────────────────┬───────┐\n" \
                               "│ Academic Category       │ Grade │\n" \
                               "├─────────────────────────┼───────┤\n"
                
                math_row      = f"│ Math Performance        │   {rc.get('Math Grade', 'N/A')}   │\n"
                english_row   = f"│ English/Language Arts   │   {rc.get('English Grade', 'N/A')}   │\n"
                college_row   = f"│ College Readiness       │   {rc.get('College Readiness Grade', 'N/A')}   │\n"
                parental_row  = f"│ Parental Rights Policy  │   {rc.get('Parental Rights', 'N/A')}   │\n"
                table_footer  = "└─────────────────────────┴───────┘\n"
                
                report_table = table_header + math_row + english_row + college_row + parental_row + table_footer
                report_card_text = (
                    f"📝 State Performance Evaluation Report Card:\n"
                    f"{report_table}"
                    f"📋 Analysis Summary:\n{rc.get('Description', 'N/A')}"
                )
                if stats_text:
                    stats_text += report_card_text
                else:
                    stats_text = f"📊 State Metrics ({state_name})\n\n{report_card_text}"
            else:
                stats_text += "\n📝 Report Card — No performance grades found for this state in database records."
        else:
            stats_text += "\n📝 Report Card — State Report Cards.csv is missing or could not be processed."

        if not stats_text.strip():
            stats_text = f"📊 State Metrics ({state_name}) — Missing statistical comparison vectors."

        self.stats_var.set(stats_text)

    def on_state_select(self, event):
        selection = self.state_listbox.curselection()
        if not selection:
            return

        self.county_listbox.delete(0, tk.END)
        self.district_listbox.delete(0, tk.END)
        self.detail_var.set("Select a county and target school district.")

        selected_state = self.state_listbox.get(selection[0]).strip()
        counties = sorted(self.data[self.data["State"] == selected_state]["County"].unique())
        for county in counties:
            self.county_listbox.insert(tk.END, f"  {county}")

        self.update_state_stats(selected_state)
        
        # Trigger background news processing thread
        self.news_listbox.delete(0, tk.END)
        self.news_listbox.insert(tk.END, "  🔄 Fetching local education headlines...")
        threading.Thread(target=self.async_fetch_news, args=(selected_state,), daemon=True).start()

        search_query = f"{selected_state}, USA"
        if search_query in self.boundary_cache:
            c = self.boundary_cache[search_query]
            self.apply_combined_updates(c["lat"], c["lon"], 7, c["path"], COLOR_PRIMARY, 3)
        else:
            threading.Thread(target=self.async_fetch_boundary, args=(search_query, True, 7), daemon=True).start()

    def async_fetch_news(self, state_name):
        """Asynchronously requests real-time education items from Google News RSS."""
        try:
            # Query pulls news relevant to 'Education' and the current state name
            query = f"K-12 Education {state_name}"
            url = f"https://news.google.com/rss/search?q={query}&hl=en-US&gl=US&ceid=US:en"
            
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
            response = requests.get(url, headers=headers, timeout=5)
            
            headlines = []
            urls = []
            
            if response.status_code == 200:
                root_xml = ET.fromstring(response.content)
                # Look up XML tree tags for standard channel RSS items
                for item in root_xml.findall(".//item")[:15]:  # Capture top 15 breaking items
                    title = item.find("title").text
                    link = item.find("link").text
                    
                    # Strip away excessive trailing publisher metadata from string headers if present
                    if " - " in title:
                        title = title.rsplit(" - ", 1)[0]
                        
                    headlines.append(f"  📰  {title}")
                    urls.append(link)
                    
            if not headlines:
                headlines = ["  No recent local education articles found."]
                urls = []
                
            self.root.after(0, self.apply_news_updates, headlines, urls)
        except Exception as e:
            print(f"News fetch system bypass exception: {e}")
            self.root.after(0, self.apply_news_updates, ["  ⚠️ Network timeline sync failed. Could not fetch news updates."], [])

    def apply_news_updates(self, headlines, urls):
        self.news_listbox.delete(0, tk.END)
        self.news_urls = urls
        for line in headlines:
            self.news_listbox.insert(tk.END, line)

    def open_headline_link(self, event):
        selection = self.news_listbox.curselection()
        if selection and self.news_urls:
            idx = selection[0]
            if idx < len(self.news_urls):
                webbrowser.open(self.news_urls[idx])

    def on_county_select(self, event):
        state_sel = self.state_listbox.curselection()
        county_sel = self.county_listbox.curselection()
        if not state_sel or not county_sel:
            return

        self.district_listbox.delete(0, tk.END)
        self.detail_var.set("Select a district to view mapped locations.")

        selected_state = self.state_listbox.get(state_sel[0]).strip()
        selected_county = self.county_listbox.get(county_sel[0]).strip()

        districts = sorted(
            self.data[
                (self.data["State"] == selected_state) & 
                (self.data["County"] == selected_county)
            ]["School District"].unique()
        )
        for dist in districts:
            self.district_listbox.insert(tk.END, f"  {dist}")

        search_query = f"{selected_county} County, {selected_state}, USA"
        
        if search_query in self.boundary_cache:
            c = self.boundary_cache[search_query]
            self.apply_combined_updates(c["lat"], c["lon"], 9, c["path"], COLOR_SECONDARY, 2)
        else:
            threading.Thread(target=self.async_fetch_boundary, args=(search_query, False, 9), daemon=True).start()

    def on_district_select(self, event):
        state_sel = self.state_listbox.curselection()
        county_sel = self.county_listbox.curselection()
        district_sel = self.district_listbox.curselection()

        if state_sel and county_sel and district_sel:
            selected_state = self.state_listbox.get(state_sel[0]).strip()
            selected_county = self.county_listbox.get(county_sel[0]).strip()
            selected_district = self.district_listbox.get(district_sel[0]).strip()

            row = self.data[
                (self.data["State"] == selected_state) & 
                (self.data["County"] == selected_county) & 
                (self.data["School District"] == selected_district)
            ]
            if not row.empty:
                city = row.iloc[0]["City"]
                self.detail_var.set(
                    f"🏫 District: {selected_district}   |   📍 City: {city}   |   🗺️ County: {selected_county}   |   State: {selected_state}"
                )

                search_query = f"{city}, {selected_state}, USA"
                marker_text = f"{selected_district}\n({city}, {selected_state})"
                
                if search_query in self.marker_cache:
                    lat, lon = self.marker_cache[search_query]
                    self.apply_map_updates(lat, lon, 11, marker_text)
                else:
                    threading.Thread(target=self.async_update_map, args=(search_query, 11, marker_text), daemon=True).start()

    def async_fetch_boundary(self, query, is_state, target_zoom):
        try:
            url = f"https://nominatim.openstreetmap.org/search?q={query}&format=json&polygon_geojson=1&limit=1"
            headers = {"User-Agent": "freedom_in_education_explorer_v4"}
            response = requests.get(url, headers=headers, timeout=5)
            
            if response.status_code == 200 and response.json():
                data = response.json()[0]
                lat = float(data.get("lat"))
                lon = float(data.get("lon"))
                
                geojson = data.get("geojson", {})
                geom_type = geojson.get("type")
                
                coordinates = []
                if geom_type == "Polygon":
                    coordinates = geojson["coordinates"][0]
                elif geom_type == "MultiPolygon":
                    coordinates = geojson["coordinates"][0][0]
                
                polygon_path = [(coord[1], coord[0]) for coord in coordinates] if coordinates else None
                self.boundary_cache[query] = {"lat": lat, "lon": lon, "path": polygon_path}
                
                color = COLOR_PRIMARY if is_state else COLOR_SECONDARY
                border_width = 3 if is_state else 2
                
                self.root.after(0, self.apply_combined_updates, lat, lon, target_zoom, polygon_path, color, border_width)
        except Exception as e:
            print(f"Failed to fetch outline boundary: {e}")

    def async_update_map(self, query, zoom_level, marker_text=None):
        try:
            location = self.geolocator.geocode(query, timeout=5)
            if location:
                self.marker_cache[query] = (location.latitude, location.longitude)
                self.root.after(0, self.apply_map_updates, location.latitude, location.longitude, zoom_level, marker_text)
        except Exception as e:
            print(f"Network Map Rendering Delay: {e}")

    def apply_map_updates(self, lat, lon, zoom, marker_text):
        self.map_widget.set_position(lat, lon)
        self.map_widget.set_zoom(zoom)

        if self.current_marker:
            self.current_marker.delete()
            self.current_marker = None

        if marker_text:
            self.current_marker = self.map_widget.set_marker(lat, lon, text=marker_text)

    def apply_combined_updates(self, lat, lon, zoom, path, color, border_width):
        self.map_widget.set_position(lat, lon)
        self.map_widget.set_zoom(zoom)

        if self.current_polygon:
            self.current_polygon.delete()
            self.current_polygon = None
            
        if path:
            self.current_polygon = self.map_widget.set_polygon(
                position_list=path,
                fill_color=None,
                outline_color=color,
                border_width=border_width
            )


if __name__ == "__main__":
    root = tk.Tk()
    app = ModernSchoolArchiveApp(root)
    root.mainloop()