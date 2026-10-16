#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Laboratorio didáctico: cifrado SIMÉTRICO de archivos con AES-256-GCM.

Basado en el PoC de AES + PBKDF2. Permite cifrar y descifrar cualquier
archivo binario (PDF, DOCX, ISO, ZIP, imagen, etc.) sin cargarlo en RAM.

No utiliza RSA: la misma contraseña permite derivar la misma clave AES al
usar el salt almacenado en el archivo cifrado.

Formato de archivo .enc:
    MAGIC (8 bytes) | SALT (16 bytes) | NONCE (12 bytes) |
    CIPHERTEXT (mismo tamaño que el archivo original) | TAG (16 bytes)
Sobrecoste fijo: 52 bytes. El encabezado se autentica como AAD.

Ejemplos:
    python3 poc_cifrado_simetrico_archivos.py archivo.iso
    python3 poc_cifrado_simetrico_archivos.py cifrar documento.pdf
    python3 poc_cifrado_simetrico_archivos.py descifrar documento.pdf.enc
    python3 poc_cifrado_simetrico_archivos.py cifrar archivo.zip --mostrar-claves
    python3 poc_cifrado_simetrico_archivos.py descifrar archivo.zip.enc --salida recuperado.zip

Requiere: pip install cryptography
ADVERTENCIA: --mostrar-claves expone contraseñas/clave derivada y solo se
recomienda con archivos y contraseñas de laboratorio.
"""

import argparse
import getpass
import hashlib
import os
import struct
import sys
import tempfile
import time
from pathlib import Path

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

MAGIC = b"AESGCM01"           # 8 bytes: identifica este formato didáctico
SALT_LEN = 16
NONCE_LEN = 12
TAG_LEN = 16
BLOQUE = 4 * 1024 * 1024    # 4 MiB por lectura
ITERACIONES = 600_000         # PBKDF2-HMAC-SHA256
ENCABEZADO_LEN = len(MAGIC) + SALT_LEN + NONCE_LEN


def derivar_clave(password: str, salt: bytes) -> bytes:
    """PBKDF2 convierte contraseña + salt en 32 bytes (AES-256).

    El salt no es secreto; se almacena en el encabezado para permitir
    derivar la MISMA clave durante el descifrado.
    """
    return PBKDF2HMAC(
        algorithm=hashes.SHA256(), length=32,
        salt=salt, iterations=ITERACIONES
    ).derive(password.encode("utf-8"))


def sha256_archivo(ruta: Path) -> str:
    """Huella para comparar original y recuperado; no cifra el contenido."""
    sha = hashlib.sha256()
    with ruta.open("rb") as entrada:
        while bloque := entrada.read(BLOQUE):
            sha.update(bloque)
    return sha.hexdigest()


def salida_libre(ruta: Path, origen: Path) -> Path:
    """Evita sobrescribir el origen u otro archivo existente."""
    ruta = ruta.resolve()
    if ruta == origen.resolve() or ruta.exists():
        raise FileExistsError(f"No se sobrescribirá: {ruta}")
    ruta.parent.mkdir(parents=True, exist_ok=True)
    return ruta


def fichero_temporal(destino: Path) -> Path:
    """Crea un temporal en el mismo directorio para reemplazo atómico."""
    fd, nombre = tempfile.mkstemp(prefix=".aes-tmp-", dir=str(destino.parent))
    os.close(fd)
    return Path(nombre)


def preguntar_password(confirmar=False) -> str:
    clave = getpass.getpass("Contraseña de cifrado: " if confirmar else "Contraseña de descifrado: ")
    if not clave:
        raise ValueError("La contraseña no puede estar vacía")
    if confirmar and clave != getpass.getpass("Repetir contraseña: "):
        raise ValueError("Las contraseñas no coinciden")
    return clave


def mostrar_datos(salt, nonce, clave, mostrar):
    print(f"Salt (público): {salt.hex()}")
    print(f"Nonce (público): {nonce.hex()}")
    print(f"PBKDF2: HMAC-SHA256, {ITERACIONES} iteraciones, 32 bytes")
    print("Cifrado: AES-256-GCM")
    if mostrar:
        print("[LABORATORIO] Clave AES-256 derivada (SECRETA):", clave.hex())


def cifrar(origen: Path, destino: Path, mostrar=False):
    origen = origen.resolve(strict=True)
    if not origen.is_file():
        raise ValueError("La entrada debe ser un archivo")
    destino = salida_libre(destino, origen)
    password = preguntar_password(confirmar=True)
    salt, nonce = os.urandom(SALT_LEN), os.urandom(NONCE_LEN)
    inicio_etapa = time.perf_counter()
    clave = derivar_clave(password, salt)
    tiempo_clave = time.perf_counter() - inicio_etapa
    print(f"[TIEMPO] Derivacion de clave PBKDF2 (cifrado): {tiempo_clave:.4f} s")
    encabezado = MAGIC + salt + nonce
    if mostrar:
        print("[LABORATORIO] Contraseña compartida (SECRETA):", password)
    mostrar_datos(salt, nonce, clave, mostrar)
    cifrador = Cipher(algorithms.AES(clave), modes.GCM(nonce)).encryptor()
    cifrador.authenticate_additional_data(encabezado)
    temporal = fichero_temporal(destino)
    inicio = time.perf_counter()
    try:
        with origen.open("rb") as entrada, temporal.open("wb") as salida:
            salida.write(encabezado)
            while bloque := entrada.read(BLOQUE):
                salida.write(cifrador.update(bloque))
            salida.write(cifrador.finalize())
            salida.write(cifrador.tag)
        os.replace(temporal, destino)
    finally:
        temporal.unlink(missing_ok=True)
    print("Tag GCM (autenticidad/integridad):", cifrador.tag.hex())
    print(f"Archivo cifrado: {destino}")
    print(f"Tamaño original: {origen.stat().st_size} bytes")
    print(f"Tamaño cifrado:  {destino.stat().st_size} bytes (+{ENCABEZADO_LEN+TAG_LEN} bytes)")
    tiempo_datos = time.perf_counter()-inicio
    print(f"[TIEMPO] Cifrado AES-GCM del archivo (lectura/escritura): {tiempo_datos:.4f} s")
    print(f"[TIEMPO] Total cifrado (PBKDF2 + AES, sin ingreso de contrasena): {tiempo_clave + tiempo_datos:.4f} s")
    return destino


def descifrar(origen: Path, destino: Path, mostrar=False):
    origen = origen.resolve(strict=True)
    if not origen.is_file():
        raise ValueError("La entrada debe ser un archivo")
    destino = salida_libre(destino, origen)
    tamano = origen.stat().st_size
    if tamano < ENCABEZADO_LEN + TAG_LEN:
        raise ValueError("Archivo cifrado incompleto")
    with origen.open("rb") as entrada:
        encabezado = entrada.read(ENCABEZADO_LEN)
        if encabezado[:len(MAGIC)] != MAGIC:
            raise ValueError("Formato no reconocido: se esperaba AESGCM01")
        salt = encabezado[len(MAGIC):len(MAGIC)+SALT_LEN]
        nonce = encabezado[len(MAGIC)+SALT_LEN:]
        entrada.seek(-TAG_LEN, os.SEEK_END)
        tag = entrada.read(TAG_LEN)
    password = preguntar_password()
    inicio_etapa = time.perf_counter()
    clave = derivar_clave(password, salt)
    tiempo_clave = time.perf_counter() - inicio_etapa
    print(f"[TIEMPO] Derivacion de clave PBKDF2 (descifrado): {tiempo_clave:.4f} s")
    if mostrar:
        print("[LABORATORIO] Contraseña compartida (SECRETA):", password)
    mostrar_datos(salt, nonce, clave, mostrar)
    print("Tag GCM almacenado:", tag.hex())
    descifrador = Cipher(algorithms.AES(clave), modes.GCM(nonce, tag)).decryptor()
    descifrador.authenticate_additional_data(encabezado)
    pendientes = tamano - ENCABEZADO_LEN - TAG_LEN
    temporal = fichero_temporal(destino)
    inicio = time.perf_counter()
    try:
        with origen.open("rb") as entrada, temporal.open("wb") as salida:
            entrada.seek(ENCABEZADO_LEN)
            while pendientes:
                bloque = entrada.read(min(BLOQUE, pendientes))
                if not bloque:
                    raise ValueError("Archivo truncado")
                pendientes -= len(bloque)
                salida.write(descifrador.update(bloque))
            # IMPORTANTE: no se publica el temporal hasta comprobar el tag.
            salida.write(descifrador.finalize())
        os.replace(temporal, destino)
    except InvalidTag as exc:
        raise ValueError("Falló la autenticación: contraseña incorrecta o archivo alterado") from exc
    finally:
        temporal.unlink(missing_ok=True)
    print(f"Archivo recuperado: {destino}")
    tiempo_datos = time.perf_counter() - inicio
    inicio_hash = time.perf_counter()
    huella = sha256_archivo(destino)
    tiempo_hash = time.perf_counter() - inicio_hash
    print(f"SHA-256 recuperado: {huella}")
    print(f"[TIEMPO] Descifrado AES-GCM del archivo (lectura/escritura): {tiempo_datos:.4f} s")
    print(f"[TIEMPO] Total descifrado (PBKDF2 + AES, sin ingreso de contrasena ni hash): {tiempo_clave + tiempo_datos:.4f} s")
    print(f"[TIEMPO] Calculo SHA-256 recuperado: {tiempo_hash:.4f} s")
    return destino


def main():
    parser = argparse.ArgumentParser(
        description="Laboratorio: AES-256-GCM + PBKDF2 para cualquier archivo")
    parser.add_argument("argumentos", nargs="+", help="Archivo o comando 'cifrar/descifrar' + archivo")
    parser.add_argument("--salida", type=Path, help="Ruta de salida (sin sobrescribir)")
    parser.add_argument("--mostrar-claves", action="store_true", help="Muestra contraseña y clave AES: solo laboratorio")
    args = parser.parse_args()
    if len(args.argumentos) == 1:
        accion, entrada = "demo", Path(args.argumentos[0])
    elif len(args.argumentos) == 2 and args.argumentos[0] in ("cifrar", "descifrar"):
        accion, entrada = args.argumentos[0], Path(args.argumentos[1])
    else:
        parser.error("Uso: script.py archivo | cifrar archivo | descifrar archivo.enc")
    inicio_total = time.perf_counter()
    try:
        if accion == "cifrar":
            cifrar(entrada, args.salida or Path(str(entrada) + ".enc"), args.mostrar_claves)
        elif accion == "descifrar":
            predeterminado = Path(str(entrada)[:-4]) if str(entrada).endswith(".enc") else Path(str(entrada) + ".recuperado")
            descifrar(entrada, args.salida or predeterminado, args.mostrar_claves)
        else:
            if args.salida:
                parser.error("--salida no está disponible en modo demostración")
            print("MODO DIDÁCTICO: cifrar y descifrar con la MISMA contraseña")
            cifrado = cifrar(entrada, Path(str(entrada) + ".enc"), args.mostrar_claves)
            recuperado = descifrar(cifrado, Path(str(entrada) + ".recuperado"), args.mostrar_claves)
            inicio_hash = time.perf_counter()
            h1, h2 = sha256_archivo(entrada), sha256_archivo(recuperado)
            print(f"[TIEMPO] Comparacion SHA-256 de ambos archivos: {time.perf_counter()-inicio_hash:.4f} s")
            print("SHA-256 original:  ", h1)
            print("SHA-256 recuperado:", h2)
            print("Integridad:", "CORRECTA" if h1 == h2 else "ERROR")
            if h1 != h2:
                return 1
    except (OSError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(f"[TIEMPO] Ejecucion completa del comando (incluye espera de contrasena y verificaciones): {time.perf_counter()-inicio_total:.4f} s")
    return 0


if __name__ == "__main__":
    sys.exit(main())
