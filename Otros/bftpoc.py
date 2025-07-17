import random
from collections import Counter

# Simulación de nodos
total_nodos = 10
maliciosos = 4  # Hasta 1/3 pueden ser maliciosos según BFT
honestos = total_nodos - maliciosos

# El valor propuesto por el líder (puede ser un bloque, transacción, etc.)
propuesta_lider = "Bloque_A"

# Generar votos
def simular_votos(propuesta, total, maliciosos):
    votos = []

    # Nodos honestos: todos votan consistentemente por la propuesta del líder
    for _ in range(total - maliciosos):
        votos.append(propuesta)

    # Nodos maliciosos: pueden votar aleatoriamente o dividir votos
    opciones = ["Bloque_X", "Bloque_Y", "Bloque_Z"]
    for _ in range(maliciosos):
        votos.append(random.choice(opciones))

    random.shuffle(votos)  # Mezclamos los votos como si fueran anónimos
    return votos

# Proceso de consenso
def consenso_bft(votos, total):
    conteo = Counter(votos)
    print("🗳 Conteo de votos:")
    for valor, cantidad in conteo.items():
        print(f" - {valor}: {cantidad} votos")

    # Condición PBFT: se necesita al menos 2/3 de los votos para llegar a consenso
    umbral = (2 * total) // 3 + 1

    for valor, cantidad in conteo.items():
        if cantidad >= umbral:
            print(f"\n✅ ¡Consenso alcanzado sobre: {valor}!\n")
            return valor

    print("\n❌ No se alcanzó consenso (valor rechazado).\n")
    return None

# Simulación
votos = simular_votos(propuesta_lider, total_nodos, maliciosos)
consenso_bft(votos, total_nodos)
