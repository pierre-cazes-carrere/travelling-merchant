
import csv
import math
from pathlib import Path

import matplotlib.pyplot as plt

CSV_PATH = Path(__file__).parent / "villes_france_lat_long.csv"


def cities_listing(path: Path = CSV_PATH) -> dict[str, tuple[float, float]]:
    """Lit le CSV et retourne un dict {nom_ville: (latitude, longitude)}."""
    cities_coordinates = {}

    with open(path, encoding="utf-8-sig") as f:
        reader = csv.reader(f)
        next(reader, None)  # ignore la ligne d'en-tête
        for row in reader:
            name, lat, lon = row[0].strip(), row[1].strip(), row[2].strip()

            try:
                cities_coordinates[name] = (float(lat), float(lon))
            except ValueError:
                continue

    return cities_coordinates


def haversine(coord1: tuple[float, float], coord2: tuple[float, float]) -> float:
    R = 6371.0  # Earth's mean radius in km

    lat1, lon1 = coord1
    lat2, lon2 = coord2

    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = (
        math.sin(delta_phi / 2) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c


def calculated_distance(
    cities_coordinates: dict[str, tuple[float, float]], city1: str, city2: str
) -> float:
    return haversine(cities_coordinates[city1], cities_coordinates[city2])


def build_distance_matrix(cities: dict[str, tuple[float, float]]) -> list[list[float]]:
    coords = list(cities.values())
    n = len(coords)
    matrix = [[0.0] * n for _ in range(n)]

    for i in range(n):
        for j in range(i + 1, n):
            d = haversine(coords[i], coords[j])
            matrix[i][j] = d
            matrix[j][i] = d  # symétrique

    return matrix


def display_map(cities: dict[str, tuple[float, float]]) -> None:
    if not cities:
        raise ValueError("The cities dictionary is empty.")

    lats = [lat for lat, lon in cities.values()]
    lons = [lon for lat, lon in cities.values()]
    names = list(cities.keys())

    plt.figure(figsize=(10, 10))
    plt.scatter(lons, lats, s=15, color="tab:red")

    for name, lon, lat in zip(names, lons, lats):
        plt.annotate(name, (lon, lat), fontsize=7, xytext=(3, 3), textcoords="offset points")

    plt.xlabel("Longitude")
    plt.ylabel("Latitude")
    plt.title("Villes de France")
    plt.gca().set_aspect("equal")
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    cities = cities_listing()
    print(f"{len(cities)} cities loaded.")

    names = list(cities.keys())
    if len(names) >= 2:
        city1, city2 = names[0], names[1]
        distance = calculated_distance(cities, city1, city2)
        print(f"Distance between {city1} and {city2}: {distance:.2f} km")

    display_map(cities)
