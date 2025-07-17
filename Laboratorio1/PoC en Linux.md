
# 🖥️ Prueba de Cifrado en Ubuntu (Línea de Comandos)

Este documento explica cómo realizar **cifrado simétrico y asimétrico directamente desde la terminal en Ubuntu** usando **OpenSSL**.  
Es un **tercer método de prueba** complementario a las PoC en Python y la interfaz web.

---

## ✅ 1. Instalar Dependencias

En Ubuntu, asegúrate de tener **OpenSSL** instalado (la mayoría de distribuciones ya lo incluyen). Si no, ejecútalo:

```bash
sudo apt update
sudo apt install openssl -y
```

Verifica la versión instalada:

```bash
openssl version
```

---

## 🔐 2. Cifrado Simétrico con AES-256

Este ejemplo usa **AES-256-CBC**, un algoritmo estándar de cifrado simétrico.

1️⃣ **Crear un archivo de texto con el mensaje a cifrar**:

```bash
echo "Este es un mensaje confidencial para la prueba de cifrado simétrico." > mensaje.txt
```

2️⃣ **Cifrar el archivo usando AES-256-CBC**:

```bash
openssl enc -aes-256-cbc -salt -in mensaje.txt -out mensaje_cifrado.bin
```

Te pedirá una **contraseña** que actuará como clave simétrica.

3️⃣ **Descifrar el archivo**:

```bash
openssl enc -aes-256-cbc -d -in mensaje_cifrado.bin -out mensaje_descifrado.txt
```

Verifica que el mensaje descifrado es el original:

```bash
cat mensaje_descifrado.txt
```

✅ **Aprendizaje:**  
- Mismo algoritmo y misma clave para cifrar/descifrar.  
- Necesitas compartir **la clave secreta** de forma segura entre emisor y receptor.

---

## 🔑 3. Cifrado Asimétrico con RSA

Este ejemplo usa **RSA 2048 bits** para demostrar el cifrado con clave pública/privada.

1️⃣ **Generar un par de claves RSA**:

```bash
# Generar clave privada protegida con AES256
openssl genpkey -algorithm RSA -out clave_privada.pem -aes256 -pkeyopt rsa_keygen_bits:2048

# Extraer la clave pública
openssl rsa -pubout -in clave_privada.pem -out clave_publica.pem
```

2️⃣ **Cifrar un archivo con la clave pública**:

```bash
openssl rsautl -encrypt -inkey clave_publica.pem -pubin -in mensaje.txt -out mensaje_rsa_cifrado.bin
```

3️⃣ **Descifrar el archivo con la clave privada**:

```bash
openssl rsautl -decrypt -inkey clave_privada.pem -in mensaje_rsa_cifrado.bin -out mensaje_rsa_descifrado.txt
```

Comprueba que el mensaje descifrado es el mismo:

```bash
cat mensaje_rsa_descifrado.txt
```

✅ **Aprendizaje:**  
- Cualquiera puede cifrar usando **la clave pública**.  
- **Solo el dueño de la clave privada** puede descifrar el mensaje.

---

## 📦 Paquetes Necesarios

En Ubuntu solo se necesita instalar:

```bash
sudo apt update
sudo apt install openssl -y
```

No requiere dependencias adicionales.

---

## 📝 Comparación con Otros Métodos

| Método               | Ventaja                                | Desventaja                           |
|----------------------|----------------------------------------|---------------------------------------|
| **Python Simétrico** | Fácil integración y automatización     | Requiere instalar librerías extras    |
| **Python Asimétrico**| Permite firmas digitales y autenticación| Más complejo para grandes volúmenes |
| **HTML Interactivo** | Visual e intuitivo para explicar       | Solo demostrativo                    |
| **OpenSSL CLI**      | Nativo en Linux, estándar en servidores| Menos amigable para principiantes    |

---

## 🚀 Automatización Opcional

Este proceso se puede automatizar con un **script Bash** que realice el cifrado/descifrado automáticamente para pruebas repetitivas.

