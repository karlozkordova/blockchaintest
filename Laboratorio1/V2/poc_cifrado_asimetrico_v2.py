# -*- coding: utf-8 -*-
"""LABORATORIO DIDACTICO - CIFRADO HIBRIDO DE ARCHIVOS BINARIOS.

OBJETIVO
========
Mostrar la diferencia entre criptografia asimetrica y simetrica sobre
cualquier archivo (.pdf, .iso, .docx, .zip, imagenes, binarios, etc.).

RSA-3072 + OAEP(SHA-256) cifra SOLO una clave aleatoria AES de 32 bytes.
AES-256-GCM cifra el archivo por bloques de 4 MiB; el tag comprueba
integridad y autenticidad del ciphertext ANTES de publicar el recuperado.
SHA-256 calcula huellas del archivo original y del recuperado; el hash
NO cifra ni protege la confidencialidad.

MODOS
=====
  python cifrado.py archivo.iso --mostrar-claves
      Genera claves si faltan, cifra, descifra y compara SHA-256.
  python cifrado.py generar-claves --mostrar-claves
      Guarda publica.pem y privada.pem junto a este .py.
  python cifrado.py cifrar archivo.pdf --publica publica.pem --mostrar-claves
  python cifrado.py descifrar archivo.pdf.enc --privada privada.pem --mostrar-claves

INSTALACION: python3 -m pip install cryptography

NOTAS DE SEGURIDAD
==================
* --mostrar-claves imprime secretos: SOLO para laboratorios aislados, con
  datos ficticios, sin grabar terminal ni compartir capturas o registros.
* La clave privada se almacena en PEM cifrado con contrasena; mostrarla
  requiere proporcionar la contrasena cuando se lee desde disco.
* Cada operacion usa una nueva clave AES y nonce aleatorios.
* El archivo .enc contiene: identificador + longitud + clave AES protegida
  por RSA + nonce + contenido cifrado + etiqueta GCM.
* Ni la extension ni el formato del archivo original afectan al algoritmo.
* No elimina ni sobrescribe el archivo original ni las claves existentes.
"""

import argparse
import getpass
import os
import struct
import hashlib
import time
from pathlib import Path

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

MAGIC = b"FILEHB01"
BLOCK = 4 * 1024 * 1024  # 4 MiB
BASE = Path(__file__).resolve().parent
NONCE_SIZE = 12
TAG_SIZE = 16


def sha256_archivo(ruta: Path) -> str:
    """Calcula hash por bloques para no cargar archivos ISO en RAM."""
    digest = hashlib.sha256()
    with ruta.open("rb") as fichero:
        for bloque in iter(lambda: fichero.read(BLOCK), b""):
            digest.update(bloque)
    return digest.hexdigest()


def mostrar_rsa(privada: Path, publica: Path, password: bytes | None = None):
    """Revela par de claves RSA con proposito EXCLUSIVAMENTE didactico."""
    print("\n[LABORATORIO] CLAVE PUBLICA PEM:\n", publica.read_text())
    if password is None:
        password = getpass.getpass("Contrasena para VISUALIZAR la clave privada: ").encode()
    obj = serialization.load_pem_private_key(privada.read_bytes(), password=password)
    texto = obj.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.PKCS8,
        serialization.NoEncryption(),
    )
    print("[LABORATORIO] CLAVE PRIVADA PEM SIN CIFRAR (SECRETA):\n", texto.decode())


def mostrar_valor(nombre: str, valor: bytes, activar: bool, secreto: bool = True):
    """Muestra valores hexadecimales; etiqueta adecuadamente secretos."""
    if activar:
        print(f"[LABORATORIO] {nombre}{' [SECRETO]' if secreto else ''}: {valor.hex()}")


def generar_claves(privada: Path, publica: Path, mostrar_claves=False):
    if privada.exists() or publica.exists():
        raise FileExistsError("Ya existe un archivo de claves. No se sobrescribira.")
    clave = getpass.getpass("Contrasena para proteger la clave privada: ").encode()
    if not clave:
        raise ValueError("Debes proporcionar una contrasena para la clave privada")
    confirmar = getpass.getpass("Confirmar contrasena: ").encode()
    if clave != confirmar:
        raise ValueError("Las contrasenas no coinciden")
    inicio_rsa = time.perf_counter()
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=3072)
    print(f"[TIEMPO] Generacion de claves RSA-3072: {time.perf_counter()-inicio_rsa:.4f} s")
    pem_priv = private_key.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.PKCS8,
        serialization.BestAvailableEncryption(clave),
    )
    pem_pub = private_key.public_key().public_bytes(
        serialization.Encoding.PEM,
        serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    fd = os.open(privada, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    with os.fdopen(fd, "wb") as f:
        f.write(pem_priv)
    try:
        with publica.open("xb") as f:
            f.write(pem_pub)
    except Exception:
        privada.unlink(missing_ok=True)
        raise
    print(f"Claves guardadas: {privada} (privada cifrada), {publica} (publica)")
    if mostrar_claves:
        mostrar_rsa(privada, publica, password=clave)


def cifrar(origen: Path, destino: Path, publica: Path, mostrar_claves=False):
    if not origen.is_file():
        raise FileNotFoundError(origen)
    if origen.resolve() == destino.resolve():
        raise ValueError("Origen y destino deben ser diferentes")
    inicio_preparacion = time.perf_counter()
    pub = serialization.load_pem_public_key(publica.read_bytes())
    aes_key = os.urandom(32)
    nonce = os.urandom(NONCE_SIZE)
    wrapped = pub.encrypt(
        aes_key,
        padding.OAEP(mgf=padding.MGF1(hashes.SHA256()), algorithm=hashes.SHA256(), label=None),
    )
    tiempo_preparacion = time.perf_counter() - inicio_preparacion
    print(f"[TIEMPO] Preparacion AES + RSA-OAEP (envolver clave): {tiempo_preparacion:.4f} s")
    mostrar_valor("Clave AES-256 generada", aes_key, mostrar_claves)
    mostrar_valor("Clave AES cifrada mediante RSA-OAEP", wrapped, mostrar_claves, False)
    mostrar_valor("Nonce GCM", nonce, mostrar_claves, False)
    # Formato: MAGIC + longitud RSA (2 bytes) + RSA(clave AES) + nonce + ciphertext + tag
    encryptor = Cipher(algorithms.AES(aes_key), modes.GCM(nonce)).encryptor()
    inicio_datos = time.perf_counter()
    with origen.open("rb") as src, destino.open("xb") as dst:
        dst.write(MAGIC + struct.pack(">H", len(wrapped)) + wrapped + nonce)
        while chunk := src.read(BLOCK):
            dst.write(encryptor.update(chunk))
        dst.write(encryptor.finalize())
        dst.write(encryptor.tag)
    mostrar_valor("Tag de autenticacion GCM", encryptor.tag, mostrar_claves, False)
    tiempo_datos = time.perf_counter() - inicio_datos
    print(f"Archivo cifrado: {destino} ({destino.stat().st_size} bytes)")
    print(f"[TIEMPO] Cifrado AES-GCM del archivo (lectura/escritura): {tiempo_datos:.4f} s")
    print(f"[TIEMPO] Total cifrado (preparacion RSA + AES, sin ingreso de contrasena): {tiempo_preparacion+tiempo_datos:.4f} s")


def descifrar(origen: Path, destino: Path, privada: Path, mostrar_claves=False):
    if not origen.is_file():
        raise FileNotFoundError(origen)
    if origen.resolve() == destino.resolve():
        raise ValueError("Origen y destino deben ser diferentes")
    password = getpass.getpass("Contrasena de la clave privada: ").encode()
    inicio_rsa = time.perf_counter()
    key = serialization.load_pem_private_key(privada.read_bytes(), password=password)
    tamano = origen.stat().st_size
    with origen.open("rb") as src:
        if src.read(len(MAGIC)) != MAGIC:
            raise ValueError("Formato de archivo cifrado no reconocido")
        wrapped_len_bytes = src.read(2)
        if len(wrapped_len_bytes) != 2:
            raise ValueError("Archivo truncado")
        wrapped_len = struct.unpack(">H", wrapped_len_bytes)[0]
        header_len = len(MAGIC) + 2 + wrapped_len + NONCE_SIZE
        if wrapped_len == 0 or tamano < header_len + TAG_SIZE:
            raise ValueError("Archivo cifrado incompleto")
        wrapped = src.read(wrapped_len)
        nonce = src.read(NONCE_SIZE)
        aes_key = key.decrypt(
            wrapped,
            padding.OAEP(mgf=padding.MGF1(hashes.SHA256()), algorithm=hashes.SHA256(), label=None),
        )
        tiempo_rsa = time.perf_counter() - inicio_rsa
        print(f"[TIEMPO] Apertura de clave privada + RSA-OAEP (recuperar AES): {tiempo_rsa:.4f} s")
        mostrar_valor("Clave AES recuperada por RSA", aes_key, mostrar_claves)
        mostrar_valor("Nonce GCM recuperado", nonce, mostrar_claves, False)
        src.seek(tamano - TAG_SIZE)
        tag = src.read(TAG_SIZE)
        mostrar_valor("Tag GCM almacenado", tag, mostrar_claves, False)
        src.seek(header_len)
        decryptor = Cipher(algorithms.AES(aes_key), modes.GCM(nonce, tag)).decryptor()
        remaining = tamano - header_len - TAG_SIZE
        # Escribir a temporal para no presentar datos incompletos como validos.
        temporal = destino.with_name(destino.name + ".partial")
        inicio_datos = time.perf_counter()
        try:
            with temporal.open("xb") as dst:
                while remaining:
                    chunk = src.read(min(BLOCK, remaining))
                    if not chunk:
                        raise ValueError("Archivo truncado")
                    remaining -= len(chunk)
                    dst.write(decryptor.update(chunk))
                dst.write(decryptor.finalize())  # verifica autenticidad GCM
            if destino.exists():
                raise FileExistsError(f"Ya existe: {destino}")
            temporal.rename(destino)
        except BaseException:
            temporal.unlink(missing_ok=True)
            raise
    tiempo_datos = time.perf_counter() - inicio_datos
    print(f"Archivo recuperado y autenticado: {destino}")
    print(f"[TIEMPO] Descifrado AES-GCM del archivo (lectura/escritura): {tiempo_datos:.4f} s")
    print(f"[TIEMPO] Total descifrado (RSA + AES, sin ingreso de contrasena): {tiempo_rsa+tiempo_datos:.4f} s")


def main():
    import sys
    # Modo directo: python cifrado.py archivo.pdf [--mostrar-claves]
    actions = {"generar-claves", "cifrar", "descifrar"}
    inicio = time.perf_counter()
    if len(sys.argv) in (2, 3) and sys.argv[1] not in actions and not sys.argv[1].startswith("-") and (len(sys.argv) == 2 or sys.argv[2] == "--mostrar-claves"):
        mostrar = "--mostrar-claves" in sys.argv
        origen = Path(sys.argv[1])
        if not origen.is_file():
            raise FileNotFoundError(origen)
        publica, privada = BASE / "publica.pem", BASE / "privada.pem"
        if not publica.exists() and not privada.exists():
            generar_claves(privada, publica, mostrar)
        elif not publica.is_file() or not privada.is_file():
            raise ValueError("Falta una de las claves. No se regeneran claves existentes.")
        elif mostrar:
            mostrar_rsa(privada, publica)
        destino = Path(str(origen) + ".enc")
        restaurado = origen.with_name(origen.name + ".recuperado")
        print("[1] Archivo:", origen, "(", origen.stat().st_size, "bytes)")
        inicio_hash = time.perf_counter()
        print("[2] SHA-256 original:", sha256_archivo(origen))
        print(f"[TIEMPO] SHA-256 original: {time.perf_counter()-inicio_hash:.4f} s")
        cifrar(origen, destino, publica, mostrar)
        descifrar(destino, restaurado, privada, mostrar)
        inicio_hash = time.perf_counter()
        hash_final = sha256_archivo(restaurado)
        print(f"[TIEMPO] SHA-256 recuperado: {time.perf_counter()-inicio_hash:.4f} s")
        print("[3] SHA-256 recuperado:", hash_final)
        print("[4] Integridad SHA-256:", "CORRECTA" if sha256_archivo(origen) == hash_final else "FALLIDA")
        print(f"[5] Tiempo total: {time.perf_counter()-inicio:.3f} segundos")
        return
    # Modo por comandos: generar-claves | cifrar | descifrar
    actions = {"generar-claves", "cifrar", "descifrar"}
    p = argparse.ArgumentParser(description="Cifrado hibrido RSA + AES-GCM de archivos binarios")
    sub = p.add_subparsers(dest="accion", required=True)
    g = sub.add_parser("generar-claves", help="Guardar claves junto al script")
    g.add_argument("--mostrar-claves", action="store_true", help="Revela secretos SOLO en un laboratorio")
    g.add_argument("--privada", type=Path, default=BASE / "privada.pem")
    g.add_argument("--publica", type=Path, default=BASE / "publica.pem")
    e = sub.add_parser("cifrar", help="Cifrar con clave publica")
    e.add_argument("--mostrar-claves", action="store_true", help="Muestra clave AES y parametros")
    e.add_argument("archivo", type=Path)
    e.add_argument("--publica", type=Path, default=BASE / "publica.pem")
    e.add_argument("--salida", type=Path)
    d = sub.add_parser("descifrar", help="Descifrar con clave privada")
    d.add_argument("--mostrar-claves", action="store_true", help="Muestra clave AES recuperada")
    d.add_argument("archivo", type=Path)
    d.add_argument("--privada", type=Path, default=BASE / "privada.pem")
    d.add_argument("--salida", type=Path)
    args = p.parse_args()
    if args.accion == "generar-claves":
        generar_claves(args.privada, args.publica, args.mostrar_claves)
    elif args.accion == "cifrar":
        inicio_hash = time.perf_counter()
        print("SHA-256 original:", sha256_archivo(args.archivo))
        print(f"[TIEMPO] SHA-256 original: {time.perf_counter()-inicio_hash:.4f} s")
        cifrar(args.archivo, args.salida or Path(str(args.archivo) + ".enc"), args.publica, args.mostrar_claves)
    else:
        default = Path(str(args.archivo).removesuffix(".enc") + ".recuperado")
        salida = args.salida or default
        descifrar(args.archivo, salida, args.privada, args.mostrar_claves)
        inicio_hash = time.perf_counter()
        print("SHA-256 recuperado:", sha256_archivo(salida))
        print(f"[TIEMPO] SHA-256 recuperado: {time.perf_counter()-inicio_hash:.4f} s")


if __name__ == "__main__":
    try:
        main()
    except (ValueError, FileNotFoundError, FileExistsError, InvalidTag, TypeError) as exc:
        raise SystemExit(f"Error: {exc}")
