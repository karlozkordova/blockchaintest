# VulnerableBank PoC

Este proyecto demuestra una **Prueba de Concepto (PoC)** de análisis de seguridad para contratos inteligentes Solidity, enfocada en la detección de la vulnerabilidad **Reentrancy** usando herramientas open source.

## Descripción del Contrato

`VulnerableBank.sol` es un contrato simple que permite a los usuarios **depositar** y **retirar** fondos. Sin embargo, en la función `withdraw()` el balance se actualiza **después** de enviar los fondos, lo que permite ataques de reentrancy.

### Funciones principales
- `deposit()`: Permite enviar fondos al contrato.
- `withdraw(uint _amount)`: Retira la cantidad solicitada si el saldo es suficiente.

## Vulnerabilidad

**Reentrancy:** Un atacante puede volver a llamar a `withdraw()` durante la ejecución antes de que se actualice el saldo, vaciando el contrato.

## Herramientas utilizadas

- **Slither** → Análisis estático para detectar patrones inseguros.
- **Mythril** → Ejecución simbólica para explorar rutas de ejecución vulnerables.
- **Manticore** → Fuzzing dinámico para simular ataques y generar inputs maliciosos.

## Cómo ejecutar el análisis

1. **Instalar dependencias**
   ```bash
   pip install slither-analyzer mythril manticore
   ```

2. **Análisis estático con Slither**
   ```bash
   slither VulnerableBank.sol
   ```

3. **Análisis simbólico con Mythril**
   ```bash
   myth analyze VulnerableBank.sol
   ```

4. **Análisis dinámico con Manticore**
   ```bash
   manticore VulnerableBank.sol
   ```

## Resultados esperados

- **Slither/Mythril** detectarán reentrancy en `withdraw()`.
- **Manticore** generará rutas de ejecución que demuestran la explotación del fallo.

## Recomendaciones de mitigación

- Aplicar patrón **Checks-Effects-Interactions**.
- Usar **ReentrancyGuard** de OpenZeppelin.
- Considerar `transfer()` o `send()` con límite de gas controlado.

## Licencia

Este PoC es solo para fines educativos y de investigación de seguridad. **No usar en producción.**
