from io import BytesIO
import json
import os
import time
from urllib.parse import quote
from urllib.request import Request, urlopen, urlretrieve
from zipfile import ZipFile

os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("NUMEXPR_NUM_THREADS", "1")

import geopandas as gpd
import matplotlib
import pandas as pd

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import matplotlib.patheffects as path_effects
import psycopg2
from PIL import Image, ImageDraw, ImageFont, ImageOps
from shapely.geometry import Point, Polygon
from shapely.ops import nearest_points

from Games.TestPrepsGames.db_config import get_db_config
from Games.TestPrepsGames.geography_features import CONTINENTS, GEOGRAPHY_FEATURES, GeographyFeature
from Games.TestPrepsGames.geography_data import IMAGE_DIR, SHAPEFILE_PATH, iter_country_capitals
from Games.TestPrepsGames.landmarks import LANDMARKS, Landmark
from Games.TestPrepsGames.political_entities import UK_CONSTITUENT_COUNTRY_CAPITALS
from Games.TestPrepsGames.us_geography import (
    US_STATES_DATA_DIR,
    US_STATES_SHAPEFILE,
    US_STATES_ZIP_URL,
    US_STATE_CAPITALS,
    USStateCapital,
)


QUESTION_DIRECTIONS = ("country_to_capital", "capital_to_country")
MAP_DPI = 240
WIKIPEDIA_SUMMARY_URL = "https://en.wikipedia.org/api/rest_v1/page/summary/{title}"
HTTP_HEADERS = {"User-Agent": "TestPrepsGames geography quiz image seeder"}
LANDMARK_IMAGE_CACHE_DIR = IMAGE_DIR / "landmark_cache"
CRIMEA_DISPLAY_POLYGON = Polygon(
    [
        (32.45, 46.10),
        (33.15, 46.05),
        (34.15, 45.85),
        (35.20, 45.35),
        (36.55, 45.35),
        (36.75, 44.90),
        (35.90, 44.45),
        (34.80, 44.35),
        (33.75, 44.45),
        (32.95, 44.65),
        (32.50, 45.20),
        (32.45, 46.10),
    ]
)


def ensure_schema(cursor):
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS geography_maps (
            id SERIAL PRIMARY KEY,
            country TEXT NOT NULL,
            capital TEXT NOT NULL,
            image_path TEXT,
            direction TEXT NOT NULL,
            image_data BYTEA,
            image_mime TEXT NOT NULL DEFAULT 'image/png',
            iso_a3 TEXT,
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        )
        """
    )
    cursor.execute("ALTER TABLE geography_maps ADD COLUMN IF NOT EXISTS image_data BYTEA")
    cursor.execute("ALTER TABLE geography_maps ADD COLUMN IF NOT EXISTS image_mime TEXT NOT NULL DEFAULT 'image/png'")
    cursor.execute("ALTER TABLE geography_maps ADD COLUMN IF NOT EXISTS iso_a3 TEXT")
    cursor.execute("ALTER TABLE geography_maps ADD COLUMN IF NOT EXISTS created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()")
    cursor.execute("ALTER TABLE geography_maps ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()")
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS geography_questions (
            id SERIAL PRIMARY KEY,
            category TEXT NOT NULL,
            prompt TEXT NOT NULL,
            answer TEXT NOT NULL,
            answer_kind TEXT NOT NULL,
            image_path TEXT,
            image_data BYTEA,
            image_mime TEXT NOT NULL DEFAULT 'image/png',
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        )
        """
    )
    cursor.execute("ALTER TABLE geography_questions ADD COLUMN IF NOT EXISTS answer_kind TEXT NOT NULL DEFAULT 'feature'")
    cursor.execute("ALTER TABLE geography_questions ADD COLUMN IF NOT EXISTS image_data BYTEA")
    cursor.execute("ALTER TABLE geography_questions ADD COLUMN IF NOT EXISTS image_mime TEXT NOT NULL DEFAULT 'image/png'")


def render_country_map(world, country_capital, direction):
    country_shape = display_country_shape(world, country_capital.country)
    if country_shape.empty:
        raise ValueError(f"Country '{country_capital.country}' not found in Natural Earth shapefile.")

    fig, ax = plt.subplots(figsize=(8, 6), dpi=MAP_DPI)
    country_shape.plot(ax=ax, color="#b7e4a2", edgecolor="#1f1f1f", linewidth=1.4)
    ax.axis("off")
    ax.margins(0.08)
    fig.patch.set_facecolor("white")

    label_point = country_shape.representative_point().iloc[0]
    if direction == "country_to_capital":
        label = ax.text(
            label_point.x,
            label_point.y,
            country_capital.country,
            ha="center",
            va="center",
            fontsize=22,
            weight="bold",
            color="#111111",
        )
        label.set_path_effects([path_effects.withStroke(linewidth=5, foreground="white")])
        add_palestine_region_labels(ax, country_capital.country)
    else:
        capital_point = display_capital_point(country_shape, country_capital)
        ax.plot(
            capital_point.x,
            capital_point.y,
            marker="o",
            markersize=13,
            markerfacecolor="#d7191c",
            markeredgecolor="white",
            markeredgewidth=2,
        )
        ax.text(
            capital_point.x + 0.5,
            capital_point.y + 0.5,
            country_capital.capital,
            fontsize=18,
            ha="left",
            va="bottom",
            color="#b00000",
            weight="bold",
            bbox={"facecolor": "white", "edgecolor": "none", "alpha": 0.85, "pad": 2},
        )
        add_palestine_region_labels(ax, country_capital.country)

    output = BytesIO()
    fig.savefig(output, format="png", dpi=MAP_DPI, bbox_inches="tight", pad_inches=0.08)
    plt.close(fig)
    return output.getvalue()


def add_palestine_region_labels(ax, country):
    if country != "Palestine":
        return

    for label, longitude, latitude in (
        ("West Bank", 35.25, 31.95),
        ("Gaza Strip", 34.36, 31.43),
    ):
        text = ax.text(
            longitude,
            latitude,
            label,
            ha="center",
            va="center",
            fontsize=13,
            weight="bold",
            color="#111111",
        )
        text.set_path_effects([path_effects.withStroke(linewidth=4, foreground="white")])


def display_capital_point(country_shape, country_capital):
    capital_point = Point(country_capital.longitude, country_capital.latitude)
    country_geometry = country_shape.geometry.union_all()
    if country_geometry.contains(capital_point) or country_geometry.touches(capital_point):
        return capital_point

    if country_geometry.distance(capital_point) > 0.25:
        return nearest_points(country_geometry, capital_point)[0]

    return capital_point


def display_country_shape(world, country):
    country_shape = world[world["ADMIN"] == country].copy()
    if country_shape.empty:
        return country_shape

    extras = []
    if country == "Cyprus":
        northern_cyprus = world[world["ADMIN"] == "Northern Cyprus"].copy()
        if not northern_cyprus.empty:
            extras.append(northern_cyprus)

    if country == "Ukraine":
        extras.append(
            gpd.GeoDataFrame(
                [{"ADMIN": "Ukraine", "geometry": CRIMEA_DISPLAY_POLYGON}],
                geometry="geometry",
                crs=world.crs,
            )
        )

    if extras:
        return gpd.GeoDataFrame(
            pd.concat([country_shape, *extras], ignore_index=True),
            geometry="geometry",
            crs=world.crs,
        )

    return country_shape


def image_filename(country, direction):
    suffix = "country" if direction == "country_to_capital" else "capital"
    safe_country = country.lower().replace(" ", "_").replace("/", "_")
    return IMAGE_DIR / f"{safe_country}_{suffix}.png"


def feature_image_filename(name, question_kind):
    safe_name = name.lower().replace(" ", "_").replace("/", "_")
    return IMAGE_DIR / f"{safe_name}_{question_kind}.png"


def text_card_filename(name, question_kind):
    safe_name = name.lower().replace(" ", "_").replace("/", "_").replace("'", "")
    return IMAGE_DIR / f"{safe_name}_{question_kind}.png"


def frame_map(ax, longitude, latitude, zoom_degrees):
    half_width = zoom_degrees
    half_height = zoom_degrees * 0.65
    ax.set_xlim(max(-180, longitude - half_width), min(180, longitude + half_width))
    ax.set_ylim(max(-85, latitude - half_height), min(85, latitude + half_height))


def render_feature_map(world, feature: GeographyFeature, show_name=False, show_countries=False):
    fig, ax = plt.subplots(figsize=(8, 6), dpi=MAP_DPI)
    world.plot(ax=ax, color="#eeeeee", edgecolor="#777777", linewidth=0.6)
    if show_countries and feature.countries:
        country_shapes = world[world["ADMIN"].isin(feature.countries)]
        if not country_shapes.empty:
            country_shapes.plot(ax=ax, color="#b7e4a2", edgecolor="#1f1f1f", linewidth=1.0)
            for _, row in country_shapes.iterrows():
                label_point = row.geometry.representative_point()
                label = ax.text(
                    label_point.x,
                    label_point.y,
                    row["ADMIN"],
                    ha="center",
                    va="center",
                    fontsize=12,
                    weight="bold",
                    color="#111111",
                )
                label.set_path_effects([path_effects.withStroke(linewidth=4, foreground="white")])
    ax.axis("off")
    ax.margins(0.04)
    fig.patch.set_facecolor("white")
    frame_map(ax, feature.longitude, feature.latitude, feature.zoom_degrees)

    marker_color = "#1f78b4" if feature.category in {"lake", "ocean", "river", "sea"} else "#d95f02"
    ax.plot(
        feature.longitude,
        feature.latitude,
        marker="o",
        markersize=14,
        markerfacecolor=marker_color,
        markeredgecolor="white",
        markeredgewidth=2,
    )
    if show_name:
        ax.text(
            feature.longitude + 0.8,
            feature.latitude + 0.8,
            feature.name,
            fontsize=18,
            ha="left",
            va="bottom",
            color="#111111",
            weight="bold",
            bbox={"facecolor": "white", "edgecolor": "none", "alpha": 0.88, "pad": 2},
        )
    elif show_countries and feature.countries:
        ax.text(
            0.02,
            0.03,
            f"Major country/countries: {', '.join(feature.countries)}",
            fontsize=14,
            ha="left",
            va="bottom",
            color="#111111",
            weight="bold",
            bbox={"facecolor": "white", "edgecolor": "#bbbbbb", "alpha": 0.9, "pad": 4},
            transform=ax.transAxes,
        )

    output = BytesIO()
    fig.savefig(output, format="png", dpi=MAP_DPI, bbox_inches="tight", pad_inches=0.08)
    plt.close(fig)
    return output.getvalue()


def render_country_context_map(world, country):
    country_shape = display_country_shape(world, country)
    if country_shape.empty:
        raise ValueError(f"Country '{country}' not found in Natural Earth shapefile.")

    fig, ax = plt.subplots(figsize=(8, 6), dpi=MAP_DPI)
    world.plot(ax=ax, color="#eeeeee", edgecolor="#888888", linewidth=0.5)
    country_shape.plot(ax=ax, color="#b7e4a2", edgecolor="#1f1f1f", linewidth=1.2)
    ax.axis("off")
    ax.margins(0.06)
    fig.patch.set_facecolor("white")

    label_point = country_shape.representative_point().iloc[0]
    label = ax.text(
        label_point.x,
        label_point.y,
        country,
        ha="center",
        va="center",
        fontsize=18,
        weight="bold",
        color="#111111",
    )
    label.set_path_effects([path_effects.withStroke(linewidth=5, foreground="white")])

    minx, miny, maxx, maxy = country_shape.total_bounds
    width = max(maxx - minx, 8)
    height = max(maxy - miny, 5)
    ax.set_xlim(max(-180, minx - width * 0.5), min(180, maxx + width * 0.5))
    ax.set_ylim(max(-85, miny - height * 0.5), min(85, maxy + height * 0.5))

    output = BytesIO()
    fig.savefig(output, format="png", dpi=MAP_DPI, bbox_inches="tight", pad_inches=0.08)
    plt.close(fig)
    return output.getvalue()


def render_text_card(title, subtitle=None):
    fig, ax = plt.subplots(figsize=(8, 4.8), dpi=MAP_DPI)
    ax.axis("off")
    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")
    ax.text(
        0.5,
        0.58 if subtitle else 0.5,
        title,
        ha="center",
        va="center",
        fontsize=32,
        weight="bold",
        color="#111111",
        wrap=True,
        transform=ax.transAxes,
    )
    if subtitle:
        ax.text(
            0.5,
            0.35,
            subtitle,
            ha="center",
            va="center",
            fontsize=20,
            color="#444444",
            wrap=True,
            transform=ax.transAxes,
        )

    output = BytesIO()
    fig.savefig(output, format="png", dpi=MAP_DPI, bbox_inches="tight", pad_inches=0.08)
    plt.close(fig)
    return output.getvalue()


def render_landmark_map(world, landmark: Landmark):
    fig, ax = plt.subplots(figsize=(8, 6), dpi=MAP_DPI)
    world.plot(ax=ax, color="#eeeeee", edgecolor="#777777", linewidth=0.6)
    country_shape = world[world["ADMIN"] == landmark.country]
    if not country_shape.empty:
        country_shape.plot(ax=ax, color="#b7e4a2", edgecolor="#1f1f1f", linewidth=1.0)
    ax.axis("off")
    ax.margins(0.04)
    fig.patch.set_facecolor("white")
    frame_map(ax, landmark.longitude, landmark.latitude, landmark.zoom_degrees)
    ax.plot(
        landmark.longitude,
        landmark.latitude,
        marker="*",
        markersize=20,
        markerfacecolor="#d95f02",
        markeredgecolor="white",
        markeredgewidth=1.6,
    )
    ax.text(
        landmark.longitude + 0.4,
        landmark.latitude + 0.4,
        f"{landmark.city_or_region}, {landmark.country}",
        fontsize=16,
        ha="left",
        va="bottom",
        color="#111111",
        weight="bold",
        bbox={"facecolor": "white", "edgecolor": "none", "alpha": 0.88, "pad": 2},
    )

    output = BytesIO()
    fig.savefig(output, format="png", dpi=MAP_DPI, bbox_inches="tight", pad_inches=0.08)
    plt.close(fig)
    return output.getvalue()


def fetch_url_bytes(url):
    request = Request(url, headers=HTTP_HEADERS)
    with urlopen(request, timeout=30) as response:
        return response.read()


def wikipedia_thumbnail_url(landmark: Landmark):
    title = quote(landmark.wikipedia_title or landmark.name.replace(" ", "_"), safe="")
    data = json.loads(fetch_url_bytes(WIKIPEDIA_SUMMARY_URL.format(title=title)).decode("utf-8"))
    thumbnail = data.get("thumbnail") or data.get("originalimage") or {}
    return thumbnail.get("source")


def render_landmark_photo(landmark: Landmark):
    cached_path = landmark_cache_path(landmark)
    if cached_path.exists():
        return cached_path.read_bytes()

    thumbnail_url = wikipedia_thumbnail_url(landmark)
    if not thumbnail_url:
        raise ValueError(f"No Wikipedia thumbnail found for {landmark.name}.")

    time.sleep(1.0)
    source = Image.open(BytesIO(fetch_url_bytes(thumbnail_url))).convert("RGB")
    source = ImageOps.contain(source, (1100, 720), Image.Resampling.LANCZOS)

    canvas = Image.new("RGB", (1100, 820), "white")
    image_x = (canvas.width - source.width) // 2
    canvas.paste(source, (image_x, 0))

    draw = ImageDraw.Draw(canvas)
    title_font = ImageFont.load_default(size=38)
    subtitle_font = ImageFont.load_default(size=24)
    title = "What is this famous landmark?"
    subtitle = f"{landmark.city_or_region}, {landmark.country}"
    draw.text((canvas.width // 2, 750), title, anchor="mm", fill="#111111", font=title_font)
    draw.text((canvas.width // 2, 790), subtitle, anchor="mm", fill="#444444", font=subtitle_font)

    output = BytesIO()
    canvas.save(output, format="PNG")
    image_data = output.getvalue()
    LANDMARK_IMAGE_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cached_path.write_bytes(image_data)
    return image_data


def landmark_cache_path(landmark):
    safe_name = landmark.name.lower().replace(" ", "_").replace("/", "_").replace("'", "")
    return LANDMARK_IMAGE_CACHE_DIR / f"{safe_name}.png"


def render_landmark_question_image(world, landmark: Landmark):
    try:
        return render_landmark_photo(landmark)
    except Exception as error:
        print(f"Using map fallback for {landmark.name}: {error}")
        return render_landmark_map(world, landmark)


def ensure_us_states_shapefile():
    if US_STATES_SHAPEFILE.exists():
        return

    US_STATES_DATA_DIR.mkdir(parents=True, exist_ok=True)
    zip_path = US_STATES_DATA_DIR / "cb_2023_us_state_20m.zip"
    if not zip_path.exists():
        urlretrieve(US_STATES_ZIP_URL, zip_path)

    with ZipFile(zip_path) as archive:
        archive.extractall(US_STATES_DATA_DIR)


def load_us_states():
    ensure_us_states_shapefile()
    states = gpd.read_file(US_STATES_SHAPEFILE)
    state_names = {state_capital.state for state_capital in US_STATE_CAPITALS}
    return states[states["NAME"].isin(state_names)]


def render_us_state_map(us_states, state_capital: USStateCapital, direction):
    state_shape = us_states[us_states["NAME"] == state_capital.state]
    if state_shape.empty:
        raise ValueError(f"State '{state_capital.state}' not found in Census state shapefile.")

    fig, ax = plt.subplots(figsize=(8, 6), dpi=MAP_DPI)
    us_states.plot(ax=ax, color="#eeeeee", edgecolor="#999999", linewidth=0.45)
    state_shape.plot(ax=ax, color="#b7e4a2", edgecolor="#1f1f1f", linewidth=1.3)
    ax.axis("off")
    ax.margins(0.06)
    fig.patch.set_facecolor("white")

    if direction == "state_to_capital":
        label_point = state_shape.representative_point().iloc[0]
        label = ax.text(
            label_point.x,
            label_point.y,
            f"{state_capital.state} ({state_capital.abbreviation})",
            ha="center",
            va="center",
            fontsize=18,
            weight="bold",
            color="#111111",
        )
        label.set_path_effects([path_effects.withStroke(linewidth=5, foreground="white")])
    else:
        ax.plot(
            state_capital.longitude,
            state_capital.latitude,
            marker="o",
            markersize=13,
            markerfacecolor="#d7191c",
            markeredgecolor="white",
            markeredgewidth=2,
        )
        ax.text(
            state_capital.longitude + 0.35,
            state_capital.latitude + 0.35,
            state_capital.capital,
            fontsize=18,
            ha="left",
            va="bottom",
            color="#b00000",
            weight="bold",
            bbox={"facecolor": "white", "edgecolor": "none", "alpha": 0.85, "pad": 2},
        )

    minx, miny, maxx, maxy = state_shape.total_bounds
    width = max(maxx - minx, 2.5)
    height = max(maxy - miny, 2.5)
    ax.set_xlim(minx - width * 0.22, maxx + width * 0.22)
    ax.set_ylim(miny - height * 0.22, maxy + height * 0.22)

    output = BytesIO()
    fig.savefig(output, format="png", dpi=MAP_DPI, bbox_inches="tight", pad_inches=0.08)
    plt.close(fig)
    return output.getvalue()


def render_continent_map(world, continent):
    fig, ax = plt.subplots(figsize=(8, 6), dpi=MAP_DPI)
    world.plot(ax=ax, color="#eeeeee", edgecolor="#888888", linewidth=0.5)
    continent_shape = world[world["CONTINENT"] == continent]
    continent_shape.plot(ax=ax, color="#b7e4a2", edgecolor="#1f1f1f", linewidth=1.0)
    ax.axis("off")
    ax.margins(0.04)
    fig.patch.set_facecolor("white")

    minx, miny, maxx, maxy = continent_shape.total_bounds
    width = maxx - minx
    height = maxy - miny
    ax.set_xlim(max(-180, minx - width * 0.1), min(180, maxx + width * 0.1))
    ax.set_ylim(max(-85, miny - height * 0.1), min(85, maxy + height * 0.1))

    output = BytesIO()
    fig.savefig(output, format="png", dpi=MAP_DPI, bbox_inches="tight", pad_inches=0.08)
    plt.close(fig)
    return output.getvalue()


def upsert_question(cursor, country_capital, direction, image_path, image_data):
    cursor.execute(
        """
        UPDATE geography_maps
        SET capital = %s,
            image_path = %s,
            image_data = %s,
            image_mime = 'image/png',
            iso_a3 = %s,
            updated_at = NOW()
        WHERE country = %s
          AND direction = %s
        """,
        (
            country_capital.capital,
            str(image_path),
            psycopg2.Binary(image_data),
            country_capital.iso_a3,
            country_capital.country,
            direction,
        ),
    )

    if cursor.rowcount:
        return

    cursor.execute(
        """
        INSERT INTO geography_maps (
            country,
            capital,
            image_path,
            direction,
            image_data,
            image_mime,
            iso_a3,
            updated_at
        )
        VALUES (%s, %s, %s, %s, %s, 'image/png', %s, NOW())
        """,
        (
            country_capital.country,
            country_capital.capital,
            str(image_path),
            direction,
            psycopg2.Binary(image_data),
            country_capital.iso_a3,
        ),
    )


def upsert_generic_question(cursor, category, prompt, answer, answer_kind, image_path, image_data):
    cursor.execute(
        """
        UPDATE geography_questions
        SET answer_kind = %s,
            image_path = %s,
            image_data = %s,
            image_mime = 'image/png',
            updated_at = NOW()
        WHERE category = %s
          AND prompt = %s
          AND answer = %s
        """,
        (
            answer_kind,
            str(image_path),
            psycopg2.Binary(image_data),
            category,
            prompt,
            answer,
        ),
    )

    if cursor.rowcount:
        return

    cursor.execute(
        """
        INSERT INTO geography_questions (
            category,
            prompt,
            answer,
            answer_kind,
            image_path,
            image_data,
            image_mime,
            updated_at
        )
        VALUES (%s, %s, %s, %s, %s, %s, 'image/png', NOW())
        """,
        (
            category,
            prompt,
            answer,
            answer_kind,
            str(image_path),
            psycopg2.Binary(image_data),
        ),
    )


def seed_feature_questions(cursor, world):
    cursor.execute(
        """
        DELETE FROM geography_questions
        WHERE category IN ('mountain', 'mountain range', 'river', 'lake', 'ocean', 'sea', 'desert', 'continent')
        """
    )

    seeded = 0
    for feature in GEOGRAPHY_FEATURES:
        name_prompt = f"🗺️ What is the name of this {feature.category}?"
        name_image = render_feature_map(world, feature, show_countries=True)
        name_path = feature_image_filename(feature.name, "name")
        name_path.write_bytes(name_image)
        upsert_generic_question(cursor, feature.category, name_prompt, feature.name, feature.category, name_path, name_image)
        seeded += 1

        if feature.countries:
            country_prompt = feature_country_prompt(feature)
            country_answer = ", ".join(feature.countries)
            country_image = render_feature_map(world, feature, show_name=True)
            country_path = feature_image_filename(feature.name, "country")
            country_path.write_bytes(country_image)
            upsert_generic_question(
                cursor,
                feature.category,
                country_prompt,
                country_answer,
                "country",
                country_path,
                country_image,
            )
            seeded += 1

    for continent in CONTINENTS:
        prompt = "🗺️ What continent is highlighted?"
        image_data = render_continent_map(world, continent)
        image_path = feature_image_filename(continent, "continent")
        image_path.write_bytes(image_data)
        upsert_generic_question(cursor, "continent", prompt, continent, "continent", image_path, image_data)
        seeded += 1

    for country, continent in continent_country_questions(world):
        prompt = f"🗺️ What continent is {country} in?"
        image_data = render_country_context_map(world, country)
        image_path = feature_image_filename(country, "continent")
        image_path.write_bytes(image_data)
        upsert_generic_question(cursor, "continent", prompt, continent, "continent", image_path, image_data)
        seeded += 1

    return seeded


def seed_us_state_questions(cursor, us_states):
    cursor.execute(
        """
        DELETE FROM geography_questions
        WHERE category = 'us state'
        """
    )

    seeded = 0
    for state_capital in US_STATE_CAPITALS:
        state_prompt = "🗺️ What is the capital of this U.S. state?"
        state_image = render_us_state_map(us_states, state_capital, "state_to_capital")
        state_path = text_card_filename(state_capital.state, "us_state")
        state_path.write_bytes(state_image)
        upsert_generic_question(
            cursor,
            "us state",
            state_prompt,
            state_capital.capital,
            "us state capital",
            state_path,
            state_image,
        )
        seeded += 1

        capital_prompt = "🗺️ This is the capital of which U.S. state?"
        capital_image = render_us_state_map(us_states, state_capital, "capital_to_state")
        capital_path = text_card_filename(state_capital.capital, "us_state_capital")
        capital_path.write_bytes(capital_image)
        upsert_generic_question(
            cursor,
            "us state",
            capital_prompt,
            state_capital.state,
            "us state",
            capital_path,
            capital_image,
        )
        seeded += 1

    return seeded


def seed_landmark_questions(cursor, world):
    cursor.execute(
        """
        DELETE FROM geography_questions
        WHERE category = 'landmark'
        """
    )

    seeded = 0
    for landmark in LANDMARKS:
        prompt = "🗺️ What is the name of this famous landmark?"
        image_data = render_landmark_question_image(world, landmark)
        image_path = text_card_filename(landmark.name, "landmark")
        image_path.write_bytes(image_data)
        upsert_generic_question(
            cursor,
            "landmark",
            prompt,
            landmark.name,
            "landmark",
            image_path,
            image_data,
        )
        seeded += 1

    return seeded


def seed_political_entity_questions(cursor):
    cursor.execute(
        """
        DELETE FROM geography_questions
        WHERE category IN ('constituent country', 'political entities')
        """
    )

    seeded = 0
    for entity_capital in UK_CONSTITUENT_COUNTRY_CAPITALS:
        entity_prompt = "🗺️ What is the capital of this UK constituent political entity?"
        entity_image = render_text_card(entity_capital.entity, entity_capital.description)
        entity_path = text_card_filename(entity_capital.entity, "constituent_country")
        entity_path.write_bytes(entity_image)
        upsert_generic_question(
            cursor,
            "political entities",
            entity_prompt,
            entity_capital.capital,
            "capital",
            entity_path,
            entity_image,
        )
        seeded += 1

        capital_prompt = f"🗺️ {entity_capital.capital} is the capital of which UK constituent political entity?"
        capital_image = render_text_card(entity_capital.capital, "capital")
        capital_path = text_card_filename(entity_capital.capital, "constituent_country_capital")
        capital_path.write_bytes(capital_image)
        upsert_generic_question(
            cursor,
            "political entities",
            capital_prompt,
            entity_capital.entity,
            "uk constituent entity",
            capital_path,
            capital_image,
        )
        seeded += 1

    return seeded


def continent_country_questions(world):
    representative_countries = [
        "Brazil",
        "Canada",
        "China",
        "Egypt",
        "France",
        "Japan",
        "South Africa",
        "Australia",
        "Argentina",
        "India",
        "Russia",
        "United States of America",
    ]
    rows = world[world["ADMIN"].isin(representative_countries)]
    return [(row["ADMIN"], row["CONTINENT"]) for _, row in rows.iterrows()]


def feature_country_prompt(feature):
    if feature.category == "river":
        return f"🗺️ Name a major country the {feature.name} flows through."
    if feature.category == "lake":
        return f"🗺️ Name a major country bordering {feature.name}."
    if feature.category == "sea":
        return f"🗺️ Name a major country bordering the {feature.name}."
    if feature.category in {"mountain", "mountain range"}:
        return f"🗺️ Name a major country containing or bordering {feature.name}."
    if feature.category == "desert":
        return f"🗺️ Name a major country containing {feature.name}."
    return f"🗺️ Name a major country associated with {feature.name}."


def seed_geography_maps():
    world = gpd.read_file(SHAPEFILE_PATH)
    us_states = load_us_states()
    IMAGE_DIR.mkdir(exist_ok=True)

    conn = psycopg2.connect(**get_db_config())
    seeded = 0
    try:
        with conn:
            with conn.cursor() as cursor:
                ensure_schema(cursor)
                for country_capital in iter_country_capitals(world):
                    for direction in QUESTION_DIRECTIONS:
                        image_data = render_country_map(world, country_capital, direction)
                        image_path = image_filename(country_capital.country, direction)
                        image_path.write_bytes(image_data)
                        upsert_question(cursor, country_capital, direction, image_path, image_data)
                        seeded += 1
                seeded += seed_feature_questions(cursor, world)
                seeded += seed_us_state_questions(cursor, us_states)
                seeded += seed_political_entity_questions(cursor)
                seeded += seed_landmark_questions(cursor, world)
    finally:
        conn.close()

    return seeded


if __name__ == "__main__":
    total = seed_geography_maps()
    print(f"Seeded {total} geography map questions.")
