
# 🔐 PoC de Cifrado Simétrico y Asimétrico

Este repositorio contiene una **Prueba de Concepto (PoC)** para comprender y aplicar conceptos clave de criptografía en el contexto de seguridad en blockchain y sistemas distribuidos. Se exploran dos enfoques de cifrado:

✅ **Cifrado Simétrico** → Basado en una misma clave para cifrar y descifrar datos.  
✅ **Cifrado Asimétrico** → Basado en un par de claves **pública** y **privada** para operaciones de cifrado/descifrado y firma/verificación.

Se incluye también una **interfaz web** para ilustrar cómo funcionan las claves públicas y privadas en el cifrado asimétrico.

---

## 📂 Estructura del Repositorio

- **`poc_cifrado_simetrico.py`**  
  Implementa una prueba con algoritmos simétricos (por ejemplo AES o Fernet).  
  - Genera una clave simétrica.  
  - Cifra un texto plano proporcionado por el usuario en el archivo.  
  - Descifra el mensaje para validar que se mantiene la integridad.  
  - Útil para entender cómo funciona la **confidencialidad** en canales privados.

- **`poc_cifrado_asimetrico.py`**  
  Implementa una prueba con cifrado asimétrico (por ejemplo RSA).  
  - Genera un par de claves pública/privada.  
  - Cifra datos con la clave pública y los descifra con la clave privada.  
  - Permite firmar datos digitalmente y verificar la firma con la clave pública.  
  - Útil para comprender **autenticidad** y **no repudio**.

- **`keypubpriv.html`**  
  Interfaz web interactiva que simula el proceso de cifrado y descifrado con claves públicas y privadas.  
  - Permite a los usuarios introducir un mensaje, cifrarlo con una clave pública y visualizar cómo sólo la clave privada correspondiente puede descifrarlo.  
  - Ayuda a visualizar la diferencia con el enfoque simétrico.

---

## ✅ Prerrequisitos

Antes de ejecutar la PoC, asegúrate de tener configurado el entorno:

1. **Python 3.8+** instalado en tu sistema.  
2. Librerías necesarias:

   ```bash
   pip install cryptography pycryptodome flask
   ```

3. Un navegador web para abrir la interfaz **HTML**.

Opcional: se recomienda usar un **entorno virtual** para aislar dependencias.

---

## ▶️ Ejecución

### 1. Prueba de Cifrado Simétrico

```bash
python poc_cifrado_simetrico.py
```

- Ingresa un mensaje.  
- Se mostrará el texto cifrado y luego el descifrado.  
- Confirma que **con la misma clave se logra cifrar y descifrar**, demostrando rapidez pero dependencia en la distribución segura de la clave.

---

### 2. Prueba de Cifrado Asimétrico

```bash
python poc_cifrado_asimetrico.py
```

- Se generará un par de claves.  
- Se cifra un mensaje con la **clave pública** y sólo podrá ser descifrado con la **clave privada**.  
- También se muestra cómo **firmar** un mensaje y verificar la firma.

---

### 3. Interfaz Web (Claves Públicas/Privadas)

Abre en el navegador el archivo:

```bash
keypubpriv.html
```

Podrás interactuar con el flujo de:  
- **Cifrado con clave pública → Descifrado con clave privada**  
- **Firma digital con clave privada → Verificación con clave pública**

---

## 📊 Interpretación de Resultados

- En el **cifrado simétrico**, notarás que:  
  - Es más rápido y eficiente.  
  - Pero requiere compartir **la misma clave secreta** de forma segura.

- En el **cifrado asimétrico**, observarás que:  
  - La clave pública puede compartirse abiertamente.  
  - Solo la clave privada puede descifrar o firmar mensajes.  
  - Es más seguro para entornos abiertos, pero **menos eficiente** en grandes volúmenes de datos.

- La interfaz web refuerza visualmente **qué rol juega cada clave** y cómo se integran para **confidencialidad, integridad y autenticación**.

---

## 🎯 Conocimiento Adquirido

Con esta PoC comprenderás:

- La **diferencia entre cifrado simétrico y asimétrico**.  
- Cómo funcionan **claves públicas y privadas** para proteger datos.  
- Por qué ambos esquemas suelen **complementarse** (por ejemplo, simétrico para el canal y asimétrico para intercambiar la clave).  
- Fundamentos aplicables a **blockchain**, como la firma de transacciones y la gestión de llaves.


## 📊 Entregables:

1. **Código fuente** (Python o similar) desarollo propio o pueden tomar como referencia el mismo del laboratorio, donde se prueben al menos dos algoritmos de hash y un esquema de firma digital.
2. **Capturas de ejecución** que muestren la generación del hash, la firma digital y su verificación.
3. **Reporte técnico** en PDF que incluya:
   - Descripción de los algoritmos usados.
   - Comparación de resultados (velocidad, tamaño de hash, facilidad de verificación).
   - Análisis de cómo estas herramientas contribuyen a la seguridad en blockchain.
4. **Reflexión final:** un apartado (½ a 1 página) donde el estudiante destaque la importancia de la criptografía en la integridad y autenticidad de transacciones.
    
