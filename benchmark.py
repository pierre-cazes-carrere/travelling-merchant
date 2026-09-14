
import statistics
import time

from cities_data import build_distance_matrix, cities_listing
from genetic_algorithmm import display_route, fitness, genetic_algorithm


N_CITIES = 20         
POP_SIZE = 80           
N_TRIALS = 25            

GENERATIONS_OPTIONS = [100, 200, 300,]
MUTATION_RATE_OPTIONS = [0.05, 0.15, 0.1]
K_NEIGHBORS_OPTIONS = [3,4,5,6]


def run_benchmark() -> tuple[list[dict], list[int], float, dict]:
    cities = cities_listing()
    subset = dict(list(cities.items())[:N_CITIES])
    distances = build_distance_matrix(subset)

    results = []
    overall_best_tour = None
    overall_best_distance = float("inf")

    total_combos = len(GENERATIONS_OPTIONS) * len(MUTATION_RATE_OPTIONS) * len(K_NEIGHBORS_OPTIONS)
    combo_num = 0

    for generations in GENERATIONS_OPTIONS:
        for mutation_rate in MUTATION_RATE_OPTIONS:
            for k_neighbors in K_NEIGHBORS_OPTIONS:
                combo_num += 1
                print(
                    f"[{combo_num}/{total_combos}] "
                    f"generations={generations}, mutation_rate={mutation_rate}, k_neighbors={k_neighbors}"
                )

                trial_distances = []
                start = time.perf_counter()

                for _ in range(N_TRIALS):
                    tour = genetic_algorithm(
                        distances,
                        pop_size=POP_SIZE,
                        generations=generations,
                        mutation_rate=mutation_rate,
                        k_neighbors=k_neighbors,
                    )
                    d = fitness(tour, distances)
                    trial_distances.append(d)

                    # on garde en mémoire le meilleur parcours trouvé, toutes
                    # combinaisons et essais confondus
                    if d < overall_best_distance:
                        overall_best_distance = d
                        overall_best_tour = tour

                elapsed = time.perf_counter() - start

                results.append(
                    {
                        "generations": generations,
                        "mutation_rate": mutation_rate,
                        "k_neighbors": k_neighbors,
                        "avg_distance": statistics.mean(trial_distances),
                        "std_distance": statistics.stdev(trial_distances) if N_TRIALS > 1 else 0.0,
                        "best_distance": min(trial_distances),
                        "avg_time_sec": elapsed / N_TRIALS,
                    }
                )

    return results, overall_best_tour, overall_best_distance, subset


def print_results_table(results: list[dict]) -> None:
    # trie du meilleur (distance moyenne la plus faible) au pire
    results_sorted = sorted(results, key=lambda r: r["avg_distance"])

    header = (
        f"{'Rang':<5}{'Gen.':<7}{'Mut. rate':<11}{'K voisins':<11}"
        f"{'Dist. moy.':<13}{'Ecart-type':<12}{'Meilleure':<12}{'Temps moy. (s)':<15}"
    )
    print("\n" + header)
    print("-" * len(header))

    for rank, r in enumerate(results_sorted, start=1):
        print(
            f"{rank:<5}{r['generations']:<7}{r['mutation_rate']:<11}{r['k_neighbors']:<11}"
            f"{r['avg_distance']:<13.2f}{r['std_distance']:<12.2f}"
            f"{r['best_distance']:<12.2f}{r['avg_time_sec']:<15.2f}"
        )


if __name__ == "__main__":
    results, best_tour, best_distance, subset = run_benchmark()
    print_results_table(results)

    print(f"\nMeilleure distance trouvée toutes combinaisons confondues : {best_distance:.2f} km")
    display_route(best_tour, subset, best_distance)