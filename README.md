
# 🔐 Laboratorios de Seguridad en Blockchain

Bienvenido a la serie de **Laboratorios de Seguridad en Blockchain**.  
Estos ejercicios prácticos complementan los conocimientos adquiridos sobre **criptografía, inmutabilidad, anonimicidad, contratos inteligentes, ataques y mitigaciones en blockchain**.

Los laboratorios están diseñados para **aprender haciendo**, explorando vulnerabilidades, ejecutando transacciones y entendiendo cómo la seguridad se refleja en la práctica.

---

## 🎯 ¿Qué aprenderás?

✅ Explorarás transacciones reales en la blockchain y comprenderás sus componentes de seguridad.  
✅ Ejecutarás pruebas de concepto (PoC) en **Remix IDE** y redes de prueba como **Sepolia Testnet**.  
✅ Analizarás vulnerabilidades clásicas como **Reentrancy Attack** y sus mitigaciones.  
✅ Relacionarás conceptos clave: **inmutabilidad, firma digital, algoritmos hash, consenso, anonimicidad**.  

Cada laboratorio incluye:

- Un **README.md** con contexto teórico y pasos prácticos.
- Archivos necesarios (`.sol`, `.py` u otros).
- Indicaciones para **documentar resultados** y relacionar teoría ↔ práctica.

---

## 🧪 Lista de Laboratorios

1️⃣ **Laboratorio 1** → Cifrado simétrico y asimétrico (Python + HTML interactivo)  
2️⃣ **Laboratorio 2** → Exploración de transacciones y PoC en Remix IDE  
3️⃣ **Laboratorio 3** → Análisis de vulnerabilidad **Reentrancy** y mitigaciones  

---

## 🛠️ Prerrequisitos Generales

Para ejecutar los laboratorios necesitarás:

- **Conocimientos básicos de Python** y Smart Contracts en Solidity.
- Acceso a internet para usar **Remix IDE** y exploradores de bloques como **Etherscan**.
- Opcionalmente, MetaMask configurado con **Sepolia Testnet** y ETH de prueba.

---

## 🖥️ Opciones de Entorno

Puedes elegir cualquiera de las siguientes opciones según tu preferencia:

---

### ✅ 1. Máquina con Ubuntu Linux + Python 3.8+

**Prerrequisitos:**
```bash
sudo apt update
sudo apt install -y python3 python3-pip openssl git
```

**Ventajas:**
- Entorno nativo para scripts de cifrado.
- Compatible con OpenSSL y herramientas CLI.
- Ideal para integrar con Docker o Hardhat en un futuro.

---

### ✅ 2. WSL (Windows Subsystem for Linux) + Python

Si usas **Windows**, puedes habilitar **WSL** para tener un entorno Ubuntu:

1. Habilita WSL:
   ```powershell
   wsl --install -d Ubuntu
   ```
2. Instala Python dentro de WSL:
   ```bash
   sudo apt update
   sudo apt install python3 python3-pip openssl git -y
   ```

**Ventajas:**
- Ambiente Linux en Windows.
- Soporte para todas las herramientas nativas.

---

### ✅ 3. Python nativo en Windows

Si prefieres **Windows puro**, solo instala Python desde la página oficial:

1. Descarga e instala **Python 3.10+**:  
   👉 [https://www.python.org/downloads/](https://www.python.org/downloads/)

2. Verifica instalación:
   ```powershell
   python --version
   pip --version
   ```

**Ventajas:**
- Rápido de configurar.
- Permite ejecutar scripts `.py` y usar herramientas gráficas como Remix + MetaMask.

---

### ✅ 4. Docker con Ubuntu Linux + Python

Si quieres un entorno **aislado y reproducible**, usa **Docker**:

```bash
docker run -it --name blockchain-labs ubuntu:22.04 bash

# Dentro del contenedor:
apt update && apt install -y python3 python3-pip openssl git
```

Puedes montar tus carpetas locales:
```bash
docker run -it -v $(pwd):/labs ubuntu:22.04 bash
```

**Ventajas:**
- Entorno limpio sin afectar tu máquina.
- Ideal para replicar la misma configuración en varias computadoras.

---

## 🚀 Cómo empezar

1️⃣ Elige tu entorno preferido (Linux, WSL, Windows o Docker).  
2️⃣ Clona este repositorio o descarga los laboratorios:  
```bash
git clone https://github.com/karlozkordova/blockchain-security-labs.git
cd blockchain-security-labs
```
3️⃣ Sigue el **README.md** de cada laboratorio.  
4️⃣ Documenta tus resultados con las plantillas incluidas.  

---

## 🔗 Herramientas externas recomendadas

- **Remix IDE:** [https://remix.ethereum.org](https://remix.ethereum.org)  
- **Etherscan Sepolia:** [https://sepolia.etherscan.io](https://sepolia.etherscan.io)  
- **MetaMask:** [https://metamask.io](https://metamask.io)  

---

## 📊 Documentación de Resultados

Por cada laboratorio existe una sección del entregable, acontinuación los apartados que deben contener la  **plantilla de reporte** para documentar:

## Portada
- **Estudiante:**  
- **Laboratorio:** (Nombre y número)  
- **Fecha de entrega:**  
## 1. Introducción
Breve descripción del laboratorio y los objetivos específicos que se persiguen.
## 2. Procedimiento realizado
- Herramientas y entornos utilizados (ej. Python, Remix, Sepolia, exploradores de bloques).  
- Pasos seguidos durante el desarrollo del laboratorio.  
- Configuraciones relevantes.  
## 3. Evidencias
Incluir capturas de pantalla numeradas y explicadas, fragmentos de código relevante y resultados obtenidos.
## 4. Análisis y resultados
- Interpretación técnica de los resultados obtenidos.  
- Explicación de cómo se cumplen los objetivos del laboratorio.  
- Comparación de comportamientos observados (ej. algoritmos, transacciones, ataques).  
## 5. Reflexión sobre seguridad
- ¿Qué aporta este laboratorio a la comprensión de la seguridad en blockchain?  
- Identificación de riesgos, buenas prácticas o mecanismos de mitigación.  
- Conexión con casos reales o aplicaciones prácticas.  
## 6. Conclusiones
Síntesis de aprendizajes clave y valoración personal del ejercicio.
## 7. Bibliografía / Referencias
- Artículos o libros consultados.  
- Enlaces relevantes (ej. exploradores de bloques, repositorio base).  
✅ **Formato de entrega**:  
- Documento en **PDF** con la estructura anterior.  
---

## 🔒 Conclusión

Con estos laboratorios pondrás en práctica la seguridad en blockchain **desde la criptografía base hasta la auditoría de contratos inteligentes**, entendiendo los riesgos y las mejores prácticas.

¡Ahora sí, **elige tu entorno y empieza a hackear la blockchain (de forma ética)!** 🚀

---
