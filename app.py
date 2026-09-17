from pathlib import Path
import pytest as pt

import pandas as pd
import streamlit as st
from src.house_search import find_houses

# TAMALE HOUSE RENTAL SEARCH SYSTEM

# PAGE CONFIGURATION
st.set_page_config(
    page_title="Tamale House Market",
    page_icon="🏠",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# CUSTOM CSS (ENFORCING DARK BLUE PAGE, WHITE FORM/CARDS & GREEN HOVER RADIUS)
st.markdown(
    """
    <style>
        /* OVERALL PAGE COLOR: DEEP DARK BLUE */
        .stApp {
            background-color: #0b1d3a !important;
            color: #ffffff !important;
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        }

        /* HERO HEADER BANNER */
        .main-header {
            background: linear-gradient(135deg, #132b50 0%, #1e3a8a 100%);
            padding: 32px 24px;
            border-radius: 16px;
            color: #ffffff;
            text-align: center;
            margin-bottom: 25px;
            border: 1px solid rgba(255, 255, 255, 0.1);
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
        }

        .main-header h1 {
            color: #ffffff !important;
            font-size: 30px !important;
            font-weight: 800 !important;
            margin-bottom: 8px !important;
            letter-spacing: -0.5px;
        }

        .main-header p {
            color: #93c5fd !important;
            font-size: 15px !important;
            margin: 0 !important;
        }

        /* SEARCH FORM: WHITE BACKGROUND WITH DARK BLUE COMPONENTS */
        div[data-testid="stForm"] {
            background-color: #ffffff !important;
            border: 1px solid #e2e8f0 !important;
            border-radius: 16px !important;
            padding: 28px !important;
            box-shadow: 0 12px 35px rgba(0, 0, 0, 0.25) !important;
        }

        .form-title {
            color: #0b1d3a;
            font-size: 20px;
            font-weight: 700;
            margin-bottom: 18px;
            border-bottom: 2px solid #e2e8f0;
            padding-bottom: 10px;
        }

        /* Form Labels */
        div[data-testid="stForm"] label p {
            color: #0b1d3a !important;
            font-weight: 600 !important;
            font-size: 14px !important;
        }

        /* Form Inputs */
        div[data-testid="stForm"] input {
            border-radius: 8px !important;
            border: 1.5px solid #cbd5e1 !important;
            background-color: #f8fafc !important;
            color: #0b1d3a !important;
            font-weight: 500 !important;
        }

        div[data-testid="stForm"] input:focus {
            border-color: #0b1d3a !important;
            background-color: #ffffff !important;
            box-shadow: 0 0 0 4px rgba(11, 29, 58, 0.15) !important;
        }

        div[data-baseweb="select"] > div {
            background-color: #f8fafc !important;
            border-radius: 8px !important;
            border: 1.5px solid #cbd5e1 !important;
            color: #0b1d3a !important;
        }

        /* Dark Blue Button */
        div[data-testid="stForm"] button[type="submit"],
        div[data-testid="stForm"] button[kind="secondaryFormSubmit"] {
            background: linear-gradient(135deg, #0b1d3a 0%, #1e3a8a 100%) !important;
            color: #ffffff !important;
            border: none !important;
            border-radius: 10px !important;
            padding: 13px 24px !important;
            font-size: 15px !important;
            font-weight: 700 !important;
            letter-spacing: 0.5px !important;
            box-shadow: 0 4px 15px rgba(11, 29, 58, 0.3) !important;
            transition: all 0.2s ease-in-out !important;
            cursor: pointer !important;
        }

        div[data-testid="stForm"] button[type="submit"]:hover {
            transform: translateY(-2px) !important;
            box-shadow: 0 8px 22px rgba(30, 58, 138, 0.45) !important;
            background: linear-gradient(135deg, #1e3a8a 0%, #2563eb 100%) !important;
        }

        /* HOUSE CARDS: WHITE WITH GREEN LIGHT HOVER RADIUS */
        .house-card {
            background-color: #ffffff;
            border-radius: 14px;
            padding: 24px;
            margin-bottom: 20px;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.15);
            border: 2px solid #e2e8f0;
            transition: transform 0.25s ease, border-color 0.25s ease, box-shadow 0.25s ease;
        }

        .house-card:hover {
            transform: translateY(-4px);
            border-color: #22c55e !important;
            box-shadow: 0 0 25px rgba(34, 197, 94, 0.4), 0 10px 25px rgba(0, 0, 0, 0.2) !important;
        }

        .house-card h3 {
            color: #0b1d3a;
            margin-top: 0;
            margin-bottom: 6px;
            font-size: 22px;
            font-weight: 800;
        }

        .house-card h2 {
            color: #16a34a;
            font-size: 20px;
            margin: 10px 0 16px 0;
            font-weight: 700;
        }

        .house-details p {
            margin: 4px 0 12px 0;
            color: #475569;
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
            background-color: #f0fdf4;
            color: #15803d;
            padding: 8px 14px;
            border-radius: 8px;
            font-size: 13px;
            font-weight: 600;
            flex: 1;
            min-width: 130px;
            text-align: center;
            border: 1px solid #bbf7d0;
        }
    </style>
""",
    unsafe_allow_html=True,
)


# HERO HEADER
st.markdown(
    """
    <div class="main-header">
        <h1>🏠 TAMALE HOUSE MARKET</h1>
        <p>Find Houses & Apartments in Tamale That Fit Your Budget</p>
    </div>
    """,
    unsafe_allow_html=True,
)


# DATA LOADER
@st.cache_data
def load_house():
    csv_path = Path(__file__).resolve().parent / "data" / "tamale_house_rentals.csv"
    return pd.read_csv(csv_path)


# SEARCH FORM
with st.form("house_search"):
    st.markdown(
        '<div class="form-title">🔍 Find Your House</div>',
        unsafe_allow_html=True,
    )

    budget = st.number_input(
        "Maximum Monthly Budget (GHS)", min_value=0.00, format="%.2f"
    )
    location = st.text_input("Preferred Neighborhood / Location (Optional)")

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


# HOUSE CARD RENDERER
def display_house_card(house):
    rent = (
        f"{house['monthly_rent_ghs']:,}"
        if isinstance(house["monthly_rent_ghs"], (int, float))
        else house["monthly_rent_ghs"]
    )

    st.markdown(
        f"""
        <div class="house-card"> 
            <h3>House #{house["house_id"]}</h3>
            <div class="house-details">
                <p>📍 <strong>Location:</strong> {house["neighborhood"]}</p>
                <h2><strong>Monthly Rent:</strong> GHS {rent}</h2>
                <div class="features">
                    <span>🛏️ <strong>Bedrooms:</strong> {house["rooms"]}</span>
                    <span>🚿 <strong>Bathrooms:</strong> {house["bathrooms"]}</span>
                    <span>💧 <strong>Water:</strong> {house["water"]}</span>
                </div>
            </div>  
        </div>
        """,
        unsafe_allow_html=True,
    )


# SEARCH LOGIC
if submitted:
    st.subheader("Available Houses")
    result = find_houses(budget, location, bedroom, water, bathroom)

    if result.empty:
        st.warning("Oops! No houses found matching your criteria.")
    else:
        st.success(f"🎉 {len(result)} house(s) found!")
        for _, house in result.iterrows():
            display_house_card(house)


# LOGIN FEATURE DEVELOPMENT            