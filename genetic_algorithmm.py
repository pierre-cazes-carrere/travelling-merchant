
import argparse
import random

import matplotlib.pyplot as plt

from cities_data import build_distance_matrix, cities_listing


def fitness(tour: list[int], distances: list[list[float]]) -> float:

    total = sum(distances[tour[i]][tour[i + 1]] for i in range(len(tour) - 1))
    total += distances[tour[-1]][tour[0]]  # retour à la ville de départ
    return total


def selection(pop: list[list[int]], distances: list[list[float]], k: int = 3) -> list[int]:

    return min(random.sample(pop, k), key=lambda t: fitness(t, distances))


def order_crossover(p1: list[int], p2: list[int]) -> list[int]:

    size = len(p1)
    start, end = sorted(random.sample(range(size), 2))
    child = [-1] * size

    child[start:end] = p1[start:end]

    p2_filtered = [x for x in p2 if x not in child]
    child[:start] = p2_filtered[:start]
    child[end:] = p2_filtered[start:]

    return child


def build_nearest_neighbors(distances: list[list[float]], k: int = 5) -> list[list[int]]:
    n = len(distances)
    neighbors = []

    for i in range(n):
        autres = [j for j in range(n) if j != i]
        autres_tries = sorted(autres, key=lambda j: distances[i][j])
        neighbors.append(autres_tries[:k])

    return neighbors


def mutate(child: list[int], neighbors: list[list[int]]) -> list[int]:

    idx1 = random.randrange(len(child))
    city1 = child[idx1]

    # on choisit une ville proche parmi les voisines précalculées
    nearby_city = random.choice(neighbors[city1])
    idx2 = child.index(nearby_city)  # position de cette ville dans le parcours

    child[idx1], child[idx2] = child[idx2], child[idx1]
    return child


def genetic_algorithm(
    distances: list[list[float]],
    pop_size: int = 100,
    generations: int = 300,
    mutation_rate: float = 0.15,
    k_neighbors: int = 4,
) -> list[int]:

    n = len(distances)
    pop = [random.sample(range(n), n) for _ in range(pop_size)]
    neighbors = build_nearest_neighbors(distances, k=k_neighbors)

    for gen in range(generations):
        is_last_generation = gen == generations - 1
        new_pop = []
        for _ in range(pop_size):
            p1 = selection(pop, distances)
            p2 = selection(pop, distances)
            child = order_crossover(p1, p2)
            if not is_last_generation and random.random() < mutation_rate:
                child = mutate(child, neighbors)
            new_pop.append(child)
        pop = new_pop

    return min(pop, key=lambda t: fitness(t, distances))


def display_route(tour: list[int], cities: dict[str, tuple[float, float]], distance: float) -> None:

    names = list(cities.keys())
    coords = list(cities.values())

    route_coords = [coords[i] for i in tour] + [coords[tour[0]]]
    lats = [lat for lat, lon in route_coords]
    lons = [lon for lat, lon in route_coords]

    plt.figure(figsize=(10, 10))
    plt.plot(lons, lats, marker="o", linestyle="-", color="tab:blue", markerfacecolor="tab:red")

    for idx in tour:
        lat, lon = coords[idx]
        plt.annotate(names[idx], (lon, lat), fontsize=7, xytext=(3, 3), textcoords="offset points")

    plt.xlabel("Longitude")
    plt.ylabel("Latitude")
    plt.title(f"Meilleur parcours trouvé (distance totale : {distance:.2f} km)")
    plt.gca().set_aspect("equal")
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.tight_layout()
    plt.show()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Algorithme génétique pour le TSP entre villes.")
    parser.add_argument("--generations", type=int, default=300, help="Nombre de générations (défaut: 300)")
    parser.add_argument("--mutation-rate", type=float, default=0.05, help="Taux de mutation, entre 0 et 1 (défaut: 0.05)")
    parser.add_argument("--k-neighbors", type=int, default=5, help="Nombre de voisines proches considérées pour la mutation (défaut: 5)")
    parser.add_argument("--pop-size", type=int, default=100, help="Taille de la population (défaut: 100)")
    parser.add_argument("--n-cities", type=int, default=20, help="Nombre de villes à utiliser, prises dans le CSV (défaut: 20)")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()

    cities = cities_listing()
    print(f"{len(cities)} cities loaded.")

    # NB : avec beaucoup de villes, réduire ce sous-ensemble pour rester rapide
    # (le TSP est très coûteux en calcul au-delà de quelques dizaines de villes).
    subset = dict(list(cities.items())[: args.n_cities])

    distances = build_distance_matrix(subset)
    best_tour = genetic_algorithm(
        distances,
        pop_size=args.pop_size,
        generations=args.generations,
        mutation_rate=args.mutation_rate,
        k_neighbors=args.k_neighbors,
    )
    best_distance = fitness(best_tour, distances)

    noms_parcours = [list(subset.keys())[i] for i in best_tour]
    print(f"Meilleur ordre de visite : {noms_parcours}")
    print(f"Distance totale du parcours : {best_distance:.2f} km")

    display_route(best_tour, subset, best_distance)
