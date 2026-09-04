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

def genetic_algorithm(distances, pop_size=100, generations=300):
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

import math
import matplotlib.pyplot as plt

#1 generation des données
villes = [(random.randint(0, 100), random.randint(0, 100)) for _ in range(15)]

#2 calcule de la matrice des distances
distances = []
for i in range(len(villes)):
    row = []
    for j in range(len(villes)):
        dist = math.hypot(villes[i][0] - villes[j][0], villes[i][1] - villes[j][1])
        row.append(dist)
    distances.append(row)

#3 execution de l'algorithme
meilleur_parcours = genetic_algorithm(villes, distances, pop_size=100, generations=300)
meilleur_distance = fitness(meilleur_parcours, distances)

#4 affichage du texte
print(f"Meilleur parcours : {meilleur_parcours}")
print(f"Meilleure distance : {meilleur_distance:.2f}")

# 5 affichage graphique
def afficher_parcours(tour, villes, distances):
    tour_coords = [villes[i] for i in tour]
    tour_coords.append(tour_coords[0])  # Retour au point de départ
    x, y = zip(*tour_coords)

    plt.figure(figsize=(8, 6))
    plt.plot(x, y, marker='o', linestyle='-', color='blue')