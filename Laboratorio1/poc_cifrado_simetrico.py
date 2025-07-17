
# -*- coding: utf-8 -*-
"""
PoC: Cifrado Simétrico y Asimétrico en Python (Con Visualización de Claves)
Requiere: Python 3.x
Dependencias: cryptography
"""

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.backends import default_backend
# Importación necesaria para mostrar claves en formato PEM
from cryptography.hazmat.primitives import serialization
import os
import base64

# =============================================
# 1. Cifrado Simétrico con AES
# =============================================
def cifrado_simetrico(mensaje):
    print("🔐 Cifrado Simétrico con AES-256")
    password = b"clave_secreta"
    print(f"🔑 Clave compartida (derivada de contraseña): {password.decode()}")

    salt = os.urandom(16)
    print(f"🧂 Salt aleatorio (hex): {salt.hex()}")

    # Derivar clave de 256 bits (32 bytes)
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    key = kdf.derive(password)
    print(f"🔐 Clave de cifrado derivada (hex): {key.hex()}")

    iv = os.urandom(16)
    print(f"📦 IV (vector de inicialización): {iv.hex()}")

    cipher = Cipher(algorithms.AES(key), modes.CFB(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(mensaje.encode()) + encryptor.finalize()

    print(f"📨 Mensaje original: {mensaje}")
    print(f"🔒 Texto cifrado (hex): {ciphertext.hex()}")

    # Descifrado
    decryptor = cipher.decryptor()
    decrypted = decryptor.update(ciphertext) + decryptor.finalize()
    print(f"🔓 Texto descifrado con la misma clave: {decrypted.decode()}\n")

# =============================================
# MAIN
# =============================================
if __name__ == "__main__":
    mensaje = "Hola Blockchain"
    cifrado_simetrico(mensaje)
