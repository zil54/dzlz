from dataclasses import dataclass


@dataclass(frozen=True)
class Landmark:
    name: str
    city_or_region: str
    country: str
    latitude: float
    longitude: float
    zoom_degrees: float = 8.0
    wikipedia_title: str | None = None


LANDMARKS = [
    Landmark("Eiffel Tower", "Paris", "France", 48.8584, 2.2945, 4.0),
    Landmark("Great Wall of China", "Beijing region", "China", 40.4319, 116.5704, 8.0),
    Landmark("Taj Mahal", "Agra", "India", 27.1751, 78.0421, 4.0),
    Landmark("Machu Picchu", "Cusco Region", "Peru", -13.1631, -72.5450, 5.0),
    Landmark("Colosseum", "Rome", "Italy", 41.8902, 12.4922, 4.0),
    Landmark("Christ the Redeemer", "Rio de Janeiro", "Brazil", -22.9519, -43.2105, 4.0, "Christ the Redeemer (statue)"),
    Landmark("Statue of Liberty", "New York City", "United States of America", 40.6892, -74.0445, 4.0),
    Landmark("Pyramids of Giza", "Giza", "Egypt", 29.9792, 31.1342, 4.0, "Giza pyramid complex"),
    Landmark("Stonehenge", "Wiltshire", "United Kingdom", 51.1789, -1.8262, 4.0),
    Landmark("Angkor Wat", "Siem Reap", "Cambodia", 13.4125, 103.8670, 4.0),
    Landmark("Petra", "Ma'an Governorate", "Jordan", 30.3285, 35.4444, 4.0),
    Landmark("Sydney Opera House", "Sydney", "Australia", -33.8568, 151.2153, 4.0),
    Landmark("Burj Khalifa", "Dubai", "United Arab Emirates", 25.1972, 55.2744, 4.0),
    Landmark("Mount Rushmore", "South Dakota", "United States of America", 43.8791, -103.4591, 5.0),
    Landmark("Sagrada Familia", "Barcelona", "Spain", 41.4036, 2.1744, 4.0),
    Landmark("Acropolis of Athens", "Athens", "Greece", 37.9715, 23.7257, 4.0),
    Landmark("Big Ben", "London", "United Kingdom", 51.5007, -0.1246, 4.0),
    Landmark("Chichen Itza", "Yucatan", "Mexico", 20.6843, -88.5678, 4.0),
    Landmark("Hagia Sophia", "Istanbul", "Turkey", 41.0086, 28.9802, 4.0),
    Landmark("Tower of Pisa", "Pisa", "Italy", 43.7230, 10.3966, 4.0, "Leaning Tower of Pisa"),
    Landmark("Forbidden City", "Beijing", "China", 39.9163, 116.3972, 4.0),
    Landmark("Louvre Museum", "Paris", "France", 48.8606, 2.3376, 4.0),
    Landmark("Niagara Falls", "Ontario/New York", "Canada", 43.0962, -79.0377, 4.0),
    Landmark("Grand Canyon", "Arizona", "United States of America", 36.1069, -112.1129, 7.0),
    Landmark("Table Mountain", "Cape Town", "South Africa", -33.9628, 18.4098, 4.0),
    Landmark("Uluru", "Northern Territory", "Australia", -25.3444, 131.0369, 5.0),
    Landmark("Brandenburg Gate", "Berlin", "Germany", 52.5163, 13.3777, 4.0),
    Landmark("The Shard", "London", "United Kingdom", 51.5045, -0.0865, 4.0),
    Landmark("St. Basil's Cathedral", "Moscow", "Russia", 55.7525, 37.6231, 4.0),
    Landmark("Blue Mosque", "Istanbul", "Turkey", 41.0054, 28.9768, 4.0, "Sultan Ahmed Mosque"),
    Landmark("Sofia Cathedral", "Kyiv", "Ukraine", 50.4529, 30.5143, 4.0, "Saint Sophia Cathedral, Kyiv"),
    Landmark("Masada", "Southern District", "Israel", 31.3156, 35.3539, 4.0),
    Landmark("Panama Canal", "Panama", "Panama", 9.0800, -79.6800, 5.0),
    Landmark("Red Square", "Moscow", "Russia", 55.7539, 37.6208, 4.0),
    Landmark("Danube River Bridges", "Budapest", "Hungary", 47.4980, 19.0437, 4.0, "Bridges of Budapest"),
    Landmark("Tower Bridge", "London", "United Kingdom", 51.5055, -0.0754, 4.0),
    Landmark("Buckingham Palace", "London", "United Kingdom", 51.5014, -0.1419, 4.0),
    Landmark("Westminster Abbey", "London", "United Kingdom", 51.4993, -0.1273, 4.0),
    Landmark("Trevi Fountain", "Rome", "Italy", 41.9009, 12.4833, 4.0),
    Landmark("St. Peter's Basilica", "Vatican City", "Vatican", 41.9022, 12.4539, 4.0),
    Landmark("Notre-Dame Cathedral", "Paris", "France", 48.8530, 2.3499, 4.0, "Notre-Dame de Paris"),
    Landmark("Arc de Triomphe", "Paris", "France", 48.8738, 2.2950, 4.0),
    Landmark("Palace of Versailles", "Versailles", "France", 48.8049, 2.1204, 4.0),
    Landmark("Berlin Wall", "Berlin", "Germany", 52.5351, 13.3903, 4.0),
    Landmark("Charles Bridge", "Prague", "Czechia", 50.0865, 14.4114, 4.0),
    Landmark("Prague Castle", "Prague", "Czechia", 50.0911, 14.4016, 4.0),
    Landmark("Wawel Castle", "Krakow", "Poland", 50.0540, 19.9352, 4.0),
    Landmark("Fisherman's Bastion", "Budapest", "Hungary", 47.5022, 19.0348, 4.0),
    Landmark("Louvre", "Paris", "France", 48.8606, 2.3376, 4.0, "Louvre"),
    Landmark("Shibuya Crossing", "Tokyo", "Japan", 35.6595, 139.7005, 4.0),
]
