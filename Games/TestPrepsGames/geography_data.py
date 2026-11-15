from dataclasses import dataclass
from pathlib import Path

from countryinfo import all_countries


BASE_DIR = Path(__file__).resolve().parent
SHAPEFILE_PATH = BASE_DIR / "data" / "ne_110m_admin_0_countries" / "ne_110m_admin_0_countries.shp"
IMAGE_DIR = BASE_DIR / "images"


@dataclass(frozen=True)
class CountryCapital:
    country: str
    capital: str
    longitude: float
    latitude: float
    iso_a3: str


CAPITAL_OVERRIDES = {
    "East Timor": ("Dili", 125.5603, -8.5569, "TLS"),
    "Israel": ("Jerusalem", 35.2137, 31.7683, "ISR"),
    "Palestine": ("East Jerusalem (Projected)", 35.2433, 31.7784, "PSE"),
    "Puerto Rico": ("San Juan", -66.1057, 18.4655, "PRI"),
    "United Kingdom": ("London", -0.127647, 51.507322, "GBR"),
    "Kosovo": ("Pristina", 21.1655, 42.6629, "XKX"),
    "Somaliland": ("Hargeisa", 44.064, 9.56, "SOL"),
}

EXCLUDED_COUNTRIES = {
    "Northern Cyprus",
}


def _countryinfo_indexes():
    by_iso3 = {}
    by_name = {}

    for country in all_countries():
        info = country.info()
        iso = info.get("ISO") or {}
        iso3 = iso.get("alpha3")
        if iso3:
            by_iso3[iso3.upper()] = info

        names = [
            info.get("name"),
            info.get("nativeName"),
            *(info.get("altSpellings") or []),
        ]
        names.extend(
            value
            for value in (info.get("translations") or {}).values()
            if isinstance(value, str)
        )

        for name in names:
            if name:
                by_name[name.casefold()] = info

    return by_iso3, by_name


def _countryinfo_match(row, by_iso3, by_name):
    for field in ("ISO_A3", "ADM0_A3"):
        iso3 = str(row.get(field) or "").upper()
        if iso3 in by_iso3:
            return by_iso3[iso3]

    for field in ("ADMIN", "NAME", "NAME_LONG", "SOVEREIGNT"):
        name = str(row.get(field) or "").casefold()
        if name in by_name:
            return by_name[name]

    return None


def _country_capital_from_info(row, info):
    capital = info.get("capital")
    capital_latlng = info.get("capital_latlng")
    if not capital or not capital_latlng or len(capital_latlng) != 2:
        return None

    latitude, longitude = capital_latlng
    return CountryCapital(
        country=row["ADMIN"],
        capital=capital,
        longitude=float(longitude),
        latitude=float(latitude),
        iso_a3=row.get("ISO_A3") or row.get("ADM0_A3") or "",
    )


def iter_country_capitals(world):
    by_iso3, by_name = _countryinfo_indexes()

    for _, row in world.sort_values("ADMIN").iterrows():
        country = row["ADMIN"]
        if country in EXCLUDED_COUNTRIES:
            continue

        override = CAPITAL_OVERRIDES.get(country)
        if override:
            capital, longitude, latitude, iso_a3 = override
            yield CountryCapital(country, capital, longitude, latitude, iso_a3)
            continue

        info = _countryinfo_match(row, by_iso3, by_name)
        if not info:
            continue

        country_capital = _country_capital_from_info(row, info)
        if country_capital:
            yield country_capital
