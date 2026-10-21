# ⛓️ Laboratorio 4: Blockchain Ethereum local con Hardhat 3, Docker, Merkle Patricia y Control de Acceso en Smart Contracts

Este laboratorio levanta una **blockchain Ethereum completa en tu propio equipo** (Hardhat 3 dentro de Docker), con un **explorador web** propio para observar bloques, transacciones, el **árbol Merkle Patricia** y dos **Smart Contracts** que se comparan entre sí:

✅ **`RegistroAcademico`** → contrato **seguro**: solo el propietario puede modificar el mensaje.  
✅ **`RegistroAcademicoVulnerable`** → contrato **intencionalmente vulnerable**: cualquier cuenta puede modificarlo (ausencia de control de acceso).

> ⚠️ **Solo para la red local Hardhat (Chain ID 31337) y ETH ficticio.** No usar en redes públicas ni con claves que tengan fondos reales.

---

## 🎯 Objetivos

- Construir y operar una **red Ethereum local** reproducible con Docker y Hardhat 3.
- Consultar la cadena mediante **JSON-RPC** (cuentas, saldos, bloques, recibos).
- Generar varias transacciones en **un mismo bloque** y verificar su `transactionsRoot` reconstruyendo el **trie Merkle Patricia** y una **prueba de inclusión**.
- Desplegar dos Smart Contracts y **demostrar la diferencia entre tener y no tener control de acceso** (`msg.sender == propietario`).
- Interpretar **recibos, eventos, reverts y estados** antes y después de cada transacción.

---

## 📝 Contexto Teórico

### Árbol Merkle Patricia (MPT)

Cada bloque de Ethereum guarda en su cabecera tres raíces criptográficas:

1. **`transactionsRoot`** → raíz del trie de las transacciones del bloque.
2. **`receiptsRoot`** → raíz del trie de los recibos (resultado de ejecución, gas, logs).
3. **`stateRoot`** → raíz del estado global (saldos, nonces, código y almacenamiento de contratos).

Si se modifica **una sola transacción**, cambia su hash y, por tanto, la raíz. Una **prueba de inclusión** permite demostrar que una transacción pertenece al bloque usando solo los nodos del camino hasta la raíz.

### Control de acceso en Smart Contracts

El contrato seguro valida quién llama a la función:

```solidity
require(msg.sender == propietario, "No autorizado");
```

El contrato vulnerable **omite** esta línea. La blockchain funciona correctamente en ambos casos: **la vulnerabilidad está en la lógica del contrato, no en Ethereum**.

### Conceptos de seguridad involucrados

- **Inmutabilidad:** una vez desplegado, el contrato vulnerable no puede corregirse; hay que desplegar uno nuevo.
- **Firma y autoría:** cada transacción registra la cuenta que la originó (`from`) y el evento registra `usuario`.
- **Revert:** si una condición `require` falla, la EVM deshace todos los cambios; el recibo queda con `status = 0`.
- **Integridad:** las raíces Merkle permiten detectar cualquier alteración de los datos de un bloque.

---

## 📂 Estructura del Laboratorio

Al clonar el repositorio, la carpeta `Laboratorio4` contiene:

```text
Laboratorio4\
│   README.md
│   .gitignore
│   Dockerfile
│   hardhat.config.ts
│   compose.yaml
│   compose.explorer.yaml
│   blockchain.ps1
│   Generar_Transacciones_Hardhat.ps1
│
├── contracts\
│   ├── RegistroAcademico.sol
│   └── RegistroAcademicoVulnerable.sol
│
├── scripts\
│   ├── rpc.mjs
│   ├── accounts.mjs
│   ├── blocks.mjs
│   ├── deploy.mjs
│   ├── ver-contrato.mjs
│   ├── interact.mjs
│   ├── deploy-vulnerable.mjs
│   └── probar-vulnerable.mjs
│
└── explorer\
    ├── Dockerfile
    ├── package.json
    ├── server.mjs
    ├── merkle.mjs
    └── public\
        ├── index.html
        ├── app.js
        ├── contract.js
        ├── wallet.js
        ├── glossary.js
        └── style.css
```

- **`Dockerfile`, `hardhat.config.ts`, `compose.yaml`**  
  Construyen y levantan el nodo Hardhat 3 (contenedor `hardhat-blockchain`, puerto `8545`).

- **`compose.explorer.yaml` y carpeta `explorer\`**  
  Explorador web (contenedor `blockchain-explorer`, puerto `3000`).  
  - Muestra bloques, cuentas, búsqueda de transacciones y el **árbol Merkle Patricia**.  
  - Incluye el selector de contrato **seguro / vulnerable**, la **Wallet de laboratorio** y un **glosario** al final de la página.

- **`blockchain.ps1`**  
  Define la función PowerShell `RPC` para consultar el nodo desde la terminal.

- **`Generar_Transacciones_Hardhat.ps1`**  
  Envía **cuatro transferencias** de ETH ficticio desde cuentas distintas y las mina en **un solo bloque**.

- **`contracts\`**  
  Código Solidity de los dos contratos a comparar.

- **`scripts\`**  
  Scripts Node.js que se ejecutan **dentro del contenedor** para consultar, desplegar y probar los contratos.

> 📌 Los archivos `scripts\deployment.json` y `scripts\deployment-vulnerable.json` **no vienen en el repositorio**: se generan en el paso 8 y dependen de la cadena en memoria de cada ejecución. Están excluidos en `.gitignore`; no deben subirse ni copiarse de otra persona.

---

## ✅ Prerrequisitos

1. **Windows 10/11** con virtualización habilitada y **WSL 2**.
2. **Docker Desktop para Windows** con motor **WSL 2 / Linux containers**:  
   👉 [https://docs.docker.com/desktop/setup/install/windows-install/](https://docs.docker.com/desktop/setup/install/windows-install/)
3. **Git para Windows** (opcional, para clonar): 👉 [https://git-scm.com/download/win](https://git-scm.com/download/win)
4. **PowerShell** (incluido en Windows) y un navegador web.

**No es necesario instalar Node.js en Windows**: todos los `.mjs` se ejecutan dentro de Docker.

> 📌 **Regla de operación:** Hardhat mantiene la cadena **en memoria**. Al reiniciar su contenedor se pierden bloques, saldos modificados, eventos y contratos; los archivos en Windows sí persisten. Si eso ocurre, repetir los pasos 6 a 9.

---

## 🛠️ Pasos del Laboratorio

### 1. Instalar y validar Docker

Si WSL aún no está disponible, abrir PowerShell **como administrador**:

```powershell
wsl --install
```

Reiniciar Windows cuando se solicite, instalar Docker Desktop, abrirlo y esperar a que indique que el motor está en ejecución.

**Validación (PowerShell):**

```powershell
docker --version
docker compose version
docker info
docker run --rm hello-world
```

✔️ **Esperado:** se imprimen versiones, `docker info` muestra datos del servidor y `hello-world` termina correctamente.  
❌ **Si falla:** iniciar Docker Desktop, confirmar que usa contenedores Linux y revisar `wsl --status` / `wsl --update`.

---

### 2. Obtener el laboratorio desde GitHub

El laboratorio está en la carpeta **`Laboratorio4`** del repositorio del curso:  
👉 [https://github.com/karlozkordova/blockchaintest/tree/main/Laboratorio4](https://github.com/karlozkordova/blockchaintest/tree/main/Laboratorio4)

No es necesario crear carpetas ni copiar archivos uno a uno; basta con conservar la estructura del repositorio.

#### Opción A — Clonar con Git (recomendada)

```powershell
git --version

# Carpeta contenedora (ejemplo)
$Base = Join-Path $HOME 'Documents\Docker'
New-Item -ItemType Directory -Path $Base -Force | Out-Null
Set-Location $Base

# Clonar el repositorio del curso y entrar al laboratorio 4
git clone https://github.com/karlozkordova/blockchaintest.git
Set-Location .\blockchaintest\Laboratorio4
```

Si ya clonaste el repositorio para laboratorios anteriores, solo actualízalo:

```powershell
Set-Location (Join-Path $HOME 'Documents\Docker\blockchaintest')
git pull
Set-Location .\Laboratorio4
```

#### Opción B — Descargar ZIP

En [https://github.com/karlozkordova/blockchaintest](https://github.com/karlozkordova/blockchaintest) usar **Code → Download ZIP**. GitHub descarga **todo el repositorio** (carpeta `blockchaintest-main`); el laboratorio está en `blockchaintest-main\Laboratorio4`. Extraerlo, por ejemplo, en `Documents\Docker` y desbloquear los scripts descargados:

```powershell
Set-Location (Join-Path $HOME 'Documents\Docker\blockchaintest-main\Laboratorio4')
Get-ChildItem -Recurse -Filter *.ps1 | Unblock-File
```

> 📌 En el resto de la guía, `$Proyecto` es la carpeta `Laboratorio4`. Ajustarla si se usó otra ubicación o la Opción B:
>
> ```powershell
> $Proyecto = Join-Path $HOME 'Documents\Docker\blockchaintest\Laboratorio4'
> Set-Location $Proyecto
> ```

#### Permitir scripts PowerShell en la terminal actual

En Windows 10/11 la política predeterminada (`Restricted`) bloquea **cualquier** `.ps1`. Permitir scripts **solo en esta ventana** (no cambia la configuración del equipo y se pierde al cerrarla):

```powershell
Get-ExecutionPolicy
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force
```

Repetirlo cada vez que se abra una nueva terminal para el laboratorio.

#### Validar la estructura

```powershell
Set-Location $Proyecto

$Archivos = @(
  'Dockerfile', 'hardhat.config.ts', 'compose.yaml', 'compose.explorer.yaml',
  'blockchain.ps1', 'Generar_Transacciones_Hardhat.ps1',
  'contracts/RegistroAcademico.sol',
  'contracts/RegistroAcademicoVulnerable.sol',
  'scripts/deploy.mjs', 'scripts/deploy-vulnerable.mjs',
  'scripts/probar-vulnerable.mjs', 'explorer/server.mjs',
  'explorer/public/index.html', 'explorer/public/wallet.js',
  'explorer/public/glossary.js'
)
$Archivos | ForEach-Object { "$_ : $(Test-Path $_)" }

docker compose -f compose.yaml -f compose.explorer.yaml config --services
```

✔️ **Esperado:** los 15 archivos aparecen como `True` y Compose reconoce los servicios `blockchain` y `explorer`.

---

### 3. Construir las imágenes

Se usan **dos** archivos Compose:

- **`compose.yaml`** → servicio `blockchain` (Hardhat), publicado en `127.0.0.1:8545`; monta `.\scripts` y `.\contracts` en `/app`.
- **`compose.explorer.yaml`** → servicio `explorer`, publicado en `127.0.0.1:3000` (puerto interno `8080`); monta `.\scripts` y `.\contracts` en `/data` **en solo lectura** (`:ro`).

```powershell
docker compose -f compose.yaml -f compose.explorer.yaml config
docker compose -f compose.yaml -f compose.explorer.yaml build
docker image ls
```

✔️ **Esperado:** `build` finaliza sin errores.  
❌ **Si hay fallo ESM:** verificar que el `Dockerfile` ejecuta `npm pkg set type=module`. Si faltan `ethers` o `solc`, reconstruir el nodo; el `Dockerfile` instala `hardhat@^3 ethers@^6 solc@^0.8.28` sobre `node:24-bookworm-slim`.

> 📌 Los puertos se publican solo en `127.0.0.1`. Los puertos Windows `8080/8085` pueden estar reservados en algunos equipos; por eso el explorador se publica en `3000`.

---

### 4. Iniciar los servicios y validar la red

```powershell
docker compose -f compose.yaml -f compose.explorer.yaml up -d --no-build
docker compose -f compose.yaml -f compose.explorer.yaml ps
docker logs --tail 40 hardhat-blockchain
docker logs --tail 40 blockchain-explorer
```

**Validación del nodo JSON-RPC:**

```powershell
$body = @{ jsonrpc='2.0'; method='eth_chainId'; params=@(); id=1 } | ConvertTo-Json
Invoke-RestMethod -Uri 'http://127.0.0.1:8545' -Method Post -ContentType 'application/json' -Body $body
docker exec hardhat-blockchain node scripts/rpc.mjs eth_blockNumber
```

✔️ **Esperado:** `result = 0x7a69` (31337) y, en una cadena recién iniciada, bloque `"0x0"`.

**Validación del explorador:**

```powershell
Invoke-WebRequest 'http://127.0.0.1:3000/'
docker exec blockchain-explorer ls -l /data/scripts
docker exec blockchain-explorer ls -l /data/contracts
```

✔️ **Esperado:** HTTP 200 y carpetas legibles; en `/data/scripts` todavía **no** hay `deployment*.json`.  
📌 En este momento `/api/contract` (y la sección *Smart Contracts* de la web) muestra `ENOENT: no such file or directory, open '/data/scripts/deployment.json'`, porque aún no se ha desplegado ningún contrato. **No es un fallo de la instalación.**

---

### 5. Cargar la función `RPC` (`blockchain.ps1`)

Este archivo **define la función `RPC`**; no crea otra blockchain ni despliega contratos. Cargarlo con **punto y espacio** para que la función quede disponible en la terminal actual:

```powershell
Set-Location $Proyecto
. .\blockchain.ps1
Get-Command RPC
RPC 'eth_chainId'
RPC 'eth_accounts'
RPC 'eth_blockNumber'
RPC 'eth_getBlockByNumber' @('0x0', $false)
```

✔️ **Esperado:** `eth_chainId` devuelve `0x7a69`, `eth_accounts` lista 20 cuentas de prueba y se obtiene el bloque génesis.  
📌 `./blockchain.ps1` (ejecución aislada) **no** es lo mismo que `. .\blockchain.ps1` (carga persistente). En una terminal nueva hay que volver a cargarlo.

**Alternativa sin la función RPC:**

```powershell
docker exec hardhat-blockchain node scripts/accounts.mjs
docker exec hardhat-blockchain node scripts/blocks.mjs
```

---

### 6. Generar cuatro transacciones en un mismo bloque

```powershell
Set-Location $Proyecto
.\Generar_Transacciones_Hardhat.ps1
```

Si no se aplicó el permiso de scripts del paso 2, usar solo para esta ejecución:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\Generar_Transacciones_Hardhat.ps1
```

El script comprueba el Chain ID y que existan al menos ocho cuentas, **desactiva temporalmente el automine**, envía cuatro transferencias, mina **un solo bloque** y restaura el automine aunque ocurra un error.

| Envío | Remitente | Destinatario | ETH de prueba |
|---|---|---|---:|
| 1 | Cuenta 0 | Cuenta 4 | 1 |
| 2 | Cuenta 1 | Cuenta 5 | 2 |
| 3 | Cuenta 2 | Cuenta 6 | 0,5 |
| 4 | Cuenta 3 | Cuenta 7 | 0,1 |

✔️ **Esperado:** el script informa el **número de bloque**, `Transacciones: 4`, los cuatro hashes, las raíces `transactionsRoot`, `receiptsRoot`, `stateRoot`, cada recibo con `status: 0x1` y al final `Automine restaurado: true.`

```powershell
RPC 'eth_blockNumber'
RPC 'eth_getBlockByNumber' @('latest', $true)
```

📌 Usar el número de bloque que informa el script; no asumir que siempre es el bloque `1`.

---

### 7. Explorar en el navegador y verificar el árbol Merkle

Abrir 👉 **http://localhost:3000** y revisar en orden:

1. Estado **Nodo conectado** y Chain ID `31337`.
2. **Cuentas y saldos** (las cuentas 0–3 enviaron ETH; las 4–7 lo recibieron).
3. **Bloques recientes**: el bloque con 4 transacciones.
4. **Buscar transacción**: pegar uno de los hashes del paso 6.
5. **Árbol Merkle Patricia**: analizar el bloque del paso 6.
6. **Glosario Blockchain** al final de la página.

**Validación del servicio:**

```powershell
Invoke-WebRequest 'http://localhost:3000/'
Invoke-WebRequest 'http://localhost:3000/glossary.js'
```

**Validación del trie de transacciones** (sustituir `N` por el número de bloque del paso 6):

```powershell
Invoke-RestMethod 'http://localhost:3000/api/merkle?block=N' | ConvertTo-Json -Depth 12
```

✔️ **Esperado:** `matches = true`, `expectedRoot` igual a `calculatedRoot` y pruebas de inclusión con `verified = true`. En la web: **"Raíz verificada: coincide con Hardhat"**. `receiptsRoot` y `stateRoot` se muestran desde la cabecera; el explorador **no** los reconstruye.

> 🔎 **Caso especial — bloque 0 (génesis):** da `matches = false`. Hardhat registra en el génesis `transactionsRoot = 0xc5d2…a470` (`keccak256` de un contenido vacío), mientras que la raíz de un trie Merkle Patricia vacío es `0x56e8…b421`. Los bloques vacíos minados después del génesis sí coinciden. Es una particularidad de Hardhat, no un error del laboratorio: **analízalo en tu reporte**.

---

### 8. Desplegar los dos Smart Contracts

Se compila y despliega **dentro del contenedor `hardhat-blockchain`**, sin reiniciarlo. Desplegar **primero el seguro** y luego el **vulnerable**:

```powershell
# Contrato con control de acceso
docker exec hardhat-blockchain node scripts/deploy.mjs

# Verificar contrato seguro y bytecode
docker exec hardhat-blockchain node scripts/ver-contrato.mjs

# Contrato intencionalmente vulnerable
docker exec hardhat-blockchain node scripts/deploy-vulnerable.mjs

# Verificar que se crearon ambos registros
Get-Content .\scripts\deployment.json -Raw | ConvertFrom-Json | Select-Object contractName,address,chainId,blockNumber,txHash
Get-Content .\scripts\deployment-vulnerable.json -Raw | ConvertFrom-Json | Select-Object contractName,address,chainId,blockNumber,txHash
```

✔️ **Esperado:**

- `deploy.mjs` y `deploy-vulnerable.mjs` muestran `Red: 31337`, la cuenta 0 como desplegadora, `Contrato`, `Hash TX`, `Bloque` y `Despliegue completado.`
- `ver-contrato.mjs` muestra el propietario, `Mensaje: Test Blockchain UTPL`, `Contador: 0` y `Bytecode compilado coincide: true`.
- Ambos registros existen, red `31337`, **direcciones distintas** y hashes no vacíos.
- Ambos contratos tienen el **mismo propietario** (cuenta 0): la **única diferencia** entre ellos es el control de acceso.

📌 Las direcciones y bloques de otra ejecución **no** son valores esperados: registrar los que aparezcan en tu equipo.

**Validación desde el explorador:**

```powershell
Invoke-RestMethod 'http://localhost:3000/api/contract?contract=seguro' | ConvertTo-Json -Depth 8
Invoke-RestMethod 'http://localhost:3000/api/contract?contract=vulnerable' | ConvertTo-Json -Depth 8
Invoke-RestMethod 'http://localhost:3000/api/wallet?contract=seguro' | ConvertTo-Json -Depth 7
Invoke-RestMethod 'http://localhost:3000/api/wallet?contract=vulnerable' | ConvertTo-Json -Depth 7
```

✔️ **Esperado:** ambos contratos son seleccionables en **Smart Contracts** y en la **Wallet de laboratorio**, y cada dirección coincide con su propio `deployment*.json`.  
❌ **Si aparece** `ENOENT /data/scripts/deployment.json` después de desplegar, revisar los montajes del paso 3 y recrear solo el explorador:

```powershell
docker compose -f compose.yaml -f compose.explorer.yaml up -d --no-deps --force-recreate explorer
```

---

### 9. Probar el control de acceso

En **http://localhost:3000**, sección **Wallet de laboratorio**. Antes de enviar cada transacción, el navegador pide confirmación; aceptar para continuar. El resultado aparece debajo del formulario.

#### 9.1 Contrato seguro — cuenta propietaria

Seleccionar contrato **Seguro**, la cuenta marcada **`[Propietario]`**, escribir un mensaje y enviar.

✔️ **Esperado:** `CONFIRMADA en bloque N · TX: 0x… · Actualización por propietario. · Contador: 1 · Eventos: 1`.

#### 9.2 Contrato seguro — cuenta NO propietaria

Seleccionar otra cuenta (**`[Otra cuenta]`**) y enviar un mensaje distinto.

✔️ **Esperado:** `REVERTIDA en bloque N · TX: 0x… · Transacción revertida por la EVM (No autorizado); el estado no cambió.` con `Eventos: 0`. El mensaje y el contador **no** cambian. Hardhat mina la transacción fallida, por lo que existe hash y recibo con `status = 0`.  
📌 Si el revert se detectara antes de minar, la web indica "no se minó ninguna transacción". **Ambos resultados son válidos.**

#### 9.3 Contrato vulnerable — cuenta NO propietaria

Seleccionar **Vulnerable**, usar **la misma cuenta no propietaria** y enviar un tercer mensaje.

✔️ **Esperado:** `CONFIRMADA … · Una cuenta no propietaria actualizó el contrato: ausencia de control de acceso.`, contador incrementado y evento con `usuario` igual a la cuenta no propietaria.

#### 9.4 Prueba automatizada del contrato vulnerable

```powershell
docker exec hardhat-blockchain node scripts/probar-vulnerable.mjs
```

Usa la cuenta de índice 1 (no propietaria) e imprime `Propietario`, `Cuenta no propietaria`, `Antes`, `TX`, `Bloque`, `Despues`, `Contador` y el evento `MensajeActualizado`. **Modifica el estado.**

#### 9.5 Comprobación independiente del frontend

```powershell
docker exec hardhat-blockchain node scripts/ver-contrato.mjs
Invoke-RestMethod 'http://localhost:3000/api/contract?contract=seguro' | ConvertTo-Json -Depth 9
Invoke-RestMethod 'http://localhost:3000/api/contract?contract=vulnerable' | ConvertTo-Json -Depth 9
```

**Opcional:** `docker exec hardhat-blockchain node scripts/interact.mjs` escribe `TX desde Docker` en el contrato seguro con la cuenta 0 (propietaria) e imprime hash, bloque, gas, contador y evento.

Buscar en el explorador el hash de cada transacción, su bloque y su recibo (`status = 1` exitosa, `status = 0` revertida), y relacionar el bloque con su `transactionsRoot` en la sección Merkle.

---

## 🔍 Qué observar

| Caso | Cuenta | Seguro | Vulnerable | Evidencia |
|---|---|---|---|---|
| Leer `mensaje`, `contador` | Cualquiera | Permite | Permite | Valores on-chain |
| Escribir mensaje | Propietario | Permite | Permite | Nuevo mensaje, recibo y evento |
| Escribir mensaje | No propietaria | **Rechaza** | **Permite** | Comparación de estados y transacciones |
| Comprobar código | Cualquiera | ABI + fuente local | ABI + fuente local | Bytecode y archivos diferenciados |

- Las **cuatro transferencias** del paso 6 comparten bloque y, por tanto, `transactionsRoot`.
- La **raíz recalculada** coincide con la de Hardhat y la prueba de inclusión se verifica.
- Una transacción **revertida** consume gas, queda registrada con `status = 0` y **no** emite evento ni cambia el estado.
- En el contrato vulnerable, el evento registra como `usuario` a una cuenta que **no** es el propietario.

> 🔐 **Seguridad de la Wallet de laboratorio:** usa cuentas de prueba desbloqueadas vía JSON-RPC (`eth_sendTransaction`). **Seleccionar una dirección en la web no autentica a una persona.** No exponer esta aplicación ni el puerto 8545 a redes públicas ni importar claves con fondos reales.

---

## 🔒 Mitigación

Para evitar la ausencia de control de acceso:

1. Validar siempre quién llama a las funciones que modifican estado: `require(msg.sender == propietario, "No autorizado");`.
2. Usar patrones probados como `Ownable` o `AccessControl` de OpenZeppelin en lugar de controles improvisados.
3. Probar explícitamente el caso **no autorizado** (como en 9.2) antes de desplegar.
4. Auditar el contrato **antes** del despliegue: por la inmutabilidad, un error en producción obliga a desplegar un contrato nuevo y migrar.

---

## 🧯 Diagnóstico rápido

| Síntoma | Diagnóstico / solución |
|---|---|
| `docker` no disponible | Iniciar Docker Desktop; revisar WSL 2 y `docker info`. |
| `la ejecución de scripts está deshabilitada` | Aplicar `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force` (paso 2). |
| `Restarting` de Hardhat | `docker logs --tail 80 hardhat-blockchain`; verificar ESM/Node/dependencias. |
| `localhost:3000` inaccesible | `docker compose ... ps`, logs del explorer y puerto 3000 del equipo. |
| `502`, `ENOENT /data/scripts/deployment.json` | Contratos aún no desplegados (paso 8) o faltan los montajes `:ro`. |
| `deploy-vulnerable.mjs` no encontrado | Faltan archivos: volver a clonar o actualizar (`git pull`) y repetir la validación del paso 2. |
| Desaparecen contratos tras `stop`/`start`/`down` | Cadena en memoria reiniciada; repetir pasos 6–9. |
| `No autorizado` al escribir en el seguro | **Esperado** con una cuenta no propietaria. |
| `matches=false` en Merkle | En el bloque 0 es **esperado** (paso 7). En otros bloques: revisar logs del explorer y el tipo de transacción. |
| La web muestra datos viejos | `Ctrl+F5`; comprobar que el `deployment*.json` pertenece al nodo actual. |

### Detener y volver a iniciar

```powershell
# Detener servicios sin eliminar imágenes (se pierde el estado de Hardhat)
docker compose -f compose.yaml -f compose.explorer.yaml stop

# Reutilizar los contenedores existentes (cadena nueva)
docker compose -f compose.yaml -f compose.explorer.yaml start

# Reconstruir SOLO la interfaz si se modifica HTML, JS o backend del explorer
docker compose -f compose.yaml -f compose.explorer.yaml up -d --build --no-deps explorer
```

**No usar** `docker compose down -v` ni `docker system prune -a` como paso ordinario. Para empezar de cero: `docker compose -f compose.yaml -f compose.explorer.yaml down` y luego `up -d --no-build`; los archivos en Windows permanecen.

---

## ✅ Resultados esperados

- Tienes una red Ethereum local funcionando con su propio explorador.
- Verificas criptográficamente que un conjunto de transacciones pertenece a un bloque (raíz Merkle + prueba de inclusión).
- Demuestras con evidencias que el contrato seguro **rechaza** a una cuenta no propietaria y el vulnerable la **acepta**.
- Relacionas los **conceptos teóricos de seguridad con la práctica**.

---

## 📎 Relación con seguridad en blockchain

- **Integridad:** las raíces Merkle de la cabecera permiten detectar cualquier alteración de transacciones, recibos o estado.
- **Trazabilidad:** cada intento (exitoso o revertido) queda registrado con su cuenta de origen, bloque y recibo.
- **Inmutabilidad:** un contrato vulnerable desplegado no puede corregirse; solo reemplazarse.
- **Confianza en el código:** la red ejecuta exactamente lo programado; si falta un control de acceso, la blockchain lo ejecuta igual.

---

## 📊 Conclusión

Este laboratorio demuestra que **una blockchain íntegra y bien construida no garantiza por sí sola la seguridad de una aplicación**. Las raíces Merkle aseguran la integridad de los datos, pero la autorización depende de la **lógica del Smart Contract**: una sola línea omitida (`require`) permite que cualquier cuenta modifique el estado.

---

## 🔗 Referencias técnicas

- **Docker Desktop (Windows):** [https://docs.docker.com/desktop/setup/install/windows-install/](https://docs.docker.com/desktop/setup/install/windows-install/)
- **Docker Compose:** [https://docs.docker.com/compose/](https://docs.docker.com/compose/)
- **Hardhat:** [https://hardhat.org/docs/getting-started](https://hardhat.org/docs/getting-started)
- **Ethereum JSON-RPC:** [https://ethereum.org/en/developers/docs/apis/json-rpc/](https://ethereum.org/en/developers/docs/apis/json-rpc/)
- **Merkle Patricia Trie:** [https://ethereum.org/en/developers/docs/data-structures-and-encoding/patricia-merkle-trie/](https://ethereum.org/en/developers/docs/data-structures-and-encoding/patricia-merkle-trie/)

**Versiones verificadas (20/10/2026):** Hardhat 3.20.0, ethers 6.17.0, solc 0.8.37, @ethereumjs/trie 6.2.1. Los Dockerfiles usan rangos (`^`), por lo que una construcción posterior puede descargar versiones más nuevas. Los scripts compilan con `solc` (última 0.8.x), no con la versión `0.8.28` de `hardhat.config.ts`, que solo se usaría con `npx hardhat compile`.
