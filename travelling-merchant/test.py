import random

from altair import sample

def fitness(tour,distances):
  return sum(distances[tour[i]][tour[i+1]] for i in range(len(tour)-1))

def selection(pop, distances , k=3):
  #Tournoi : on tire K individus, on garde le meilleur
  return min(random.sample(pop, k), key=lambda t: fitness(t, distances))

def order_crossover(p1, p2):
  size = len(p1)
  start, end = sorted(random,sample(range(size), 2))
  child = [-1] * size
  #copie de la sous chaine de p1
  child[start:end] = p1[start:end]
  #remplissage avec les élements du p2
  p2_filtered = [x for x in p2 if x not in child]
  child[:start] = p2_filtered[:start]
  child[end:] = p2_filtered[start:]
  return child 

def mutate(child):
  idx1, idx2 = random.sample(range(len(child)), 2)
  child[idx1], child[idx2] = child[idx2], child[idx1]
  return child

def genetic_algorithm(villes , distances, pop_size=100, generations=500):
  pop = [random.sample(range(len(villes)), len(villes)) for _ in range(pop_size)]
  for gen in range(generations):
    new_pop = []
    for _ in range(pop_size):
      p1,p2 = selection(pop, distances), selection(pop, distances)
      child = order_crossover(p1, p2)
      if random.random() < 0.05: child = mutate(child)  #mutation 5%
      new_pop.append(child)
    pop = new_pop
    
  return min(pop, key=lambda t: fitness(t, distances))   

import math
import matplotlib.pyplot as plt

villes = [(random.randint(0,100)),(random.randint(0,100))] for _ in range(15)]

distances = []
for i in  
      
