import geopandas as gpd

from Games.TestPrepsGames.geography_data import IMAGE_DIR, SHAPEFILE_PATH, iter_country_capitals
from Games.TestPrepsGames.seed_geography_maps import QUESTION_DIRECTIONS, image_filename, render_country_map


def generate_all_maps():
    world = gpd.read_file(SHAPEFILE_PATH)
    IMAGE_DIR.mkdir(exist_ok=True)

    generated = 0
    for country_capital in iter_country_capitals(world):
        for direction in QUESTION_DIRECTIONS:
            image_path = image_filename(country_capital.country, direction)
            image_path.write_bytes(render_country_map(world, country_capital, direction))
            generated += 1
            print(f"Saved {image_path}")

    return generated


if __name__ == "__main__":
    total = generate_all_maps()
    print(f"Generated {total} country/capital map images.")