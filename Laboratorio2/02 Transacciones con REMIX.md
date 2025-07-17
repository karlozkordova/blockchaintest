## ✅ Parte 2: PoC de transacciones en Remix IDE (Testnet)

Ahora vamos a **crear y ejecutar una transacción propia**, desplegando un contrato simple en una **testnet (Sepolia)** y observando la transacción resultante.

---

### 🛠️ 1. Preparación

1. Abre [https://remix.ethereum.org](https://remix.ethereum.org)
2. Instala MetaMask en tu navegador.
3. Configura **Sepolia Testnet** en MetaMask.
4. Consigue ETH de prueba desde un faucet:  
   [https://sepoliafaucet.com/](https://sepoliafaucet.com/)

---

### 🔹 2. Contrato inteligente simple

En Remix crea un archivo **SimpleStorage.sol**:

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract SimpleStorage {
    uint public storedData;

    function set(uint x) public {
        storedData = x;
    }
}
```

---

### 🔹 3. Compilar y desplegar

- Ve a **Solidity Compiler** y compila con versión 0.8.x
- Ve a **Deploy & Run Transactions**
  - Environment → `Injected Web3` (MetaMask)
  - Selecciona `SimpleStorage`
  - Clic en **Deploy**
- MetaMask solicitará firmar la transacción → confirma.

📌 **Conceptos de seguridad aquí:**
- **Firma digital**: MetaMask usa tu clave privada para autorizar el despliegue.
- **Gas**: Necesario para escribir datos en blockchain.
- **Consenso PoS (Sepolia)**: valida y añade el bloque con tu contrato.

---

### 🔹 4. Ejecutar una transacción al contrato

1. En Remix, en el contrato desplegado, busca la función `set`.
2. Introduce un valor (ejemplo `42`).
3. Clic en **Transact**.
4. MetaMask pedirá firmar → confirma.
5. Abre MetaMask → historial → clic en la transacción → **ver en Sepolia Etherscan**.

📌 **Conceptos de seguridad:**
- **Dirección origen (From)** es tu cuenta → autenticada por firma digital.
- **Dirección destino (To)** es el contrato inteligente.
- **Gas usado** muestra costo computacional.
- **Input Data** es el valor enviado (`42`) codificado en hex.
- **Inmutabilidad**: una vez escrito, no se puede revertir sin un hard fork.

---

### 🔐 Qué estás aplicando en seguridad blockchain

- **Criptografía asimétrica:** para firmar y autenticar.
- **Hashing:** garantiza integridad de bloques y transacciones.
- **Inmutabilidad:** la transacción queda grabada permanentemente.
- **Anonimicidad:** no se expone tu identidad, solo dirección pública.
- **Algoritmo de consenso:** asegura que la transacción es válida y única.

---

## 📝 Template para documentar resultados


Cuando se finalice, documentar:

1. **Hash de transacción generada en Remix** y link de enlace a Sepolia Etherscan
2. Reflexión:
   - ¿Qué asegura la **autenticidad** de la transacción?
   - ¿Qué garantiza su **inmutabilidad**?
   - ¿Qué rol juegan **gas y consenso**?
   - ¿Cómo se mantiene el **pseudonimato**?
3. Conclusión sobre cómo la **teoría se ve reflejada en la práctica**.


