## ✅ Parte 2: PoC de transacciones en Remix IDE (Testnet)

Ahora vamos a **crear y ejecutar una transacción propia**, desplegando un contrato simple en una **testnet (Sepolia)** y observando la transacción resultante.

---

### 🔹 1. Preparación

### Paso 1.1 — Abrir Remix IDE

1. Ve a **[https://remix.ethereum.org](https://remix.ethereum.org)** desde tu navegador.
2. En el panel izquierdo, verán el explorador de archivos con algunos contratos de ejemplo. Puedes ignorarlos por ahora.
3. Crea una nueva carpeta llamada **`Lab2`** y dentro crea el archivo **`SimpleStorage.sol`**.

> 💡 **¿Por qué Remix?** Es un IDE en línea sin instalación. Incluye compilador de Solidity, debugger y conexión directa a MetaMask. Ideal para aprender sin configurar un entorno local.

---

### Paso 1.2 — Instalar y configurar MetaMask

1. Descarga MetaMask desde **[https://metamask.io](https://metamask.io)** como extensión de Chrome o Firefox.
2. Sigue el asistente para crear una nueva billetera.
3. **IMPORTANTE:** Guarda tu frase semilla (seed phrase) en un lugar seguro. Nunca la compartas.  Clic en ≡ (tres líneas) — esquina superior derecha de MetaMask → Configuración -> Seguridad y Contraseña -> Gestionar la recuperación de la contraseña -> Revlar. Siga los pasos indicados.
4. Una vez instalado, haz clic en el icono de MetaMask → Clic en ≡ (tres líneas) — esquina superior derecha de MetaMask → Redes → **"Mostrar redes de prueba"** → activa la opción.


> 🔐 **Concepto de seguridad:** La frase semilla es la raíz criptográfica de tu identidad en blockchain. Quien la posea controla todos tus fondos. En producción, se guarda en hardware wallets o gestores de claves seguros.

---

### Paso 1.3 — Obtener ETH de prueba (Faucet)

Para pagar el gas de las transacciones necesitas ETH de prueba (sin valor real).

1. Ve a **[https://sepolia-faucet.pk910.de/#/](https://sepolia-faucet.pk910.de/#/)** o **[https://sepoliafaucet.com](https://sepoliafaucet.com)** o **[https://faucet.sepolia.dev](https://faucet.sepolia.dev)**
2. Copia tu dirección pública de MetaMask (0x...). En MetaMask haz clic en "Account 1" → se abre la pantalla "Direcciones" → copia la dirección de Ethereum (0x...) usando el ícono 📋 de la derecha.
3. Pégala en el faucet y solicita ETH de prueba.
4. Espera 1–2 minutos y verifica el saldo en MetaMask.

> 💡 **Tip:** Si un faucet no funciona, prueba con **[https://www.alchemy.com/faucets/ethereum-sepolia](https://www.alchemy.com/faucets/ethereum-sepolia)**. Requiere cuenta gratuita en Alchemy.

> 💡 Sepolia usa la misma dirección que Ethereum mainnet. No uses las direcciones de Bitcoin, Solana u otras redes que aparecen en esa pantalla.

> 💡 Si un faucet no funciona, prueba con https://www.alchemy.com/faucets/ethereum-sepolia. Requiere cuenta gratuita en Alchemy. 
---
### 🔹 2. Contrato inteligente simple

En Remix, dentro de `Lab2/SimpleStorage.sol`, escribe el siguiente código:
 
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

### Paso 3.1 — Compilar el contrato

1. En Remix, haz clic en el ícono de **Solidity Compiler** (panel izquierdo, ícono con el logo de Solidity).
2. Asegúrate de que el archivo `SimpleStorage.sol` esté abierto.
4. Clic en **"Compile"**.
5. Si la compilación es exitosa, en el editor aparece el estimado de gas junto a la función: 22514 gas (como se ve en la línea 8).
6. Si no hay errores, aparecerá un check verde ✅.

> ⚠️ **Error común:** Si ves un error de versión, verifica que la versión del compilador coincida con `pragma solidity ^0.8.0`.

---
### Paso 3.2 — Configurar el entorno de despliegue

1. Haz clic en el ícono de **Deploy & Run Transactions** (ícono de Ethereum).
2. En Environment haz clic en el desplegable — verás: Remix VM, VM Fork, Dev, Base, WalletConnect, Custom.
3. Selecciona "WalletConnect" — esta es la opción para conectar MetaMask en la versión 2.1.0 de Remix.
4. MetaMask abrirá un popup → selecciona tu cuenta → clic en **Conectar**.
5. Verifica que en Remix aparezca tu dirección de MetaMask y el saldo en Sepolia.
6. En **Contract** confirma que dice `SimpleStorage`.

---
### Paso 3.3 — Desplegar el contrato

1. Verifica que en Deploy diga **"Sepolia (11155111) network"**.
2. Haz clic en el botón azul **"Deploy"**
3. MetaMask abrirá un popup mostrando **"Implementar un contrato"**:
   - **Red:** Spolia.
   - **Tarifa de red:**  en SepoliaETH (sin valor real)
4. Haz clic en **"Confirmar"**.
5. Espera ~15–30 segundos. En la consola aparecerá el bloque, hash y dirección del contrato.
6. En **"Deployed Contracts"** aparecerá SimpleStorage con su dirección y la red Sepolia.

> 🔐 **¿Qué ocurrió en seguridad?**
> - **Firma digital:** MetaMask usó tu clave privada para firmar el bytecode del contrato. Sin tu firma, nadie más puede desplegar en tu nombre.
> - **Gas:** La red cobró una comisión para prevenir spam (vector de ataque DoS en blockchain).
> - **Consenso PoS:** Los validadores de Sepolia verificaron y añadieron el bloque con tu contrato. Sin consenso, no hay despliegue.



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


