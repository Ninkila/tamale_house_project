from pathlib import Path

import pandas as pd
import streamlit as st


@st.cache_data
def load_house():
    csv_path = Path(__file__).resolve().parents[1] / "data" / "tamale_house_rentals.csv"
    return pd.read_csv(csv_path)


def search_houses(budget, location, bedroom, water, bathroom):
    houses = load_house().copy()
    houses['monthly_rent_ghs'] = pd.to_numeric(houses['monthly_rent_ghs'], errors='coerce')
    houses['rooms'] = pd.to_numeric(houses['rooms'], errors='coerce')
    houses['bathrooms'] = pd.to_numeric(houses['bathrooms'], errors='coerce')

    mask = (
        houses['monthly_rent_ghs'].le(budget)
        & houses['rooms'].le(bedroom)
        & houses['bathrooms'].le(bathroom)
    )

    if location:
        location_text = str(location).strip().lower()
        mask &= houses['neighborhood'].fillna('').astype(str).str.lower().eq(location_text)

    if water and str(water).strip().lower() != 'any':
        water_text = str(water).strip().lower()
        mask &= houses['water'].fillna('').astype(str).str.lower().eq(water_text)

    result = houses.loc[mask].copy()
    if not result.empty:
        result = result.sort_values(by='monthly_rent_ghs', ascending=True)

    
    if budget < 0:
        raise ValueError("Budget cannot be negative")

    if bedroom < 0:
        raise ValueError("Bedrooms cannot be negative")

    if bathroom < 0:
        raise ValueError("Bathrooms cannot be negative")
    return result

def find_houses(budget, location, bedroom, water, bathroom):
    return search_houses(budget, location, bedroom, water, bathroom)

    