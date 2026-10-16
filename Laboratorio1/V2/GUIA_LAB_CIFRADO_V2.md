# 🔐 PoC de Cifrado Simétrico y Asimétrico de Archivos

Este laboratorio contiene una **Prueba de Concepto (PoC)** para comprender conceptos de criptografía aplicados a la seguridad de la información, blockchain y sistemas distribuidos. A diferencia de los ejemplos basados en mensajes de texto, aquí se cifra y recupera **cualquier archivo binario** (`.pdf`, `.docx`, `.zip`, `.jpg`, `.iso`, etc.), incluso si tiene varios gigabytes.

✅ **Cifrado Simétrico** → Una contraseña permite derivar la misma clave AES para cifrar y descifrar.  
✅ **Cifrado Asimétrico (híbrido)** → Se usa una clave pública RSA para proteger una clave AES aleatoria y una clave privada RSA para recuperarla.  
✅ **Hash SHA-256** → Permite comparar el archivo original y el recuperado, sin cifrar ni descifrar información.

> **Diferencia fundamental:** ambos programas utilizan **AES-256-GCM** para cifrar y descifrar los archivos. La diferencia está en **cómo se obtiene, protege y recupera la clave AES**. En el cifrado simétrico, una contraseña permite derivar la clave mediante **PBKDF2**; para recuperarla se necesita la misma contraseña y el *salt* guardado con el archivo cifrado. En el cifrado asimétrico híbrido, se genera una **clave AES aleatoria**, que se protege utilizando la **clave pública RSA** y se recupera mediante la **clave privada RSA**. Por tanto, **RSA no cifra directamente la ISO: cifra únicamente la clave que permite descifrarla con AES**.
>
> **Advertencia didáctica:** `--mostrar-claves` muestra secretos en pantalla. Usarlo solo con datos, contraseñas y claves de laboratorio. No compartir capturas con secretos reales ni subir estas claves a un repositorio.

---

## 📂 Estructura del Repositorio

- **`poc_cifrado_simetrico_v2.py`**  
  PoC de cifrado simétrico **AES-256-GCM** con clave derivada de contraseña usando **PBKDF2-HMAC-SHA256**.  
  - Lee y cifra archivos binarios por bloques de 4 MiB.  
  - Permite cifrar y descifrar en una sola ejecución o por separado.  
  - Solicita la contraseña de forma interactiva.  
  - Muestra, opcionalmente, contraseña, clave derivada, *salt*, *nonce* y *tag* GCM.  
  - Genera el archivo `.enc` y permite verificar el archivo recuperado.  
  - Mide por separado la derivación PBKDF2, cifrado AES, descifrado AES, SHA-256 y tiempo total.

- **`poc_cifrado_asimetrico_v2.py`**  
  PoC de cifrado **híbrido RSA-3072 + AES-256-GCM**.  
  - Genera `publica.pem` y `privada.pem` (la privada protegida con contraseña).  
  - Cifra el archivo con AES y protege la clave AES con la clave pública RSA.  
  - Descifra recuperando la clave AES mediante la clave privada RSA.  
  - Permite ejecución directa o comandos separados para generar claves, cifrar y descifrar.  
  - Muestra, opcionalmente, claves y parámetros criptográficos con fines didácticos.  
  - Mide generación RSA, protección/recuperación de AES, cifrado/descifrado AES y hashes.

- **`archivo_prueba.iso`** (o cualquier archivo disponible en el laboratorio)  
  Archivo de entrada que se usará **en ambos procedimientos** para observar las diferencias de tiempo, tamaño y gestión de claves.

> Estos dos scripts **no implementan firma digital** ni incorporan una interfaz HTML. Una firma digital con Ed25519 o RSA-PSS puede estudiarse en otra práctica; **cifrar con una clave pública no equivale a firmar**.

---

## ✅ Prerrequisitos

Antes de ejecutar la PoC, se debe instalar las dependencias en Linux o WSL o una distribución Linux equivalente:

1. **Python 3** y espacio libre suficiente para almacenar el original, el `.enc` y el archivo recuperado. Para una ISO grande se recomienda disponer de **al menos tres veces su tamaño** como espacio libre durante el laboratorio.
2. **Dependencias y herramientas para medir tiempos**:

   ```bash
   sudo apt update
   sudo apt install -y python3 python3-venv time
   python3 -m venv .venv
   source .venv/bin/activate
   python3 -m pip install cryptography
   ```

3. Guardar los dos programas en una carpeta y verificar su existencia:

   ```bash
   ls -lh poc_cifrado_simetrico_v2.py  poc_cifrado_asimetrico_v2.py
   ```

4. Colocar en una ruta conocida el archivo que se va a cifrar. En estos ejemplos se usará **`archivo_prueba.iso`**. Pueden sustituirlo por cualquier otro nombre o ruta.

5. Consultar la ayuda de los programas:

   ```bash
   python3 poc_cifrado_simetrico_v2.py --help
   python3 poc_cifrado_asimetrico_v2.py --help
   ```

> Los dos programas necesitan la biblioteca `cryptography`. No es necesario instalar `flask` ni `pycryptodome` para ejecutar estas versiones.

---

## ▶️ Ejecución

### 1. Prueba de Cifrado Simétrico — AES-256-GCM

**Objetivo:** comprobar cómo **una contraseña compartida** permite cifrar y recuperar un archivo completo.

**Opción A. Cifrar y descifrar automáticamente:**

```bash
python3 poc_cifrado_simetrico_v2.py archivo_prueba.iso --mostrar-claves
```

- Introducir la contraseña solicitada para cifrar y volver a ingresarla para descifrar.
- Observar el *salt* aleatorio y cómo PBKDF2-HMAC-SHA256 deriva una clave AES de 256 bits.
- Observar el *nonce* y el *tag* de autenticación de AES-GCM.
- Se crean `archivo_prueba.iso.enc` y `archivo_prueba.iso.recuperado`.
- Se comparan los hashes SHA-256 del original y del recuperado.

**Opción B. Ejecutar cada operación por separado:**

**Cifrar el archivo:**

```bash
python3 poc_cifrado_simetrico_v2.py cifrar archivo_prueba.iso --mostrar-claves
```

**Descifrar con la misma contraseña:**

```bash
python3 poc_cifrado_simetrico_v2.py descifrar archivo_prueba.iso.enc \
  --salida archivo_simetrico_recuperado.iso --mostrar-claves
```

**Validar la integridad:**

```bash
sha256sum archivo_prueba.iso archivo_simetrico_recuperado.iso
```

Los valores SHA-256 deben coincidir exactamente. Si la contraseña es incorrecta o el archivo cifrado fue alterado, la autenticación GCM debe fallar.

**Tiempos que presenta automáticamente el programa:**

```text
[TIEMPO] Derivacion de clave PBKDF2 (cifrado): ... s
[TIEMPO] Cifrado AES-GCM del archivo (lectura/escritura): ... s
[TIEMPO] Total cifrado (PBKDF2 + AES, sin ingreso de contrasena): ... s
[TIEMPO] Derivacion de clave PBKDF2 (descifrado): ... s
[TIEMPO] Descifrado AES-GCM del archivo (lectura/escritura): ... s
[TIEMPO] Total descifrado (PBKDF2 + AES, sin ingreso de contrasena ni hash): ... s
[TIEMPO] Calculo SHA-256 recuperado: ... s
```

> Los valores `...` son marcadores: el programa mostrará los segundos reales. En modo directo también se informa el tiempo completo, que **sí incluye** la espera al introducir contraseñas y las verificaciones. Para comparar rendimiento criptográfico, utilizar los tiempos parciales que excluyen esa espera.

**¿Qué observar en el cifrado simétrico?**

- Una misma contraseña permite volver a **derivar** la clave AES con el *salt* almacenado.
- El *salt* y el *nonce* son parámetros públicos, pero la contraseña y la clave AES son secretas.
- Dos ejecuciones sobre el mismo archivo normalmente producen cifrados diferentes por la aleatoriedad.
- El archivo cifrado conserva casi el mismo tamaño: en este formato se añaden **52 bytes** (identificador, *salt*, *nonce* y *tag*).

---

### 2. Prueba de Cifrado Asimétrico (Híbrido) — RSA-3072 + AES-256-GCM

**Objetivo:** observar el uso de **dos claves RSA (pública y privada)** para proteger y recuperar la **clave AES** que cifra el archivo.

**Opción A. Generar claves, cifrar y descifrar automáticamente:**

```bash
python3 poc_cifrado_asimetrico_v2.py archivo_prueba.iso --mostrar-claves
```

- Si no existen las claves necesarias, el programa genera `publica.pem` y `privada.pem` junto al script.
- Solicita una contraseña para proteger la clave privada RSA.
- Genera una clave AES aleatoria, cifra el archivo con AES-256-GCM y protege la clave AES con RSA-OAEP-SHA256.
- Recupera la clave AES con la privada RSA, descifra el archivo y compara SHA-256.
- Genera `archivo_prueba.iso.enc` y `archivo_prueba.iso.recuperado`.

**Opción B. Generar y reutilizar las claves:**

**Generar par de claves:**

```bash
python3 poc_cifrado_asimetrico_v2.py generar-claves --mostrar-claves
```

Los archivos `publica.pem` y `privada.pem` se crean en el directorio del programa. Guardar la clave privada y su contraseña: **sin ellas no se podrá recuperar el archivo cifrado**.

**Cifrar con la clave pública:**

```bash
python3 poc_cifrado_asimetrico_v2.py cifrar archivo_prueba.iso \
  --publica publica.pem --salida archivo_asimetrico.iso.enc --mostrar-claves
```

**Descifrar con la clave privada:**

```bash
python3 poc_cifrado_asimetrico_v2.py descifrar archivo_asimetrico.iso.enc \
  --privada privada.pem --salida archivo_asimetrico_recuperado.iso --mostrar-claves
```

**Validar la integridad:**

```bash
sha256sum archivo_prueba.iso archivo_asimetrico_recuperado.iso
```

**Tiempos que presenta automáticamente el programa:**

```text
[TIEMPO] Generacion de claves RSA-3072: ... s
[TIEMPO] Preparacion AES + RSA-OAEP (envolver clave): ... s
[TIEMPO] Cifrado AES-GCM del archivo (lectura/escritura): ... s
[TIEMPO] Total cifrado (preparacion RSA + AES, sin ingreso de contrasena): ... s
[TIEMPO] Apertura de clave privada + RSA-OAEP (recuperar AES): ... s
[TIEMPO] Descifrado AES-GCM del archivo (lectura/escritura): ... s
[TIEMPO] Total descifrado (RSA + AES, sin ingreso de contrasena): ... s
[TIEMPO] SHA-256 original: ... s
[TIEMPO] SHA-256 recuperado: ... s
```

> El tiempo de **generación RSA** aparece cuando se generan las claves, no cada vez que se cifra. El tiempo de **apertura de clave privada** incluye su carga y el descifrado RSA-OAEP de la clave AES. Estos valores no equivalen al tiempo de AES aplicado al archivo completo.

**¿Qué observar en el cifrado híbrido?**

- La **clave pública RSA** permite cifrar la clave AES sin conocer la clave privada.
- La **clave privada RSA** permite recuperar la clave AES y descifrar los datos.
- RSA-3072 + OAEP-SHA256 cifra únicamente una clave AES de 32 bytes, **no toda la ISO**.
- La clave privada PEM requiere una contraseña, además de ser distinta de la clave AES del archivo.
- En este formato y con RSA-3072 se añaden **422 bytes** al tamaño del archivo original.

> **Importante al repetir la práctica:** ambos programas generan nombres similares (`archivo_prueba.iso.enc`). Utilizar el argumento `--salida` o carpetas distintas para no confundir los resultados. Ninguno de los formatos `.enc` se descifra con el otro programa.

---

### 3. Práctica comparativa: un mismo archivo grande

Seleccionar **el mismo archivo** (por ejemplo, una ISO de **1 a 4 GB**) y ejecutar ambos procedimientos por separado. Para no sobrescribir resultados y guardar salidas con nombres diferentes.

**Primero, registrar los tiempos internos `[TIEMPO]` que muestran los scripts.** Son las mediciones principales para distinguir el costo de la gestión de claves del procesamiento del archivo. Si desean medir además el consumo de memoria y el tiempo real total del sistema, utilizar `/usr/bin/time -v` como complemento o equivalente.

**Medir cifrado simétrico:**

```bash
/usr/bin/time -v python3 poc_cifrado_simetrico_v2.py cifrar \
  archivo_prueba.iso --salida archivo_simetrico.iso.enc
```

**Medir cifrado híbrido (se generan previamente las claves si aún no existen):**

```bash
python3 poc_cifrado_asimetrico_v2.py generar-claves

/usr/bin/time -v python3 poc_cifrado_asimetrico_v2.py cifrar \
  archivo_prueba.iso --publica publica.pem \
  --salida archivo_asimetrico.iso.enc
```

**Cómo interpretar dos mediciones de tiempo diferentes:**

- **`[TIEMPO] Total cifrado` y `[TIEMPO] Total descifrado`:** suma de las etapas criptográficas medidas por el script; excluye la espera de la contraseña. No incluye necesariamente el cálculo posterior del hash.
- **`[TIEMPO] Cifrado/Descifrado AES-GCM`:** tiempo para procesar el contenido y leer/escribir el archivo; no es una medición exclusiva de CPU del algoritmo AES.
- **`Elapsed (wall clock) time` de `/usr/bin/time -v`:** tiempo de todo el proceso, incluyendo esperas de contraseña, arranque de Python y otras actividades.
- **`Maximum resident set size`:** máximo uso de memoria residente durante la ejecución.
- **Generación de claves RSA:** registrar por separado y no añadir al cifrado de cada archivo cuando se reutilicen claves.

**Comparar tamaños exactos:**

```bash
stat -c '%n: %s bytes' \
  archivo_prueba.iso \
  archivo_simetrico.iso.enc \
  archivo_asimetrico.iso.enc
```
```bash
ls -al \
  archivo_prueba.iso \
  archivo_simetrico.iso.enc \
  archivo_asimetrico.iso.enc
```


**Medir descifrado (con las contraseñas correspondientes):**

```bash
/usr/bin/time -v python3 poc_cifrado_simetrico_v2.py descifrar \
  archivo_simetrico.iso.enc --salida archivo_simetrico_recuperado.iso

/usr/bin/time -v python3 poc_cifrado_asimetrico_v2.py descifrar \
  archivo_asimetrico.iso.enc --privada privada.pem \
  --salida archivo_asimetrico_recuperado.iso
```

**Comprobar que ambos recuperados son idénticos al original:**

```bash
sha256sum archivo_prueba.iso \
  archivo_simetrico_recuperado.iso \
  archivo_asimetrico_recuperado.iso
```

Opción de registro de los resultados:

| Indicador | Simétrico (AES + PBKDF2) | Híbrido (RSA + AES) |
|---|---|---|
| Tamaño original (bytes) | | |
| Tamaño cifrado (bytes) | | |
| Incremento de tamaño (bytes) | | |
| Tiempo de preparación/derivación de clave para cifrar (s) | | |
| Tiempo AES-GCM cifrado (s) | | |
| Tiempo total interno de cifrado (s) | | |
| Tiempo de recuperación/derivación de clave para descifrar (s) | | |
| Tiempo AES-GCM descifrado (s) | | |
| Tiempo total interno de descifrado (s) | | |
| Tiempo SHA-256 (s) | | |
| Tiempo de generación RSA (s; separado) | No aplica | |
| Tiempo `Elapsed (wall clock)` de cifrado | | |
| Tiempo `Elapsed (wall clock)` de descifrado | | |
| Memoria máxima `Maximum resident set size` | | |
| SHA-256 recuperado coincide | Sí / No | Sí / No |
| Mecanismo de gestión de claves | Contraseña + PBKDF2 | Claves RSA |

> Ejecutar las pruebas en condiciones comparables: mismo archivo, equipo y unidad de almacenamiento, sin cargas importantes en segundo plano. Realizar varias mediciones si desean comparar rendimiento. **Ambos programas usan AES para el archivo**: la diferencia de tiempo puede deberse principalmente al costo de PBKDF2, a la generación/carga de claves y al sistema de archivos, no a que RSA procese todos los gigabytes.

---

## 📊 Interpretación de Resultados

### 🔑 ¿Qué diferencias se pueden identificar entre ambos mecanismos de cifrado?

| Pregunta | Cifrado simétrico (AES + PBKDF2) | Cifrado asimétrico híbrido (RSA + AES) |
|---|---|---|
| ¿Qué cifra el contenido del archivo? | AES-256-GCM | AES-256-GCM |
| ¿Cómo se obtiene la clave AES? | Se deriva de una contraseña y un *salt* mediante PBKDF2 | Se genera aleatoriamente para el archivo |
| ¿Cómo se protege o recupera la clave? | Se vuelve a derivar con la misma contraseña y el *salt* | RSA-OAEP la cifra con la clave pública y la recupera con la clave privada |
| ¿Qué secreto debe conservar quien descifra? | La contraseña | La clave privada RSA y su contraseña de protección, si corresponde |
| ¿RSA cifra directamente los gigabytes de la ISO? | No se utiliza RSA | No; cifra solo la clave AES |

**Ejemplo con una ISO de 4 GB:** el programa simétrico deriva una clave AES a partir de la contraseña; el híbrido genera una clave AES aleatoria y cifra esa clave con RSA. En ambos casos, **AES-256-GCM procesa los 4 GB de datos**. Por eso, los tiempos de cifrado del contenido pueden ser similares; las diferencias adicionales dependen de PBKDF2, las operaciones RSA, la gestión de claves y la lectura/escritura en disco.

- **En el cifrado simétrico**, se observa:  
  - La contraseña es el secreto compartido para cifrar y descifrar.  
  - PBKDF2 agrega un costo de derivación de clave que también aparece en los tiempos medidos.  
  - Separar el costo de PBKDF2 del tiempo empleado en lectura, cifrado AES y escritura.  
  - AES-GCM proporciona confidencialidad y detección de alteraciones mediante un *tag*.

- **En el cifrado híbrido**, se observa:  
  - La clave pública puede distribuirse para cifrar; la clave privada debe protegerse.  
  - RSA cifra solamente la clave AES; por eso es viable trabajar con archivos ISO grandes.  
  - AES-GCM vuelve a ser el responsable de cifrar los datos del archivo.  
  - Comparar por separado el tiempo de RSA-OAEP y el tiempo AES-GCM; la generación RSA se mide una sola vez al crear las claves.

- **En la comprobación SHA-256**, se observa:  
  - Los hashes de **original y recuperado** deben coincidir.  
  - El hash del `.enc` será diferente del hash del original.  
  - Un hash no es un cifrado ni demuestra por sí solo quién generó el archivo.

- **En el tamaño**, se comprueba:  
  - AES-GCM no expande sustancialmente el contenido; estos formatos agregan metadatos.  
  - El programa simétrico agrega **52 bytes** y el híbrido **422 bytes** cuando se emplea RSA-3072.  
  - En archivos de gigabytes, ambos incrementos pueden quedar ocultos por el redondeo del gestor de archivos.

- **En blockchain**, los resultados se relacionan con:  
  - Protección de información confidencial **fuera de la cadena** (*off-chain*).  
  - Uso de hashes para comprobar integridad de datos.  
  - Diferencia entre **cifrado** y **firma digital**: las transacciones sobre una red blockchain como Solana se autorizan mediante firmas; estos scripts son laboratorios de cifrado, no de firma de transacciones (estas se verán más adelante).

---

## 🎯 Conocimiento Adquirido

Al finalizar esta práctica, será capaz de comprender:

- La diferencia entre **cifrado simétrico**, **cifrado asimétrico/híbrido** y **hash**.
- Por qué no resulta adecuado aplicar RSA directamente a un archivo de varios gigabytes.
- Cómo se generan, protegen y utilizan **contraseñas, claves AES, claves públicas y privadas RSA**.
- Qué función cumplen *salt*, *nonce*, *tag* GCM y el hash SHA-256.
- Cómo comprobar la **integridad del archivo recuperado** y detectar errores de autenticación.
- Cómo medir **tiempos por etapa, tiempo total, tamaños y memoria** sin confundir el cifrado de los datos con la gestión de claves.
- Cómo se relacionan estos principios con la **seguridad de aplicaciones y blockchain**.

---
