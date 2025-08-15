from geopy.geocoders import Nominatim
from geopy.distance import geodesic

geolocator = Nominatim(user_agent="reroute-jobs")

def get_coordinates(zip_code):
    try:
        location = geolocator.geocode({"postalcode": zip_code, "countryRegion": "United States"})
        return (location.latitude, location.longitude) if location else None
    except Exception:
        return None

def is_within_radius(zip1, zip2, miles=5):
    coords1 = get_coordinates(zip1)
    coords2 = get_coordinates(zip2)
    if coords1 and coords2:
        return geodesic(coords1, coords2).miles <= miles
    return False
