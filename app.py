from pathlib import Path
import pandas as pd
import streamlit as st

# Safe import of find_houses if src.house_search module exists, otherwise fallback function
try:
    from src.house_search import find_houses
except ImportError:

    def find_houses(budget, location, bedroom, water, bathroom):
        df = load_house()
        filtered = df.copy()
        if budget > 0:
            rent_col = (
                "monthly_rent_ghs"
                if "monthly_rent_ghs" in filtered.columns
                else "annual_rent_ghs"
            )
            filtered = filtered[filtered[rent_col] <= budget]
        if location and location.strip():
            filtered = filtered[
                filtered["neighborhood"].str.contains(
                    location.strip(), case=False, na=False
                )
            ]
        if bedroom > 0:
            filtered = filtered[filtered["rooms"] >= bedroom]
        if bathroom > 0:
            filtered = filtered[filtered["bathrooms"] >= bathroom]
        if water and water != "Any":
            filtered = filtered[filtered["water"] == water]
        return filtered


# PAGE CONFIGURATION
st.set_page_config(
    page_title="Tamale House Market | Real Estate Marketplace",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -----------------------------------------------------------------------------
# REALISTIC VECTOR SVG ICONS (NO EMOJIS)
# -----------------------------------------------------------------------------
SVG_HOUSE = '<svg style="vertical-align: text-bottom; margin-right: 8px;" width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="#38bdf8" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="m3 9 9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>'
SVG_SEARCH = '<svg style="vertical-align: text-bottom; margin-right: 8px;" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#0b1d3a" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/></svg>'
SVG_LOCATION = '<svg style="vertical-align: middle; margin-right: 6px;" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#2563eb" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0Z"/><circle cx="12" cy="10" r="3"/></svg>'
SVG_BED = '<svg style="vertical-align: middle; margin-right: 6px;" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#16a34a" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M2 4v16"/><path d="M2 8h18a2 2 0 0 1 2 2v10"/><path d="M2 17h20"/><path d="M6 8v9"/></svg>'
SVG_BATH = '<svg style="vertical-align: middle; margin-right: 6px;" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#0284c7" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 6 6.5 3.5a1.5 1.5 0 0 0-2.12 0 1.5 1.5 0 0 0 0 2.12L6.88 8"/><path d="M4 12h16a1 1 0 0 1 1 1v3a4 4 0 0 1-4 4H7a4 4 0 0 1-4-4v-3a1 1 0 0 1 1-1Z"/><line x1="6" x2="6" y1="12" y2="16"/></svg>'
SVG_WATER = '<svg style="vertical-align: middle; margin-right: 6px;" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#0284c7" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2.69l5.66 5.66a8 8 0 1 1-11.31 0z"/></svg>'
SVG_TARGET = '<svg style="vertical-align: text-bottom; margin-right: 8px;" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#38bdf8" stroke-width="2.2"><circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/></svg>'
SVG_STAR = '<svg style="vertical-align: text-bottom; margin-right: 8px;" width="22" height="22" viewBox="0 0 24 24" fill="#eab308" stroke="#eab308" stroke-width="2"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>'

# -----------------------------------------------------------------------------
# 1. AUTHENTICATION SESSION MANAGEMENT
# -----------------------------------------------------------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "user" not in st.session_state:
    st.session_state.user = None

# -----------------------------------------------------------------------------
# 2. FULL-SCREEN LOGIN PAGE WITH HOUSE BACKGROUND WALLPAPER
# -----------------------------------------------------------------------------
if not st.session_state.logged_in:
    st.markdown(
        """
        <style>
            .stApp {
                background: linear-gradient(135deg, rgba(11, 29, 58, 0.82) 0%, rgba(11, 29, 58, 0.92) 100%),
                            url('https://images.unsplash.com/photo-1600596542815-ffad4c1539a9?auto=format&fit=crop&w=1920&q=80') center/cover no-repeat fixed !important;
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            }

            div[data-testid="stForm"] {
                max-width: 460px !important;
                margin: 60px auto !important;
                background-color: rgba(255, 255, 255, 0.98) !important;
                backdrop-filter: blur(16px) !important;
                border-radius: 20px !important;
                padding: 36px !important;
                box-shadow: 0 20px 50px rgba(0, 0, 0, 0.5) !important;
                border: 1px solid rgba(255, 255, 255, 0.9) !important;
            }

            div[data-testid="stForm"] label p,
            div[data-testid="stForm"] p,
            div[data-testid="stForm"] span,
            div[data-testid="stForm"] h2,
            div[data-testid="stForm"] h3 {
                color: #0b1d3a !important;
                font-weight: 700 !important;
            }

            div[data-testid="stForm"] input {
                background-color: #f1f5f9 !important;
                color: #0b1d3a !important;
                border: 2px solid #cbd5e1 !important;
                border-radius: 8px !important;
                font-weight: 600 !important;
            }

            div[data-testid="stForm"] button[type="submit"] {
                background: linear-gradient(135deg, #0b1d3a 0%, #1e3a8a 100%) !important;
                color: #ffffff !important;
                border: none !important;
                border-radius: 10px !important;
                padding: 13px 24px !important;
                font-size: 15px !important;
                font-weight: 700 !important;
                box-shadow: 0 4px 15px rgba(11, 29, 58, 0.3) !important;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
        <div style="text-align: center; margin-top: 40px; color: #ffffff;">
            <h1 style="color: #ffffff !important; font-size: 38px; font-weight: 800;">{SVG_HOUSE} TAMALE HOUSE MARKET</h1>
            <p style="color: #93c5fd !important; font-size: 18px; font-weight: 500;">Find Your Ideal Rental House in Tamale</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.form("login_form"):
        st.markdown(
            """
            <div style="text-align: center; margin-bottom: 20px;">
                <h2 style="color: #0b1d3a !important; font-weight: 800; margin-bottom: 4px;">Welcome Back</h2>
                <p style="color: #475569 !important; font-size: 14px; font-weight: 500;">Sign in to access verified real estate listings</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        username = st.text_input(
            "Username / Email", placeholder="Enter your username"
        )
        password = st.text_input(
            "Password", placeholder="Enter your password"
        )
        login_btn = st.form_submit_button(
            "LOGIN TO MARKETPLACE", use_container_width=True
        )

        if login_btn:
            if username and password:
                st.session_state.logged_in = True
                st.session_state.user = {"username": username}
                st.success("Login successful!")
                st.rerun()
            else:
                st.error("Please fill in both username and password.")

    st.stop()


# -----------------------------------------------------------------------------
# 3. HIGH CONTRAST STYLING FOR NAVBAR, SIDEBAR & FORMS
# -----------------------------------------------------------------------------
st.markdown(
    """
    <style>
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(12px); }
            to { opacity: 1; transform: translateY(0); }
        }

        .stApp {
            background-color: #0b1d3a !important;
            color: #ffffff !important;
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            animation: fadeIn 0.5s ease-out;
        }

        /* --- A. SIDEBAR TEXT VISIBILITY --- */
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #071326 0%, #0b1d3a 100%) !important;
            border-right: 1.5px solid rgba(255, 255, 255, 0.15) !important;
        }

        [data-testid="stSidebar"] h1,
        [data-testid="stSidebar"] h2,
        [data-testid="stSidebar"] h3 {
            color: #38bdf8 !important;
            font-weight: 800 !important;
        }

        [data-testid="stSidebar"] p,
        [data-testid="stSidebar"] span,
        [data-testid="stSidebar"] div {
            color: #ffffff !important;
            font-weight: 600 !important;
            font-size: 15px !important;
        }

        [data-testid="stSidebar"] button {
            background: linear-gradient(135deg, #dc2626 0%, #ef4444 100%) !important;
            color: #ffffff !important;
            font-weight: 700 !important;
            border: none !important;
            border-radius: 8px !important;
            padding: 10px 16px !important;
            box-shadow: 0 4px 12px rgba(239, 68, 68, 0.3) !important;
        }

        /* --- B. NAVBAR TABS TEXT VISIBILITY --- */
        div[data-testid="stRadio"] > div {
            background: #132b50 !important;
            padding: 8px !important;
            border-radius: 14px !important;
            border: 1.5px solid rgba(255, 255, 255, 0.18) !important;
            display: flex !important;
            gap: 10px !important;
            margin-bottom: 24px !important;
        }

        div[data-testid="stRadio"] label {
            background: rgba(255, 255, 255, 0.08) !important;
            color: #ffffff !important;
            padding: 12px 24px !important;
            border-radius: 10px !important;
            font-weight: 700 !important;
            font-size: 15px !important;
            letter-spacing: 0.3px !important;
            cursor: pointer !important;
            transition: all 0.25s ease !important;
        }

        div[data-testid="stRadio"] label:hover {
            color: #ffffff !important;
            background: rgba(255, 255, 255, 0.22) !important;
        }

        div[data-testid="stRadio"] label[data-checked="true"] {
            background: linear-gradient(135deg, #1d4ed8 0%, #2563eb 100%) !important;
            color: #ffffff !important;
            box-shadow: 0 4px 14px rgba(37, 99, 235, 0.5) !important;
            font-weight: 800 !important;
        }

        /* --- C. FORM LABELS & INPUT TEXT VISIBILITY --- */
        div[data-testid="stForm"] {
            background-color: #ffffff !important;
            border: 2px solid #e2e8f0 !important;
            border-radius: 18px !important;
            padding: 32px !important;
            box-shadow: 0 14px 40px rgba(0, 0, 0, 0.25) !important;
        }

        .form-title {
            color: #0b1d3a !important;
            font-size: 22px;
            font-weight: 800;
            margin-bottom: 20px;
            border-bottom: 2px solid #f1f5f9;
            padding-bottom: 10px;
        }

        div[data-testid="stForm"] label p,
        div[data-testid="stForm"] p,
        div[data-testid="stForm"] span,
        div[data-testid="stForm"] h1,
        div[data-testid="stForm"] h2,
        div[data-testid="stForm"] h3 {
            color: #0b1d3a !important;
            font-weight: 700 !important;
            font-size: 15px !important;
        }

        div[data-testid="stForm"] input,
        div[data-testid="stForm"] textarea {
            border-radius: 8px !important;
            border: 2px solid #cbd5e1 !important;
            background-color: #f1f5f9 !important;
            color: #0b1d3a !important;
            font-weight: 600 !important;
            font-size: 15px !important;
        }

        div[data-testid="stForm"] input:focus,
        div[data-testid="stForm"] textarea:focus {
            border-color: #0b1d3a !important;
            background-color: #ffffff !important;
            box-shadow: 0 0 0 4px rgba(11, 29, 58, 0.15) !important;
        }

        /* DROPDOWN SELECT VISIBILITY */
        div[data-baseweb="select"] * {
            color: #0b1d3a !important;
            font-weight: 600 !important;
        }

        div[data-baseweb="select"] > div {
            background-color: #f1f5f9 !important;
            border-radius: 8px !important;
            border: 2px solid #cbd5e1 !important;
        }

        div[data-baseweb="menu"] * {
            color: #0b1d3a !important;
            font-weight: 600 !important;
            background-color: #ffffff !important;
        }

        div[data-testid="stForm"] button[type="submit"],
        div[data-testid="stForm"] button[kind="secondaryFormSubmit"] {
            background: linear-gradient(135deg, #0b1d3a 0%, #1e3a8a 100%) !important;
            color: #ffffff !important;
            border: none !important;
            border-radius: 10px !important;
            padding: 14px 24px !important;
            font-size: 16px !important;
            font-weight: 700 !important;
            letter-spacing: 0.5px !important;
            box-shadow: 0 4px 15px rgba(11, 29, 58, 0.3) !important;
            transition: all 0.25s ease-in-out !important;
            cursor: pointer !important;
        }

        div[data-testid="stForm"] button[type="submit"]:hover {
            transform: translateY(-2px) !important;
            box-shadow: 0 8px 22px rgba(30, 58, 138, 0.45) !important;
            background: linear-gradient(135deg, #1e3a8a 0%, #2563eb 100%) !important;
        }

        /* HOUSE CARDS: WHITE WITH GREEN LIGHT HOVER RADIUS GLOW */
        .house-card {
            background-color: #ffffff;
            border-radius: 16px;
            padding: 26px;
            margin-bottom: 22px;
            box-shadow: 0 4px 18px rgba(0, 0, 0, 0.15);
            border: 2px solid #e2e8f0;
            transition: transform 0.3s ease, border-color 0.3s ease, box-shadow 0.3s ease;
        }

        .house-card:hover {
            transform: translateY(-5px);
            border-color: #22c55e !important;
            box-shadow: 0 0 28px rgba(34, 197, 94, 0.45), 0 12px 30px rgba(0, 0, 0, 0.22) !important;
        }

        .house-card h3 {
            color: #0b1d3a !important;
            margin-top: 0;
            margin-bottom: 6px;
            font-size: 22px;
            font-weight: 800;
        }

        .house-card h2 {
            color: #16a34a !important;
            font-size: 21px;
            margin: 10px 0 16px 0;
            font-weight: 700;
        }

        .house-details p {
            margin: 4px 0 12px 0;
            color: #475569 !important;
            font-size: 15px;
        }

        .features {
            display: flex;
            justify-content: space-between;
            flex-wrap: wrap;
            gap: 12px;
            margin-top: 16px;   
        }

        .features span {
            background-color: #f0fdf4 !important;
            color: #15803d !important;
            padding: 8px 14px;
            border-radius: 8px;
            font-size: 13px;
            font-weight: 600;
            flex: 1;
            min-width: 130px;
            text-align: center;
            border: 1px solid #bbf7d0;
        }

        .main-header {
            background: linear-gradient(135deg, #132b50 0%, #1e3a8a 100%);
            padding: 36px 28px;
            border-radius: 20px;
            color: #ffffff;
            text-align: center;
            margin-bottom: 30px;
            border: 1px solid rgba(255, 255, 255, 0.12);
            box-shadow: 0 12px 35px rgba(0, 0, 0, 0.35);
        }

        .main-header h1 {
            color: #ffffff !important;
            font-size: 34px !important;
            font-weight: 800 !important;
            margin-bottom: 8px !important;
        }

        .main-header p {
            color: #93c5fd !important;
            font-size: 16px !important;
            margin: 0 !important;
        }

        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(170px, 1fr));
            gap: 16px;
            margin-top: 24px;
        }

        .stat-card {
            background: rgba(255, 255, 255, 0.08);
            backdrop-filter: blur(10px);
            padding: 18px;
            border-radius: 14px;
            text-align: center;
            border: 1px solid rgba(255, 255, 255, 0.12);
        }

        .stat-number {
            font-size: 26px;
            font-weight: 800;
            color: #22c55e;
        }

        .stat-label {
            font-size: 13px;
            color: #cbd5e1;
            margin-top: 4px;
        }

        .footer-container {
            background: linear-gradient(135deg, #071326 0%, #0e2447 100%);
            border-top: 1px solid rgba(255, 255, 255, 0.1);
            padding: 40px 30px 20px 30px;
            border-radius: 20px 20px 0 0;
            margin-top: 60px;
            color: #94a3b8;
        }

        .footer-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 30px;
            margin-bottom: 30px;
        }

        .footer-col h3 {
            color: #ffffff !important;
            font-size: 20px;
            font-weight: 800;
            margin-bottom: 12px;
        }

        .footer-col h4 {
            color: #38bdf8 !important;
            font-size: 16px;
            font-weight: 700;
            margin-bottom: 14px;
        }

        .footer-col p, .footer-col li {
            font-size: 14px;
            line-height: 1.6;
            color: #cbd5e1 !important;
        }

        .footer-col ul {
            list-style: none;
            padding: 0;
            margin: 0;
        }

        .footer-col ul li {
            margin-bottom: 8px;
        }

        .footer-bottom {
            text-align: center;
            border-top: 1px solid rgba(255, 255, 255, 0.08);
            padding-top: 20px;
            font-size: 13px;
            color: #64748b !important;
        }
    </style>
""",
    unsafe_allow_html=True,
)

# -----------------------------------------------------------------------------
# 4. SIDEBAR & NAVBAR
# -----------------------------------------------------------------------------
with st.sidebar:
    st.markdown("### User Account")
    st.write(f"Logged in as: **{st.session_state.user['username']}**")
    st.markdown("---")

    if st.button("Logout", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.user = None
        st.rerun()

# TOP NAVBAR NAVIGATION
selected_nav = st.radio(
    "Navigation Menu",
    ["Home", "Search Houses", "About Us", "Contact Us"],
    horizontal=True,
    label_visibility="collapsed",
)


# -----------------------------------------------------------------------------
# 5. DATA LOADER & HOUSE CARD RENDERER
# -----------------------------------------------------------------------------
@st.cache_data
def load_house():
    csv_path = Path(__file__).resolve().parent / "data" / "tamale_house_rentals.csv"
    if csv_path.exists():
        return pd.read_csv(csv_path)

    return pd.DataFrame(
        [
            {
                "house_id": 101,
                "neighborhood": "Lamashegu",
                "monthly_rent_ghs": 850,
                "rooms": 2,
                "bathrooms": 1,
                "water": "Available",
            },
            {
                "house_id": 102,
                "neighborhood": "Vittin",
                "monthly_rent_ghs": 1200,
                "rooms": 3,
                "bathrooms": 2,
                "water": "Available",
            },
            {
                "house_id": 103,
                "neighborhood": "Aboabo",
                "monthly_rent_ghs": 600,
                "rooms": 1,
                "bathrooms": 1,
                "water": "Not available",
            },
            {
                "house_id": 104,
                "neighborhood": "Kalpohin",
                "monthly_rent_ghs": 1500,
                "rooms": 4,
                "bathrooms": 3,
                "water": "Available",
            },
        ]
    )


def display_house_card(house):
    rent_key = (
        "monthly_rent_ghs"
        if "monthly_rent_ghs" in house
        else "annual_rent_ghs"
    )
    rent_val = house[rent_key]
    formatted_rent = (
        f"{rent_val:,}" if isinstance(rent_val, (int, float)) else rent_val
    )
    rent_label = "Monthly Rent" if rent_key == "monthly_rent_ghs" else "Annual Rent"

    st.markdown(
        f"""
        <div class="house-card"> 
            <h3>House #{house["house_id"]}</h3>
            <div class="house-details">
                <p>{SVG_LOCATION}<strong>Location:</strong> {house["neighborhood"]}</p>
                <h2><strong>{rent_label}:</strong> GHS {formatted_rent}</h2>
                <div class="features">
                    <span>{SVG_BED}<strong>Bedrooms:</strong> {house["rooms"]}</span>
                    <span>{SVG_BATH}<strong>Bathrooms:</strong> {house["bathrooms"]}</span>
                    <span>{SVG_WATER}<strong>Water:</strong> {house["water"]}</span>
                </div>
            </div>  
        </div>
        """,
        unsafe_allow_html=True,
    )


# -----------------------------------------------------------------------------
# 6. ROUTER (PAGES)
# -----------------------------------------------------------------------------

# --- A) HOME PAGE ---
if selected_nav == "Home":
    st.markdown(
        f"""
        <div class="main-header">
            <h1>{SVG_HOUSE} TAMALE HOUSE MARKET</h1>
            <p>The #1 Digital Marketplace for Houses & Apartments in Tamale</p>
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-number">500+</div>
                    <div class="stat-label">Verified Listings</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">12+</div>
                    <div class="stat-label">Neighborhoods</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">98%</div>
                    <div class="stat-label">Happy Renters</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">24/7</div>
                    <div class="stat-label">Support</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        '<h3 style="color: #ffffff !important; margin-bottom: 16px;">Featured Houses in Tamale</h3>',
        unsafe_allow_html=True,
    )
    df_houses = load_house()
    for _, house in df_houses.head(3).iterrows():
        display_house_card(house)


# --- B) SEARCH HOUSES PAGE ---
elif selected_nav == "Search Houses":
    st.markdown(
        """
        <div class="main-header" style="padding: 24px; margin-bottom: 20px;">
            <h1 style="font-size: 26px !important;">Search Available Rentals</h1>
            <p style="font-size: 14px !important;">Filter by budget, neighborhood, rooms, and water availability</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.form("house_search"):
        st.markdown(
            f'<div class="form-title">{SVG_SEARCH}Search Criteria</div>',
            unsafe_allow_html=True,
        )

        budget = st.number_input(
            "Maximum Monthly Budget (GHS)", min_value=0.00, format="%.2f"
        )
        location = st.text_input(
            "Preferred Neighborhood / Location (Optional)"
        )

        col5, col6, col7 = st.columns(3)
        with col5:
            bedroom = st.number_input(
                "Bedrooms", min_value=1, max_value=10, step=1, value=1
            )
        with col6:
            water = st.selectbox(
                "Water Availability", ["Any", "Available", "Not available"]
            )
        with col7:
            bathroom = st.number_input(
                "Bathrooms", min_value=1, max_value=10, step=1, value=1
            )

        submitted = st.form_submit_button(
            "SEARCH AVAILABLE HOUSES", use_container_width=True
        )

    if submitted:
        st.markdown(
            '<h3 style="color: #ffffff !important; margin-top: 20px;">Search Results</h3>',
            unsafe_allow_html=True,
        )
        result = find_houses(budget, location, bedroom, water, bathroom)

        if result.empty:
            st.warning("Oops! No houses found matching your criteria.")
        else:
            st.success(f"{len(result)} house(s) found!")
            for _, house in result.iterrows():
                display_house_card(house)


# --- C) ABOUT US PAGE ---
elif selected_nav == "About Us":
    st.markdown(
        """
        <div class="main-header">
            <h1>About Tamale House Market</h1>
            <p>Connecting Tenants with Verified Landlords across Tamale, Ghana</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown(
            f"""
            <div style="background: rgba(255,255,255,0.06); padding: 24px; border-radius: 14px; border: 1px solid rgba(255,255,255,0.1);">
                <h3 style="color: #38bdf8 !important;">{SVG_TARGET} Our Mission</h3>
                <p style="color: #cbd5e1 !important; line-height: 1.6;">
                    We make finding rental properties in Tamale fast, transparent, and hassle-free.
                    Whether you are looking for a single-room self-contained or a full family bungalow,
                    our platform connects you directly with legitimate listings.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col_b:
        st.markdown(
            f"""
            <div style="background: rgba(255,255,255,0.06); padding: 24px; border-radius: 14px; border: 1px solid rgba(255,255,255,0.1);">
                <h3 style="color: #22c55e !important;">{SVG_STAR} Why Choose Us?</h3>
                <p style="color: #cbd5e1 !important; line-height: 1.6;">
                    • <strong>Verified Listings:</strong> All properties inspected for accuracy.<br>
                    • <strong>No Hidden Fees:</strong> Direct pricing in GHS with clear monthly rates.<br>
                    • <strong>Water & Amenities Info:</strong> Know water availability before visiting.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )


# --- D) CONTACT US PAGE ---
elif selected_nav == "Contact Us":
    st.markdown(
        """
        <div class="main-header">
            <h1>Contact Our Team</h1>
            <p>Have questions or need assistance finding a house? Reach out to us!</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.form("contact_form"):
        st.markdown(
            '<div class="form-title">Send Us a Message</div>',
            unsafe_allow_html=True,
        )
        c_name = st.text_input("Your Full Name")
        c_email = st.text_input("Your Email Address / Phone Number")
        c_msg = st.text_area("How can we help you?")
        send_msg = st.form_submit_button(
            "SEND MESSAGE", use_container_width=True
        )

        if send_msg:
            if c_name and c_msg:
                st.success("Thank you! Your message has been sent to our Tamale support team.")
            else:
                st.error("Please fill in your name and message.")


# -----------------------------------------------------------------------------
# 7. BUSINESS FOOTER
# -----------------------------------------------------------------------------
st.markdown(
    """
    <footer class="footer-container">
        <div class="footer-grid">
            <div class="footer-col">
                <h3>Tamale House Market</h3>
                <p>Your #1 trusted digital marketplace for renting houses and apartments across Tamale and the Northern Region of Ghana.</p>
            </div>
            <div class="footer-col">
                <h4>Quick Links</h4>
                <ul>
                    <li>Home Page</li>
                    <li>Search Rentals</li>
                    <li>About Our Platform</li>
                    <li>Contact Support</li>
                </ul>
            </div>
            <div class="footer-col">
                <h4>Top Neighborhoods</h4>
                <p>Lamashegu • Vittin • Aboabo • Kalpohin • Nyohini</p>
            </div>
            <div class="footer-col">
                <h4>Contact Info</h4>
                <p>Central Market Road, Tamale, Ghana</p>
                <p>+233 (0)20 123 4567</p>
                <p>info@tamalehousemarket.com</p>
            </div>
        </div>
        <div class="footer-bottom">
            <p>© 2026 Tamale House Market. All Rights Reserved. Real Estate Excellence in Tamale.</p>
        </div>
    </footer>
    """,
    unsafe_allow_html=True,
)