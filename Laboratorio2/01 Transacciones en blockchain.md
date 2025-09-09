
## ✅ Parte 1: Explorando una transacción en una red blockchain

En esta sección **veremos una transacción real**, observaremos sus datos en un explorador de bloques y conectaremos con los conceptos de seguridad.

---

### 🛠️ 1. Pasos prácticos

1. Existen algunos exploradores de bloques como:
   - **Ethereum Mainnet:** [https://etherscan.io](https://etherscan.io)
   - **Bitcoin:** [https://mempool.space](https://mempool.space)
   - **Ethereum Testnet Sepolia:** [https://sepolia.etherscan.io](https://sepolia.etherscan.io)

   Para esta prueba usaremos la red de **Ethereum Testnet Sepolia:**

2. Puedes buscar por dirección, un hash de transacción (**TxHash**), un bloque o un token a manera de ejemplo en la barra de búsqueda, coloca:

   ```
   0xb394a2ad1608a886b02f44b0285eed0a7bdf9a277aa660ae9a43ba474558a8b8
   ```

3. Observa la información mostrada:
   - **Transaction Hash** → identificador único
   - **From / To** → dirección origen y destino
   - **Block** → número de bloque donde se incluyó
   - **Timestamp** → cuándo se minó
   - **Gas Used / Gas Price** → costo de ejecución
   - **Nonce** → número de transacciones previas del emisor
   - **Input Data** → datos enviados (en caso de contratos)

---

### 🔍 2. Relación con conceptos de seguridad

| Campo observado en la práctica | Concepto de seguridad asociado |
|--------------------------------|--------------------------------|
| **TxHash** (identificador único) | Uso de **algoritmos criptográficos hash (SHA-256/Keccak)** para garantizar integridad e inmutabilidad |
| **Direcciones From / To** | **Anonimicidad/Pseudonimato**: no se conoce identidad real, solo direcciones públicas |
| **Gas y Fee** | Relacionado con el **mecanismo económico de protección contra spam y ataques DoS** |
| **Bloque y Confirmaciones** | **Inmutabilidad**: cada bloque enlazado al anterior con un hash, garantizando que no se puede alterar sin rehacer toda la cadena |
| **Nonce** | Protección contra **reenvío de transacciones (replay attacks)** |
| **Firma digital implícita** | Uso de **criptografía asimétrica (Elliptic Curve / ECDSA)** para autenticar remitente |
| **Estado “Success” o “Failed”** | Validación mediante **algoritmo de consenso (PoW, PoS)** para determinar inclusión en el ledger |

---

### 🔐 3. Seguridad en acción

- **Criptografía asimétrica:** cada transacción es firmada con la clave privada del emisor.
- **Hashing:** asegura que cualquier modificación cambia el TxHash.
- **Inmutabilidad:** una vez incluida en un bloque y asegurada por consenso, no puede revertirse.
- **Anonimicidad relativa:** solo ves direcciones públicas, no datos personales.
- **Gas como protección:** evita que un atacante sature la red con transacciones sin costo.

---

### 🔐 4. Replica el ejercicio


- Ahora realizar el mismo procedimiento en una red publica de transacciones busca y elige cualquiera de ellas y observa los conceptos revisados en los puntos anteriores.

---


### 📝 Resultados esperados

Al terminar la exploración se deberá:

✅ **Registrar capturas del explorador de bloques**  
✅ Explicación por cada red, los campos y su relación con la teoría  
✅ Reflexión sobre **qué asegura la inmutabilidad y autenticidad** de la transacción en ambas redes.
✅ Reflexión sobre **se pudieron evidenciar los crietrios de seguridad implícitos, ¿Cuáles?** de la transacción en ambas redes.


---

