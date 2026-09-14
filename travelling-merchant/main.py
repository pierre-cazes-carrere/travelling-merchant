import pandas as pd

# Chargement des données
villes = pd.read_csv("data/villes_france_lat_long.csv")

print(villes)
print()
print("Nombre de villes :", len(villes))



from src.distance import haversine

distance = haversine(
    villes.iloc[0]["Latitude"],
    villes.iloc[0]["Longitude"],
    villes.iloc[1]["Latitude"],
    villes.iloc[1]["Longitude"]
)

print("Distance :", distance, "km")



import numpy as np

n = len(villes)

matrice_distances = np.zeros((n, n))

for i in range(n):
    for j in range(n):

        if i != j:

            distance = haversine(
                villes.iloc[i]["Latitude"],
                villes.iloc[i]["Longitude"],
                villes.iloc[j]["Latitude"],
                villes.iloc[j]["Longitude"]
            )

            matrice_distances[i][j] = distance
            
print(matrice_distances)            