
import pytest
from src.house_search import search_houses

def test_search_houses():
    result = search_houses(
        budget=2000,
        location="Lamashegu",
        bedroom=3,
        water="Yes",
        bathroom=2
    )

    assert result is not None 
    assert (result["monthly_rent_ghs"] <= 2000).all()
    assert (result["rooms"] <= 3).all()
    assert (result["bathrooms"] <= 2).all()
    assert (result["neighborhood"].str.lower() == "lamashegu").all()

def test_search_houses_respects_budget():
    result = search_houses(
        budget=5000,
        location="",
        bedroom=10,
        water="Yes",
        bathroom=10
    )

    assert (result["monthly_rent_ghs"] <= 5000).all()



def test_search_houses_respects_bedrooms():
    result = search_houses(
        budget=20000,
        location="",
        bedroom=2,
        water="Yes",
        bathroom=10
    )

    assert (result["rooms"] <= 2).all()   

def test_search_houses_respects_bathrooms():
    result = search_houses(
        budget=20000,
        location="",
        bedroom=10,
        water="Yes",
        bathroom=1
    )

    assert (result["bathrooms"] <= 1).all() 

def test_search_houses_respects_location():
    result = search_houses(
        budget=20000,
        location="Lamashegu",
        bedroom=10,
        water="Yes",
        bathroom=10
    )

    assert (result["neighborhood"].str.lower() == "lamashegu").all()

def test_search_houses_no_results():
    result = search_houses(
        budget=1,
        location="Lamashegu",
        bedroom=1,
        water="Yes",
        bathroom=1
    )

    assert result.empty

def test_search_houses_rejects_negative_budget():
    with pytest.raises(ValueError):
        search_houses(
            budget=-100,
            location="",
            bedroom=3,
            water="Yes",
            bathroom=2
        )


def test_search_houses_rejects_negative_bedrooms():
    with pytest.raises(ValueError):
        search_houses(
            budget=5000,
            location="",
            bedroom=-10,
            water="Yes",
            bathroom=2
        )


def test_search_houses_rejects_negative_bathrooms():
    with pytest.raises(ValueError):
        search_houses(
            budget=5000,
            location="",
            bedroom=3,
            water="Yes",
            bathroom=-10
        )

def test_search_houses_respects_water():
    result = search_houses(
        budget=20000,
        location="",
        bedroom=10,
        water="Yes",
        bathroom=10
    )

    assert (result["water"].str.lower() == "yes").all()

def test_search_houses_includes_exact_budget():
    result = search_houses(
        budget=350,
        location="",
        bedroom=10,
        water="Any",
        bathroom=10
    )

    assert (result["monthly_rent_ghs"] <= 350).all()
    assert 350 in result["monthly_rent_ghs"].values    

def test_search_houses_water_any():
    result = search_houses(
        budget=20000,
        location="",
        bedroom=10,
        water="Any",
        bathroom=10
    )

    assert not result.empty
    assert result["water"].str.lower().nunique() > 1    

def test_search_houses_location_is_case_insensitive():
    result = search_houses(
        budget=20000,
        location="LAMASHEGU",
        bedroom=10,
        water="Any",
        bathroom=10
    )

    assert not result.empty
    assert (result["neighborhood"].str.lower() == "lamashegu").all()
    
def test_search_houses_sorted_by_rent():
    result = search_houses(
        budget=20000,
        location="",
        bedroom=10,
        water="Any",
        bathroom=10
    )

    rents = result["monthly_rent_ghs"].tolist()

    assert rents == sorted(rents)    