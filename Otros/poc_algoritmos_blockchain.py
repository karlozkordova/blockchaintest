
# -*- coding: utf-8 -*-
"""
POC: Algoritmos Criptográficos en Blockchain
Requiere: Python 3.x
Dependencias estándar: hashlib, hmac, os, base64, cryptography
"""

import hashlib
import hmac
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec, rsa, utils
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric.utils import (
    encode_dss_signature, decode_dss_signature
)
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import asymmetric
from cryptography.hazmat.primitives.asymmetric import padding


import os

# =============================================
# 1. SHA-256
# =============================================
def demo_sha256(message):
    """Calcula el hash SHA-256 de una cadena de texto."""
    print("SHA-256:")
    h = hashlib.sha256(message.encode()).hexdigest()
    print(f"Mensaje: {message}")
    print(f"Hash: {h}\n")

# =============================================
# 2. SHA-3-256
# =============================================
def demo_sha3_256(message):
    """Calcula el hash SHA3-256 de una cadena de texto."""
    print("SHA3-256:")
    h = hashlib.sha3_256(message.encode()).hexdigest()
    print(f"Mensaje: {message}")
    print(f"Hash: {h}\n")

# =============================================
# 3. ECDSA (secp256r1)
# =============================================
def demo_ecdsa(message):
    """Firma y verificación usando ECDSA."""
    print("ECDSA (secp256r1):")
    private_key = ec.generate_private_key(ec.SECP256R1(), default_backend())
    public_key = private_key.public_key()

    signature = private_key.sign(message.encode(), ec.ECDSA(hashes.SHA256()))
    print(f"Mensaje: {message}")
    print(f"Firma (hex): {signature.hex()}")

    try:
        public_key.verify(signature, message.encode(), ec.ECDSA(hashes.SHA256()))
        print("Verificación: OK\n")
    except InvalidSignature:
        print("Verificación: Fallida\n")

# =============================================
# 4. RSA
# =============================================
def demo_rsa(message):
    """Firma y verificación usando RSA."""
    print("RSA (2048 bits):")
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )
    public_key = private_key.public_key()

    signature = private_key.sign(
        message.encode(),
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )
    print(f"Mensaje: {message}")
    print(f"Firma (hex): {signature.hex()[:64]}...")

    try:
        public_key.verify(
            signature,
            message.encode(),
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        print("Verificación: OK\n")
    except InvalidSignature:
        print("Verificación: Fallida\n")


# =============================================
# 5. VRF simulada (HMAC-SHA256)
# =============================================
def demo_vrf_sim(message, secret_key=b'secret'):
    """Simula una VRF usando HMAC-SHA256."""
    print("VRF simulada con HMAC-SHA256:")
    vrf_output = hmac.new(secret_key, message.encode(), hashlib.sha256).hexdigest()
    print(f"Mensaje: {message}")
    print(f"Clave secreta: {secret_key.decode(errors='ignore')}")
    print(f"Salida VRF (hex): {vrf_output}\n")

# =============================================
# MAIN
# =============================================
if __name__ == "__main__":
    mensaje = "Hola Blockchain" #Cadena de texto a cifrar
    demo_sha256(mensaje)
    demo_sha3_256(mensaje)
    demo_ecdsa(mensaje)
    demo_rsa(mensaje)
    demo_vrf_sim(mensaje)
