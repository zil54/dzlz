from dataclasses import dataclass


@dataclass(frozen=True)
class GeographyFeature:
    category: str
    name: str
    latitude: float
    longitude: float
    countries: tuple[str, ...]
    zoom_degrees: float = 18.0


MAJOR_MOUNTAINS_AND_RANGES = [
    GeographyFeature("mountain", "Everest", 27.9881, 86.9250, ("Nepal", "China"), 8.0),
    GeographyFeature("mountain", "K2", 35.8808, 76.5158, ("Pakistan", "China"), 8.0),
    GeographyFeature("mountain", "Kilimanjaro", -3.0674, 37.3556, ("Tanzania",), 8.0),
    GeographyFeature("mountain", "Denali", 63.0695, -151.0074, ("United States of America",), 12.0),
    GeographyFeature("mountain", "Aconcagua", -32.6532, -70.0109, ("Argentina",), 8.0),
    GeographyFeature("mountain", "Mount Fuji", 35.3606, 138.7274, ("Japan",), 8.0),
    GeographyFeature("mountain range", "Andes", -22.0, -68.0, ("Argentina", "Bolivia", "Chile", "Colombia", "Ecuador", "Peru", "Venezuela"), 35.0),
    GeographyFeature("mountain range", "Himalayas", 28.0, 84.0, ("Bhutan", "China", "India", "Nepal", "Pakistan"), 22.0),
    GeographyFeature("mountain range", "Alps", 46.5, 10.0, ("Austria", "France", "Germany", "Italy", "Slovenia", "Switzerland"), 14.0),
    GeographyFeature("mountain range", "Rocky Mountains", 43.0, -110.0, ("Canada", "United States of America"), 28.0),
    GeographyFeature("mountain range", "Atlas Mountains", 31.0, -7.0, ("Algeria", "Morocco", "Tunisia"), 16.0),
    GeographyFeature("mountain range", "Ural Mountains", 60.0, 60.0, ("Kazakhstan", "Russia"), 24.0),
]


MAJOR_RIVERS = [
    GeographyFeature("river", "Nile", 26.0, 31.0, ("Egypt", "Sudan", "South Sudan", "Uganda"), 24.0),
    GeographyFeature("river", "Amazon River", -3.0, -60.0, ("Brazil", "Colombia", "Peru"), 24.0),
    GeographyFeature("river", "Yangtze River", 30.8, 112.0, ("China",), 20.0),
    GeographyFeature("river", "Mississippi River", 35.0, -90.0, ("United States of America",), 20.0),
    GeographyFeature("river", "Danube", 45.5, 20.0, ("Germany", "Austria", "Hungary", "Romania", "Serbia", "Slovakia", "Ukraine"), 22.0),
    GeographyFeature("river", "Ganges", 25.3, 83.0, ("Bangladesh", "India"), 16.0),
    GeographyFeature("river", "Mekong", 16.0, 104.0, ("Cambodia", "China", "Laos", "Myanmar", "Thailand", "Vietnam"), 22.0),
    GeographyFeature("river", "Congo River", -2.0, 18.0, ("Angola", "Democratic Republic of the Congo", "Republic of the Congo"), 24.0),
    GeographyFeature("river", "Volga", 54.0, 46.0, ("Russia",), 18.0),
    GeographyFeature("river", "Rhine", 49.0, 7.0, ("France", "Germany", "Netherlands", "Switzerland"), 12.0),
]


MAJOR_LAKES = [
    GeographyFeature("lake", "Lake Baikal", 53.5, 108.0, ("Russia",), 10.0),
    GeographyFeature("lake", "Lake Victoria", -1.0, 33.0, ("Kenya", "Tanzania", "Uganda"), 12.0),
    GeographyFeature("lake", "Lake Superior", 47.7, -87.5, ("Canada", "United States of America"), 12.0),
    GeographyFeature("lake", "Caspian Sea", 41.7, 50.7, ("Azerbaijan", "Iran", "Kazakhstan", "Russia", "Turkmenistan"), 18.0),
    GeographyFeature("lake", "Lake Tanganyika", -6.5, 29.6, ("Burundi", "Democratic Republic of the Congo", "Tanzania", "Zambia"), 12.0),
    GeographyFeature("lake", "Lake Titicaca", -15.8, -69.4, ("Bolivia", "Peru"), 8.0),
    GeographyFeature("lake", "Lake Malawi", -12.2, 34.4, ("Malawi", "Mozambique", "Tanzania"), 10.0),
    GeographyFeature("lake", "Great Bear Lake", 66.0, -120.0, ("Canada",), 10.0),
    GeographyFeature("lake", "Lake Ladoga", 60.8, 31.5, ("Russia",), 8.0),
    GeographyFeature("lake", "Lake Chad", 13.0, 14.0, ("Cameroon", "Chad", "Niger", "Nigeria"), 10.0),
]


OCEANS = [
    GeographyFeature("ocean", "Pacific Ocean", 0.0, -150.0, (), 65.0),
    GeographyFeature("ocean", "Atlantic Ocean", 0.0, -30.0, (), 55.0),
    GeographyFeature("ocean", "Indian Ocean", -20.0, 80.0, (), 55.0),
    GeographyFeature("ocean", "Arctic Ocean", 78.0, 0.0, (), 45.0),
    GeographyFeature("ocean", "Southern Ocean", -62.0, 40.0, (), 55.0),
]


MAJOR_SEAS = [
    GeographyFeature("sea", "Mediterranean Sea", 35.0, 18.0, ("Italy", "Greece", "Turkey", "Egypt"), 22.0),
    GeographyFeature("sea", "Caribbean Sea", 15.0, -75.0, ("Cuba", "Jamaica", "Colombia", "Venezuela"), 18.0),
    GeographyFeature("sea", "South China Sea", 13.0, 115.0, ("China", "Philippines", "Vietnam", "Malaysia"), 18.0),
    GeographyFeature("sea", "Arabian Sea", 15.0, 65.0, ("India", "Oman", "Pakistan", "Yemen"), 20.0),
    GeographyFeature("sea", "Red Sea", 20.0, 38.0, ("Egypt", "Israel", "Saudi Arabia", "Sudan", "Yemen"), 12.0),
    GeographyFeature("sea", "Black Sea", 43.5, 35.0, ("Turkey", "Ukraine", "Russia", "Georgia"), 10.0),
    GeographyFeature("sea", "Baltic Sea", 58.0, 20.0, ("Sweden", "Finland", "Poland", "Germany"), 14.0),
    GeographyFeature("sea", "North Sea", 56.0, 3.0, ("United Kingdom", "Norway", "Denmark", "Netherlands"), 12.0),
    GeographyFeature("sea", "Bering Sea", 58.0, -175.0, ("United States of America", "Russia"), 16.0),
    GeographyFeature("sea", "Sea of Japan", 40.0, 135.0, ("Japan", "Russia", "South Korea", "North Korea"), 12.0),
]


MAJOR_DESERTS = [
    GeographyFeature("desert", "Sahara", 23.5, 13.0, ("Algeria", "Egypt", "Libya", "Mali", "Morocco", "Niger", "Sudan", "Tunisia"), 35.0),
    GeographyFeature("desert", "Gobi Desert", 42.5, 103.0, ("China", "Mongolia"), 20.0),
    GeographyFeature("desert", "Arabian Desert", 23.0, 45.0, ("Saudi Arabia", "Oman", "United Arab Emirates", "Yemen"), 20.0),
    GeographyFeature("desert", "Kalahari Desert", -23.0, 22.0, ("Botswana", "Namibia", "South Africa"), 18.0),
    GeographyFeature("desert", "Atacama Desert", -24.5, -69.25, ("Chile", "Peru"), 12.0),
    GeographyFeature("desert", "Mojave Desert", 35.0, -115.5, ("United States of America",), 10.0),
    GeographyFeature("desert", "Great Victoria Desert", -29.0, 129.0, ("Australia",), 18.0),
    GeographyFeature("desert", "Patagonian Desert", -45.0, -68.0, ("Argentina",), 18.0),
    GeographyFeature("desert", "Syrian Desert", 33.0, 39.0, ("Syria", "Iraq", "Jordan", "Saudi Arabia"), 14.0),
    GeographyFeature("desert", "Thar Desert", 27.0, 71.0, ("India", "Pakistan"), 10.0),
]


GEOGRAPHY_FEATURES = [
    *MAJOR_MOUNTAINS_AND_RANGES,
    *MAJOR_RIVERS,
    *MAJOR_LAKES,
    *OCEANS,
    *MAJOR_SEAS,
    *MAJOR_DESERTS,
]

CONTINENTS = ["Africa", "Antarctica", "Asia", "Europe", "North America", "Oceania", "South America"]
