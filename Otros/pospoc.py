import random
import time

# Lista de nodos con su cantidad de tokens en stake
nodos = {
    "Nodo_A": 5,
    "Nodo_B": 20,
    "Nodo_C": 10,
    "Nodo_D": 15
}

# Función que simula la selección del validador según stake proporcional
def seleccionar_validador(nodos_stake):
    # Creamos una lista con los nombres de nodos repetidos proporcionalmente al stake
    pool = []
    for nodo, stake in nodos_stake.items():
        pool.extend([nodo] * stake)  # Más stake → más entradas al sorteo

    # Elegimos aleatoriamente un nodo entre los ponderados
    validador = random.choice(pool)
    return validador

# Ejecutamos varias rondas de simulación para ver probabilidades
resultados = {}
rondas = 1000

inicio = time.time()

for _ in range(rondas):
    ganador = seleccionar_validador(nodos)
    resultados[ganador] = resultados.get(ganador, 0) + 1

fin = time.time()

# Mostramos resultados
print("Resultados de selección PoS después de", rondas, "rondas:\n")
for nodo, veces in resultados.items():
    porcentaje = (veces / rondas) * 100
    print(f"{nodo}: {veces} veces seleccionado ({porcentaje:.2f}%)")

print(f"\n Tiempo total de simulación: {round(fin - inicio, 4)} segundos")
