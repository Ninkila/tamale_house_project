from functools import lru_cache
from pathlib import Path

import pandas as pd


@lru_cache(maxsize=1)
def load_house():
    csv_path = Path(__file__).resolve().parent.parent / "data" / "tamale_house_rentals.csv"
    return pd.read_csv(csv_path)


def search_houses(budget, location, bedroom, water, bathroom):
    if budget < 0:
        raise ValueError("Budget cannot be negative")
    if bedroom < 0:
        raise ValueError("Bedrooms cannot be negative")
    if bathroom < 0:
        raise ValueError("Bathrooms cannot be negative")

    houses = load_house().copy()
    for col in ("monthly_rent_ghs", "rooms", "bathrooms"):
        houses[col] = pd.to_numeric(houses[col], errors="coerce")

    houses["water"] = houses["water"].fillna("No").astype(str).str.strip()
    houses["water"] = houses["water"].str.replace(r"^.*available.*$", "Yes", regex=True)
    houses["water"] = houses["water"].str.replace(r"^.*not available.*$", "No", regex=True)
    houses["water"] = houses["water"].str.replace(r"^(yes|no|true|false)$", lambda m: "Yes" if m.group(1).lower() == "yes" or m.group(1).lower() == "true" else "No", regex=True)

    mask = houses["monthly_rent_ghs"].le(float(budget))

    if bedroom and int(bedroom) > 0:
        mask &= houses["rooms"].le(int(bedroom))
    if bathroom and int(bathroom) > 0:
        mask &= houses["bathrooms"].le(int(bathroom))

    if location and str(location).strip():
        text = str(location).strip().lower()
        mask &= houses["neighborhood"].fillna("").astype(str).str.lower().str.contains(text, regex=False)

    if water and str(water).strip().lower() != "any":
        requested = str(water).strip().lower()
        if requested in {"yes", "available", "true"}:
            mask &= houses["water"].str.lower().eq("yes")
        elif requested in {"no", "not available", "notavailable", "false"}:
            mask &= houses["water"].str.lower().eq("no")
        else:
            mask &= houses["water"].str.lower().eq(requested)

    return houses.loc[mask].sort_values(by="monthly_rent_ghs", ascending=True)


def find_houses(budget, location, bedroom, water, bathroom):
    return search_houses(budget, location, bedroom, water, bathroom)
