import pandas as pd
import math
import itertools
import networkx as nx
import matplotlib.pyplot as plt
from math import sin, cos, asin, sqrt

df = pd.read_csv('villes_france_lat_long.csv')

# Consigne 1 : Modélisation du problème

#On défini la fonction haversine pour calculé une distance avec les coordonnées GPS de deux points (latitude et longitude).
def haversine(lat1, lon1, lat2, lon2):
    lat1 = math.radians(lat1)
    lon1 = math.radians(lon1)
    lat2 = math.radians(lat2)
    lon2 = math.radians(lon2)

#On calcule l'écart ( Delta) de latitude et de longitude entre les deux points.
    dlat = lat2 - lat1
    dlon = lon2 - lon1

 # Formule de Haversine pour calculer la distance entre deux points sur une sphère
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2

#asin(sqrt(a)) nous donne l'angle (en radians) entre les deux points en partant du centre de la Terre.
    return 6371 * 2 * asin(sqrt(a))




# Graphique des villes et distances

G = nx.Graph()

#Ici on crée des points (noeuds) en parcourant le csv pour ensuite pouvoir faire les arretes.
for _, row in df.iterrows():
    G.add_node(row['Ville'], pos=(row['Longitude'], row['Latitude']))

# On prend le dataframe et on génére tout les chemins possibles sans doubles et ça nous donnes des tuples genre ( london - paris ) et ( paris - london )
#  donc on utilise itertools.combinations pour ne pas avoir de doublons.
for (i, row_i), (j, row_j) in itertools.combinations(df.iterrows(), 2):
    d = haversine(row_i['Latitude'], row_i['Longitude'], row_j['Latitude'], row_j['Longitude'])
    G.add_edge(row_i['Ville'], row_j['Ville'], weight=d)

print(G.edges(data=True))








































# Consigne 2 : Résolution avec l'algorithme de Christofides

def resoudre_christofides(G):
    circuit = nx.approximation.christofides(G, weight='weight') # Pour calculer les distances/coûts, va chercher la clé 'weight' dans les attributs de chaque arête.

    # Distance totale = somme des poids des arêtes 
    distance_totale = sum(
        G[circuit[k]][circuit[k + 1]]['weight']
        for k in range(len(circuit) - 1)
    )

    return circuit, distance_totale

# Graphiques carte parcours

def afficher_circuit(G, circuit, titre, nom_fichier):

    pos = nx.get_node_attributes(G, 'pos')

    plt.figure(figsize=(10, 10))
    nx.draw(G, pos, with_labels=True, node_color='lightblue',
            node_size=300, font_size=8, edge_color='none')

    chemin_edges = list(zip(circuit[:-1], circuit[1:]))
    nx.draw_networkx_edges(G, pos, edgelist=chemin_edges,
                            edge_color='red', width=2)

    plt.title(titre)
    plt.savefig(nom_fichier, dpi=120, bbox_inches='tight')
    plt.close()





























import math
import random

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

cities_df = df.rename(columns={
    "Ville": "city",
    "Latitude": "latitude",
    "Longitude": "longitude"
})

print("=== Données chargées ===")
print(f"Nombre de villes : {len(cities_df)}")
print(cities_df)


villes = list(
    zip(
        cities_df["latitude"],
        cities_df["longitude"]
    )
)

print("\nCorrespondance index -> ville :")

for index, city_name in enumerate(cities_df["city"]):
    print(f"{index} = {city_name}")

EARTH_RADIUS_KM = 6371.0


def haversine(city_a, city_b):
    """
    Calcule la distance géographique à vol d'oiseau
    entre deux villes sous la forme :
    city_a = (latitude, longitude)
    city_b = (latitude, longitude)

    Retourne une distance en kilomètres.
    """
    lat1, lon1 = city_a
    lat2, lon2 = city_b

    lat1 = math.radians(lat1)
    lon1 = math.radians(lon1)
    lat2 = math.radians(lat2)
    lon2 = math.radians(lon2)

    delta_lat = lat2 - lat1
    delta_lon = lon2 - lon1

    a = (
        math.sin(delta_lat / 2) ** 2
        + math.cos(lat1)
        * math.cos(lat2)
        * math.sin(delta_lon / 2) ** 2
    )

    c = 2 * math.atan2(
        math.sqrt(a),
        math.sqrt(1 - a)
    )

    return EARTH_RADIUS_KM * c


distances = []

for i in range(len(villes)):
    row = []

    for j in range(len(villes)):
        distance = haversine(
            villes[i],
            villes[j]
        )

        row.append(distance)

    distances.append(row)

distances = np.array(distances)

distance_matrix_df = pd.DataFrame(
    distances,
    index=cities_df["city"],
    columns=cities_df["city"]
)

print("\n=== Vérifications de la matrice ===")
print("Dimensions :", distances.shape)
print("Matrice symétrique :", np.allclose(distances, distances.T))
print("Diagonale nulle :", np.allclose(np.diag(distances), 0))

paris_index = cities_df.index[
    cities_df["city"] == "Paris"
][0]

marseille_index = cities_df.index[
    cities_df["city"] == "Marseille"
][0]

print(
    f"Distance Paris -> Marseille : "
    f"{distances[paris_index][marseille_index]:.2f} km"
)

def fitness(tour, distances):
    """
    Calcule la distance totale d'une tournée TSP.

    Important :
    - additionne chaque trajet entre deux villes successives ;
    - ajoute le retour de la dernière ville à la première.
    """
    distance_totale = sum(
        distances[tour[i]][tour[i + 1]]
        for i in range(len(tour) - 1)
    )

    distance_retour = distances[
        tour[-1]
    ][
        tour[0]
    ]

    return distance_totale + distance_retour

def selection(pop, distances, k=3):
    """
    Tire k tournées aléatoires dans la population,
    puis retourne la plus courte.
    """
    candidats = random.sample(pop, k)

    return min(
        candidats,
        key=lambda tour: fitness(tour, distances)
    ).copy()


def order_crossover(p1, p2):
    """
    Ordered Crossover (OX).

    Copie une sous-chaîne du parent 1, puis complète
    avec les villes manquantes du parent 2.
    Cela garantit un enfant sans doublon.
    """
    size = len(p1)

    start, end = sorted(
        random.sample(range(size), 2)
    )

    child = [-1] * size

    child[start:end] = p1[start:end]

    p2_filtered = [
        city
        for city in p2
        if city not in child
    ]

    child[:start] = p2_filtered[:start]
    child[end:] = p2_filtered[start:]

    return child


def mutate(child):

    mutated_child = child.copy()

    index_1, index_2 = random.sample(
        range(len(mutated_child)),
        2
    )

    mutated_child[index_1], mutated_child[index_2] = (
        mutated_child[index_2],
        mutated_child[index_1]
    )

    return mutated_child


def genetic_algorithm(
    villes,
    distances,
    pop_size=100,
    generations=500,
    mutation_rate=0.05
):

    population = [
        random.sample(
            range(len(villes)),
            len(villes)
        )
        for _ in range(pop_size)
    ]

    best_history = []

    for generation in range(generations):
        # Trier du meilleur au moins bon itinéraire.
        population = sorted(
            population,
            key=lambda tour: fitness(
                tour,
                distances
            )
        )

        # Élitisme : copie du meilleur individu.
        elite = population[0].copy()

        new_population = [elite]

        # Création des autres individus.
        while len(new_population) < pop_size:
            parent_1 = selection(
                population,
                distances
            )

            parent_2 = selection(
                population,
                distances
            )

            child = order_crossover(
                parent_1,
                parent_2
            )

            if random.random() < mutation_rate:
                child = mutate(child)

            new_population.append(child)

        population = new_population

        best_history.append(
            fitness(elite, distances)
        )

    best_tour = min(
        population,
        key=lambda tour: fitness(
            tour,
            distances
        )
    )

    return best_tour, best_history


random.seed(42)

meilleur_parcours, historique = genetic_algorithm(
    villes=villes,
    distances=distances,
    pop_size=100,
    generations=300,
    mutation_rate=0.05
)

meilleure_distance = fitness(
    meilleur_parcours,
    distances
)

assert len(meilleur_parcours) == len(villes)
assert len(set(meilleur_parcours)) == len(villes)
assert set(meilleur_parcours) == set(range(len(villes)))

parcours_noms = [
    cities_df.iloc[index]["city"]
    for index in meilleur_parcours
]

# Retour à la ville de départ pour afficher le circuit.
parcours_noms_ferme = parcours_noms + [
    parcours_noms[0]
]

print("\n=== RÉSULTAT DE L'ALGORITHME GÉNÉTIQUE ===")
print("Meilleur ordre de visite :")
print(" → ".join(parcours_noms_ferme))

print(
    f"\nDistance totale : "
    f"{meilleure_distance:.2f} km"
)
def afficher_parcours(
    tour,
    villes,
    cities_df,
    distance
):
    """
    Affiche la tournée sur un plan longitude / latitude.
    villes est une liste de tuples (latitude, longitude).
    """
    # On ajoute le retour à la ville de départ.
    tour_ferme = tour + [tour[0]]

    latitudes = [
        villes[index][0]
        for index in tour_ferme
    ]

    longitudes = [
        villes[index][1]
        for index in tour_ferme
    ]

    plt.figure(figsize=(13, 10))

    plt.plot(
        longitudes,
        latitudes,
        marker="o",
        linestyle="-",
        color="royalblue",
        markerfacecolor="crimson",
        linewidth=1.8,
        markersize=5,
        zorder=2
    )

    # Écriture du nom de chaque ville.
    for index, (latitude, longitude) in enumerate(villes):
        city_name = cities_df.iloc[index]["city"]

        plt.annotate(
            f"{index}. {city_name}",
            (longitude, latitude),
            xytext=(5, 5),
            textcoords="offset points",
            fontsize=8
        )

    # Mettre en évidence la ville de départ / arrivée.
    start_city_index = tour[0]
    start_latitude, start_longitude = villes[
        start_city_index
    ]

    plt.scatter(
        start_longitude,
        start_latitude,
        s=180,
        color="gold",
        edgecolor="black",
        zorder=3,
        label=(
            "Départ / arrivée : "
            f"{cities_df.iloc[start_city_index]['city']}"
        )
    )

    plt.title(
        "TSP — Algorithme génétique avec distance Haversine\n"
        f"Distance totale : {distance:.2f} km"
    )

    plt.xlabel("Longitude")
    plt.ylabel("Latitude")
    plt.grid(
        True,
        linestyle="--",
        alpha=0.5
    )
    plt.legend()
    plt.tight_layout()
    plt.show()


afficher_parcours(
    tour=meilleur_parcours,
    villes=villes,
    cities_df=cities_df,
    distance=meilleure_distance
)


plt.figure(figsize=(10, 5))

plt.plot(
    historique,
    color="crimson",
    linewidth=2
)

plt.title("Convergence de l'algorithme génétique")
plt.xlabel("Génération")
plt.ylabel("Meilleure distance totale (km)")
plt.grid(alpha=0.3)
plt.tight_layout()
plt.show()