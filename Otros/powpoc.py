import hashlib  # Librería para calcular el hash SHA-256
import time     # Para medir el tiempo de procesamiento

# Función que calcula el hash SHA-256 de una entrada de texto
# Esta función representa el uso de la función hash en PoW, por ejemplo SHA-256 en Bitcoin
def calcular_hash(texto):
    return hashlib.sha256(texto.encode('utf-8')).hexdigest()

# Función principal que simula la prueba de trabajo (Proof of Work)
# dato_bloque: información del bloque (transacciones, timestamp, hash anterior, etc.)
# dificultad: número de ceros que el hash resultante debe tener al inicio

def prueba_de_trabajo(dato_bloque, dificultad):
    # Este prefijo define el objetivo: un hash con "dificultad" cantidad de ceros al inicio
    prefix = '0' * dificultad

    # Este valor será incrementado hasta que el hash cumpla con la dificultad
    nonce = 0

    # Guardamos el tiempo de inicio para medir cuánto tarda en encontrar un hash válido
    inicio = time.time()

    # Bucle de minería: simula a los mineros intentando encontrar un nonce válido
    while True:
        # Concatenamos los datos del bloque con el nonce actual
        texto = f"{dato_bloque}|{nonce}"

        # Calculamos el hash del bloque
        hash_resultado = calcular_hash(texto)

        # Validamos si el hash cumple con el objetivo (es menor al umbral definido por los ceros)
        if hash_resultado.startswith(prefix):
            # ⏱ Medimos el tiempo total de minado
            fin = time.time()

            # Retornamos los datos clave del proceso PoW
            return {
                "nonce": nonce,              # Nonce que resolvió el puzzle
                "hash": hash_resultado,      # Hash válido encontrado
                "tiempo": round(fin - inicio, 4),  # Tiempo de cómputo
                "intentos": nonce + 1        # Número de pruebas realizadas
            }

        # ➕ Si no cumple, incrementamos el nonce y seguimos intentando
        nonce += 1

# --- SIMULACIÓN ---

#  Datos del bloque a minar (puedes simular una transacción o mensaje arbitrario)
bloque = "Carlos envía 1 BTC a Ana"

# 🎚 Nivel de dificultad: número de ceros que el hash debe tener al inicio
# A mayor dificultad, más difícil encontrar un hash válido (más intentos y más tiempo)
dificultad = 5  # Prueba con 5 o 6 para ver cómo cambia el rendimiento

# Ejecutamos el proceso de minería
resultado = prueba_de_trabajo(bloque, dificultad)

# Mostramos los resultados
print("Bloque a minar: ", bloque)                      # Simulación de Bloque a minar con un string
print("Dificultad: ", dificultad)                       # Nivel de dificultad para el minado 
print("Nonce encontrado:", resultado["nonce"])         # Número que resolvió el puzzle
print("Hash válido:", resultado["hash"])               # Hash resultante del bloque + nonce
print("Tiempo:", resultado["tiempo"], "segundos")      # Tiempo requerido para minar
print("Intentos:", resultado["intentos"])              # Número total de pruebas (hashes)
