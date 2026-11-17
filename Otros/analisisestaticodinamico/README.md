# VulnerableBank PoC

Este proyecto demuestra una **Prueba de Concepto (PoC)** de análisis de seguridad para contratos inteligentes Solidity, enfocada en la detección de la vulnerabilidad **Reentrancy** usando herramientas open source.

## Descripción del Contrato

`VulnerableBank.sol` es un contrato simple que permite a los usuarios **depositar** y **retirar** fondos. Sin embargo, en la función `withdraw()` el balance se actualiza **después** de enviar los fondos, lo que permite ataques de reentrancy.

### Funciones principales
- `deposit()`: Permite enviar fondos al contrato.
- `withdraw(uint _amount)`: Retira la cantidad solicitada si el saldo es suficiente.

## Vulnerabilidad

La llamada externa `msg.sender.call{value: _amount}("")` ocurre antes de actualizar `balances[msg.sender]`. Un contrato receptor podría intentar llamar de nuevo a `withdraw()` mientras la primera retirada sigue en curso: se incumple el patrón **Checks-Effects-Interactions**.

**Matiz importante:** en Solidity 0.8.x, un subdesbordamiento aritmético provoca una reversión. Por ello, detectar este patrón no equivale automáticamente a demostrar el vaciado del contrato: el impacto concreto debe verificarse mediante pruebas reproducibles.

## Herramientas utilizadas

| Herramienta | Enfoque | Uso previsto |
| --- | --- | --- |
| **Slither** | Análisis estático | Detectar patrones inseguros y generar alertas revisables. |
| **Mythril** | Ejecución simbólica | Explorar rutas de ejecución y posibles condiciones de vulnerabilidad. |
| **Echidna** | Fuzzing basado en propiedades | Explorar transacciones y buscar contraejemplos de invariantes definidos en un contrato auxiliar. |

Las alertas y los resultados esperados **no son resultados obtenidos**. Cada ejecución debe registrarse con la versión de la herramienta, los comandos, su salida y las limitaciones encontradas.

## Precondiciones

Las instrucciones siguientes están orientadas a **WSL / Ubuntu / Debian con Python 3.12**, u otros sistemas similares con Python administrado por el sistema operativo.

Se requiere:

- Acceso a una terminal y permisos `sudo` para instalar paquetes del sistema.
- Python 3 y soporte para entornos virtuales (`venv`).
- Conexión a Internet para instalar dependencias y el compilador de Solidity.
- El archivo `VulnerableBank.sol` disponible en el directorio desde donde se ejecuten los análisis.

Comprobar la versión de Python:

```bash
python3 --version
```

Instalar las dependencias básicas del sistema:

```bash
sudo apt update
sudo apt install -y python3-full python3-venv python3-pip build-essential git
```

### ¿Por qué no usar `sudo pip install`?

En distribuciones actuales de Ubuntu/Debian puede aparecer el error `externally-managed-environment` (**PEP 668**) cuando se intenta instalar paquetes globalmente con `pip`. Para evitar alterar los paquetes del sistema, se utiliza un **entorno virtual**. No se recomienda usar `sudo pip` ni la opción `--break-system-packages`.

## Instalación: entorno virtual para Slither

### 1. Crear el directorio de trabajo

```bash
mkdir -p ~/auditoria_smart_contracts
cd ~/auditoria_smart_contracts
```

Copiar aquí el archivo `VulnerableBank.sol`, o ejecutar los comandos posteriores desde el directorio donde se encuentre.

### 2. Crear y activar el entorno virtual

```bash
python3 -m venv venv
source venv/bin/activate
```

Cuando el entorno esté activo, el prompt normalmente mostrará `(venv)`.

### 3. Actualizar las herramientas de instalación

```bash
python -m pip install --upgrade pip setuptools wheel
```

### 4. Instalar Slither y un gestor de versiones de Solidity

```bash
python -m pip install slither-analyzer solc-select
```

El archivo del ejemplo declara `pragma solidity ^0.8.0`. Para este laboratorio puede usarse el compilador **0.8.20**, compatible con esa declaración:

```bash
solc-select install 0.8.20
solc-select use 0.8.20
```

### 5. Verificar la instalación

```bash
python --version
slither --version
solc --version
```

### 6. Ejecutar el análisis estático

Situarse en el directorio que contiene `VulnerableBank.sol` (o indicar su ruta completa):

```bash
slither VulnerableBank.sol
```

Para limitar la revisión al detector de transferencia de ETH potencialmente reentrante:

```bash
slither VulnerableBank.sol --detect reentrancy-eth
```

Guardar los resultados de la ejecución, incluidos mensajes de error y versión de la herramienta. Una alerta debe corroborarse con revisión manual o pruebas.

### 7. Desactivar o volver a activar el entorno

Para salir:

```bash
deactivate
```

Para volver a utilizarlo posteriormente:

```bash
cd ~/auditoria_smart_contracts
source venv/bin/activate
```

## Instalación separada de Mythril

**No se recomienda instalar Slither, Mythril  en el mismo entorno virtual**: pueden necesitar versiones incompatibles de bibliotecas. Para Mythril, crear otro entorno:

```bash
cd ~/auditoria_smart_contracts
python3 -m venv venv_mythril
source venv_mythril/bin/activate
python -m pip install --upgrade pip wheel
python -m pip install "setuptools<81"
python -m pip install mythril
```

### Compatibilidad habitual: `pkg_resources` en Python 3.12

Al ejecutar `myth version`, algunas combinaciones de dependencias pueden fallar con:

```text
ModuleNotFoundError: No module named 'pkg_resources'
```

La causa inmediata es que una dependencia intenta importar `pkg_resources`, un módulo proporcionado por versiones anteriores de `setuptools`. Para **prevenir o corregir** este problema dentro del entorno virtual de Mythril (sin `sudo`), mantener `setuptools` por debajo de la versión 81:

```bash
python -m pip install "setuptools<81"
python -c "import pkg_resources; print('pkg_resources disponible')"
myth version
```

La importación puede mostrar una advertencia de obsolescencia; si se imprime el mensaje de confirmación, el módulo está disponible. Este ajuste resuelve únicamente la ausencia de `pkg_resources`: **no garantiza** que Mythril y todas sus dependencias funcionen con Python 3.12. Si surge otro error, conservar la traza completa y comprobar la compatibilidad de las versiones antes de continuar.

> **Nota sobre rutas:** si ya creaste `venv_mythril` en otro directorio (por ejemplo, en tu carpeta de trabajo bajo WSL), actívalo desde esa ubicación y ejecuta allí los comandos de corrección. No necesitas crear un segundo entorno solo por la diferencia de ruta.

### Instalar y seleccionar `solc` para Mythril (paso necesario en este laboratorio)

Con **`venv_mythril` activado**, instalar el gestor y la versión requerida del compilador:

```bash
python -m pip install solc-select
solc-select install 0.8.20
solc-select use 0.8.20
solc --version
```

### Verificar y ejecutar el análisis

Verificar primero que Mythril y el compilador sean accesibles:

```bash
myth version
command -v solc
solc --version
```

Situarse en el directorio que contiene `VulnerableBank.sol`. Como primera prueba, ejecutar sin forzar una descarga por versión:

```bash
myth analyze VulnerableBank.sol
```

Si Mythril requiere seleccionar explícitamente la versión, puede probarse:

```bash
myth analyze VulnerableBank.sol --solv 0.8.20
```

**Atención:** aunque `solc-select` haya instalado `solc` y este responda a `--version`, el parámetro `--solv` puede hacer que Mythril intente localizar o instalar la versión mediante `py-solc-x` y vuelva a acceder a la red. Registrar el error si ocurre; no dar por validado el análisis hasta obtener una salida real de Mythril.

> **Compatibilidad:** Mythril puede presentar conflictos de dependencias o compilador con ciertas combinaciones de Python y sistema operativo. Si aparece otro problema, registrar la traza y comprobar las versiones antes de modificar el entorno. No forzar la instalación global.

Para salir del entorno:

```bash
deactivate
```

## Demostración práctica con Echidna 2.4.0

Echidna complementa Slither (análisis estático) y Mythril (ejecución simbólica) mediante **fuzzing basado en propiedades**. En esta demostración se utiliza el **mismo contrato original** `VulnerableBank.sol`, sin cambiar su lógica, y un segundo contrato de pruebas llamado `VulnerableBankEchidna.sol`.

### 1. Precondiciones y organización de archivos

- Docker instalado y disponible desde Ubuntu/WSL (`docker --version`).
- Imagen `ghcr.io/crytic/echidna/echidna:latest` descargable o ya disponible.
- Ambos archivos Solidity en la **misma carpeta**, ya que el auxiliar contiene `import "./VulnerableBank.sol";`.
- Trabajar únicamente en un entorno de prueba, sin fondos reales.

```text
analisiscontratos/
├── VulnerableBank.sol
└── VulnerableBankEchidna.sol
```

El `import` permite que el archivo auxiliar compile y cree una instancia del banco original (`banco = new VulnerableBank()`); sus actores de prueba llaman a `banco.deposit()` y `banco.withdraw()`. **No es necesario añadir funciones de Echidna al contrato auditado.**

### 2. Ejecutar el contenedor y verificar el montaje

Desde **Ubuntu/WSL**, en la carpeta que contiene los `.sol`:

```bash
docker pull ghcr.io/crytic/echidna/echidna:latest
docker run --rm -it --mount "type=bind,source=$(pwd),target=/src" ghcr.io/crytic/echidna/echidna:latest
```

Dentro del contenedor:

```bash
echidna --version
ls /src
```

En esta demostración se verificó **Echidna 2.4.0** y que `/src` contenía los archivos del proyecto. Si se ejecuta Docker desde PowerShell, la expresión `$(pwd)` de Bash debe sustituirse por la sintaxis apropiada de PowerShell; no se debe copiar literalmente el comando de WSL.

### 3. Exploración inicial del contrato original

```bash
echidna /src/VulnerableBank.sol --test-mode exploration
```

**Salida real registrada (16 de noviembre de 2026):** compilación correcta, análisis auxiliar con Slither terminado, `Unique instructions: 675`, `Unique codehashes: 1`, `Corpus size: 4`, `Seed: 1166626813762970013` y `Total calls: 50000`.

El modo `exploration` registra exploración y cobertura, pero **no constituye por sí solo una detección o demostración de reentrada**.

### 4. Prueba basada en propiedades con el contrato auxiliar

Ejecutar:

```bash
echidna /src/VulnerableBankEchidna.sol \
  --contract VulnerableBankEchidna \
  --test-mode property \
  --test-limit 50000
```

El auxiliar contiene dos propiedades:

| Propiedad | Regla evaluada | Resultado real |
| --- | --- | --- |
| `echidna_un_pago_por_retiro` | En una retirada instrumentada no debe registrarse más de un pago al actor. | **FAILED** (`ReturnFalse`). |
| `echidna_fondos_cubren_saldos` | El ETH del banco debe cubrir los saldos modelados del actor y la víctima. | **PASSING** en la campaña. |

**Contraejemplo real reportado por Echidna:**

```text
echidna_un_pago_por_retiro: failed!
Reason: ReturnFalse
Call sequence:
  VulnerableBankEchidna.depositarActor() Value: 0x2
  VulnerableBankEchidna.intentarReentrada(0)
Traces:
  pagosUltimoRetiro() -> 2

echidna_fondos_cubren_saldos: passing
Unique instructions: 2563
Unique codehashes: 3
Corpus size: 7
Seed: 6891570959957412991
Total calls: 50000
```

**Interpretación precisa del argumento `0`:** en `intentarReentrada(0)`, el valor `0` es una **semilla** (`semilla`), **no** el monto transferido. El contrato auxiliar calcula:

```solidity
uint256 saldo = banco.balances(address(actor));
if (saldo < 2) return;
uint256 monto = 1 + (semilla % (saldo / 2));
actor.retirarConReentrada(monto);
```

Con el depósito registrado de `0x2` (= **2 wei**) y semilla `0`, resulta `monto = 1 wei`. La propiedad falla porque se registraron **dos pagos reentrantes**, no porque se hiciera una retirada de cero ni porque se haya demostrado robo de fondos ajenos. En esta prueba los dos descuentos de 1 wei pueden ser aritméticamente válidos bajo Solidity 0.8.x.

`PASSING` significa únicamente que no se encontró un contraejemplo para esa segunda propiedad en las **50.000 llamadas** de esta ejecución. No certifica la seguridad del contrato. Los números `Unique instructions`, `Corpus size` y `Total calls` son métricas de exploración, **no cantidades de vulnerabilidades**.

### 5. Comparación con Slither y Mythril

| Herramienta | Evidencia observada | Alcance de la conclusión |
| --- | --- | --- |
| **Slither** | Cuatro resultados, incluido `reentrancy-eth` (llamada externa antes del cambio de saldo). | Detecta el patrón de código riesgoso; no demuestra explotación. |
| **Mythril v0.24.8** | Tres hallazgos SWC-107: llamada externa (Low), lectura posterior (Medium), escritura posterior (Medium). | Corrobora el riesgo; su secuencia reportada utiliza `withdraw(0)` y no prueba sustracción de fondos. |
| **Echidna 2.4.0** | Contraejemplo de dos pagos de 1 wei en el escenario instrumentado; segunda propiedad sin fallo encontrado. | Evidencia dinámica de reentrada; **no demuestra extracción indebida de ETH**. |

Para reproducibilidad, conservar los archivos originales, versiones de herramientas y compilador, comandos, salidas completas y las semillas indicadas. No comparar directamente los **4** resultados de Slither, **3** de Mythril y **2** propiedades de Echidna como si midieran lo mismo.


### 6. Siguiente validación

Probar una **copia corregida** de `VulnerableBank.sol` aplicando Checks-Effects-Interactions (descontar saldo **antes** de `call`) y repetir las propiedades; la lógica de prueba puede requerir ajustes para tratar explícitamente reversiones esperadas. La corrección y su resultado **todavía no han sido ejecutados ni verificados** en este registro.



## Resultados esperados

- **Slither/Mythril** detectarán reentrancy en `withdraw()`.

## Recomendaciones de mitigación

- Aplicar patrón **Checks-Effects-Interactions**.
- Usar **ReentrancyGuard** de OpenZeppelin.
- Considerar `transfer()` o `send()` con límite de gas controlado.

## Licencia

Este PoC es solo para fines educativos y de investigación de seguridad. **No usar en producción.**
