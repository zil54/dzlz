from dataclasses import dataclass
from pathlib import Path


US_STATES_DATA_DIR = Path(__file__).resolve().parent / "data" / "us_states"
US_STATES_ZIP_URL = "https://www2.census.gov/geo/tiger/GENZ2023/shp/cb_2023_us_state_20m.zip"
US_STATES_SHAPEFILE = US_STATES_DATA_DIR / "cb_2023_us_state_20m.shp"


@dataclass(frozen=True)
class USStateCapital:
    state: str
    abbreviation: str
    capital: str
    latitude: float
    longitude: float


US_STATE_CAPITALS = [
    USStateCapital("Alabama", "AL", "Montgomery", 32.3777, -86.3000),
    USStateCapital("Alaska", "AK", "Juneau", 58.3019, -134.4197),
    USStateCapital("Arizona", "AZ", "Phoenix", 33.4484, -112.0740),
    USStateCapital("Arkansas", "AR", "Little Rock", 34.7465, -92.2896),
    USStateCapital("California", "CA", "Sacramento", 38.5816, -121.4944),
    USStateCapital("Colorado", "CO", "Denver", 39.7392, -104.9903),
    USStateCapital("Connecticut", "CT", "Hartford", 41.7658, -72.6734),
    USStateCapital("Delaware", "DE", "Dover", 39.1582, -75.5244),
    USStateCapital("Florida", "FL", "Tallahassee", 30.4383, -84.2807),
    USStateCapital("Georgia", "GA", "Atlanta", 33.7490, -84.3880),
    USStateCapital("Hawaii", "HI", "Honolulu", 21.3099, -157.8581),
    USStateCapital("Idaho", "ID", "Boise", 43.6150, -116.2023),
    USStateCapital("Illinois", "IL", "Springfield", 39.7817, -89.6501),
    USStateCapital("Indiana", "IN", "Indianapolis", 39.7684, -86.1581),
    USStateCapital("Iowa", "IA", "Des Moines", 41.5868, -93.6250),
    USStateCapital("Kansas", "KS", "Topeka", 39.0473, -95.6752),
    USStateCapital("Kentucky", "KY", "Frankfort", 38.2009, -84.8733),
    USStateCapital("Louisiana", "LA", "Baton Rouge", 30.4515, -91.1871),
    USStateCapital("Maine", "ME", "Augusta", 44.3106, -69.7795),
    USStateCapital("Maryland", "MD", "Annapolis", 38.9784, -76.4922),
    USStateCapital("Massachusetts", "MA", "Boston", 42.3601, -71.0589),
    USStateCapital("Michigan", "MI", "Lansing", 42.7325, -84.5555),
    USStateCapital("Minnesota", "MN", "Saint Paul", 44.9537, -93.0900),
    USStateCapital("Mississippi", "MS", "Jackson", 32.2988, -90.1848),
    USStateCapital("Missouri", "MO", "Jefferson City", 38.5767, -92.1735),
    USStateCapital("Montana", "MT", "Helena", 46.5891, -112.0391),
    USStateCapital("Nebraska", "NE", "Lincoln", 40.8136, -96.7026),
    USStateCapital("Nevada", "NV", "Carson City", 39.1638, -119.7674),
    USStateCapital("New Hampshire", "NH", "Concord", 43.2081, -71.5376),
    USStateCapital("New Jersey", "NJ", "Trenton", 40.2206, -74.7597),
    USStateCapital("New Mexico", "NM", "Santa Fe", 35.6870, -105.9378),
    USStateCapital("New York", "NY", "Albany", 42.6526, -73.7562),
    USStateCapital("North Carolina", "NC", "Raleigh", 35.7796, -78.6382),
    USStateCapital("North Dakota", "ND", "Bismarck", 46.8083, -100.7837),
    USStateCapital("Ohio", "OH", "Columbus", 39.9612, -82.9988),
    USStateCapital("Oklahoma", "OK", "Oklahoma City", 35.4676, -97.5164),
    USStateCapital("Oregon", "OR", "Salem", 44.9429, -123.0351),
    USStateCapital("Pennsylvania", "PA", "Harrisburg", 40.2732, -76.8867),
    USStateCapital("Rhode Island", "RI", "Providence", 41.8240, -71.4128),
    USStateCapital("South Carolina", "SC", "Columbia", 34.0007, -81.0348),
    USStateCapital("South Dakota", "SD", "Pierre", 44.3683, -100.3510),
    USStateCapital("Tennessee", "TN", "Nashville", 36.1627, -86.7816),
    USStateCapital("Texas", "TX", "Austin", 30.2672, -97.7431),
    USStateCapital("Utah", "UT", "Salt Lake City", 40.7608, -111.8910),
    USStateCapital("Vermont", "VT", "Montpelier", 44.2601, -72.5754),
    USStateCapital("Virginia", "VA", "Richmond", 37.5407, -77.4360),
    USStateCapital("Washington", "WA", "Olympia", 47.0379, -122.9007),
    USStateCapital("West Virginia", "WV", "Charleston", 38.3498, -81.6326),
    USStateCapital("Wisconsin", "WI", "Madison", 43.0731, -89.4012),
    USStateCapital("Wyoming", "WY", "Cheyenne", 41.1400, -104.8202),
]
