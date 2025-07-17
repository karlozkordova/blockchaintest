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
# 1. Cifrado Asimétrico con RSA
# =============================================
def cifrado_asimetrico(mensaje):
    print("🔐 Cifrado Asimétrico con RSA-2048")

    # Generar par de claves
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )
    public_key = private_key.public_key()

    # Mostrar claves en base64 para facilitar la lectura
    priv_pem = private_key.private_bytes(
        encoding = serialization.Encoding.PEM,
        format = serialization.PrivateFormat.PKCS8,
        encryption_algorithm = serialization.NoEncryption()
    )
    pub_pem = public_key.public_bytes(
        encoding = serialization.Encoding.PEM,
        format = serialization.PublicFormat.SubjectPublicKeyInfo
    )

    print("🔑 Clave pública (PEM):")
    print(pub_pem.decode())
    print("🔐 Clave privada (PEM):")
    print(priv_pem.decode())

    # Cifrar con clave pública
    ciphertext = public_key.encrypt(
        mensaje.encode(),
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    print(f"📨 Mensaje original: {mensaje}")
    print(f"🔒 Texto cifrado (hex): {ciphertext.hex()[:60]}...")

    # Descifrar con clave privada
    decrypted = private_key.decrypt(
        ciphertext,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    print(f"🔓 Texto descifrado con clave privada: {decrypted.decode()}\n")

# =============================================
# MAIN
# =============================================
if __name__ == "__main__":
    mensaje = "Hola Blockchain"
    cifrado_asimetrico(mensaje)
