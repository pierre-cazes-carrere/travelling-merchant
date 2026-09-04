import pandas as pd
import math
import itertools
import networkx as nx
import matplotlib.pyplot as plt
from math import sin, cos, asin, sqrt

df = pd.read_csv('villes_france_lat_long.csv')

# Consigne 1 : Modélisation du problème

def haversine(lat1, lon1, lat2, lon2):
    lat1 = math.radians(lat1)
    lon1 = math.radians(lon1)
    lat2 = math.radians(lat2)
    lon2 = math.radians(lon2)
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    return 6371 * 2 * asin(sqrt(a))

# Graphique des villes et distances

G = nx.Graph()

for _, row in df.iterrows():
    G.add_node(row['Ville'], pos=(row['Longitude'], row['Latitude']))

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





























# Consigne 3 : Résolution avec un algorithme génétique ( HOW TO )

import random

def fitness(tour, distances):
    return sum(distances[tour[i]][tour[i+1]] for i in range(len(tour)-1))

def selection(pop, distances, k=3):
    # Tournoi : on tire k individus, on garde le meilleur
    return min(random.sample(pop, k), key=lambda t: fitness(t, distances))

def order_crossover(p1, p2):
    size = len(p1)
    start, end = sorted(random.sample(range(size), 2))
    child = [-1] * size
    child[start:end] = p1[start:end]
    p2_filtered = [x for x in p2 if x not in child]
    child[:start] = p2_filtered[:start]
    child[end:] = p2_filtered[start:]
    return child

def mutate(child):
    idx1, idx2 = random.sample(range(len(child)), 2)
    child[idx1], child[idx2] = child[idx2], child[idx1]
    return child

def genetic_algorithm(villes, distances, pop_size=100, generations=300):
    pop = [random.sample(range(len(villes)), len(villes)) for _ in range(pop_size)]
    for gen in range(generations):
        new_pop = []
        for _ in range(pop_size):
            p1 = selection(pop, distances)
            p2 = selection(pop, distances)
            child = order_crossover(p1, p2)
            if random.random() < 0.05:  # Mutation probability
                child = mutate(child)
            new_pop.append(child)
        pop = new_pop

    return min(pop, key=lambda t: fitness(t, distances))


#1 génération des données -> on reprend les villes de la consigne 1
villes = list(zip(df['Longitude'], df['Latitude']))

#2 calcul de la matrice des distances -> Haversine de la consigne 1
distances = []
for i in range(len(df)):
    row = []
    for j in range(len(df)):
        d = haversine(df.iloc[i]['Latitude'], df.iloc[i]['Longitude'],
                      df.iloc[j]['Latitude'], df.iloc[j]['Longitude'])
        row.append(d)
    distances.append(row)

#3 execution de l'algorithme
meilleur_parcours = genetic_algorithm(villes, distances, pop_size=100, generations=300)
meilleur_distance = fitness(meilleur_parcours, distances)

#4 affichage du texte
print(f"Meilleur parcours : {[df.iloc[i]['Ville'] for i in meilleur_parcours]}")
print(f"Meilleure distance : {meilleur_distance:.2f}")

# 5 affichage graphique
def afficher_parcours(tour, villes, distances):
    tour_coords = [villes[i] for i in tour]
    tour_coords.append(tour_coords[0])  # Retour au point de départ
    x, y = zip(*tour_coords)

    plt.figure(figsize=(8, 6))
    plt.plot(x, y, marker='o', linestyle='-', color='blue')
    plt.title(f"Itinéraire de Théobald (Génétique) - {meilleur_distance:.0f} km")
    plt.savefig('itineraire_genetique.png', dpi=120, bbox_inches='tight')
    plt.close()


if __name__ == "__main__":
    print(f"Nombre de villes (noeuds) : {G.number_of_nodes()}")
    print(f"Nombre de routes (arêtes) : {G.number_of_edges()}")
    print(f"Exemple : Marseille a Lyon : {G['Marseille']['Lyon']['weight']:.1f} km")

    # Graphique du graphe complet (consigne 1)
    pos = nx.get_node_attributes(G, 'pos')
    plt.figure(figsize=(10, 10))
    nx.draw(G, pos, with_labels=True, node_color='lightblue',
            node_size=300, font_size=8, edge_color='gray', alpha=0.5)
    plt.title("Graphe des villes de France")
    plt.savefig('graphe_villes.png', dpi=120, bbox_inches='tight')
    plt.close()

    #  Consigne 2 : Christofides 
    circuit_christofides, distance_christofides = resoudre_christofides(G)

    print("\n--- Consigne 2 : Christofides ---")
    print("Itinéraire :", " -> ".join(circuit_christofides))
    print(f"Distance totale : {distance_christofides:.1f} km")

    afficher_circuit(
        G, circuit_christofides,
        titre=f"Itinéraire de Théobald (Christofides) - {distance_christofides:.0f} km",
        nom_fichier="itineraire_christofides.png"
    )

    #  Consigne 3 : Algorithme génétique 
    afficher_parcours(meilleur_parcours, villes, distances)
