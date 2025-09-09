
# 🔓 Laboratorio 3: Análisis de Vulnerabilidad por Reentrancy en Smart Contracts

Este laboratorio demuestra cómo funciona la **vulnerabilidad de Reentrancy** en contratos inteligentes escritos en Solidity y desplegados en la blockchain de Ethereum.

---

## 🎯 Objetivos

- Comprender la **naturaleza del ataque de reentrancy** y su impacto en contratos inteligentes.
- Aprender a **explotar una vulnerabilidad** usando un contrato atacante.
- Analizar las **consecuencias de no actualizar el estado antes de transferir fondos**.
- Conectar los conceptos de **seguridad en blockchain**: inmutabilidad, gas, llamadas externas, firma digital, y buenas prácticas.

---

## 📝 Contexto Teórico

El **ataque de reentrancy** ocurre cuando:

1. Un contrato víctima envía Ether a otro contrato (externo).
2. El contrato atacante tiene un `fallback` o `receive()` que **vuelve a llamar** a la función vulnerable de la víctima **antes de que se actualice el estado interno**.
3. Esto permite **retirar fondos múltiples veces en una misma transacción**.

### Conceptos de seguridad involucrados

- **Inmutabilidad:** una vez desplegado, el contrato vulnerable no puede modificarse.
- **Firma digital:** el ataque está firmado por el atacante, pero la vulnerabilidad está en la lógica del contrato.
- **Gas:** permite múltiples ejecuciones recursivas hasta agotar el gas.
- **Patrón Checks-Effects-Interactions:** orden correcto que evita reentrancy.
- **Uso de ReentrancyGuard (OpenZeppelin):** mitiga ataques.

---

## 📂 Archivos del laboratorio

1. **`VulnerableBank.sol`** → Contrato vulnerable que permite depósitos y retiros.
2. **`Attacker.sol`** → Contrato malicioso que explota la vulnerabilidad.

---

## 🛠️ Pasos del Laboratorio

### 1. Abrir Remix IDE
- [https://remix.ethereum.org](https://remix.ethereum.org)

### 2. Crear los contratos
- Copia el contenido de `VulnerableBank.sol` y `Attacker.sol` en Remix.

### 3. Desplegar el contrato VulnerableBank
- Deploy `VulnerableBank`.
- Deposita algo de Ether (ejemplo: **1 ETH**) desde una cuenta víctima.

### 4. Desplegar el contrato Attacker
- Deploy `Attacker`, pasando como parámetro la dirección del contrato VulnerableBank.

### 5. Ejecutar el ataque
- Llama a `attack()` desde el contrato Attacker enviando por ejemplo **0.1 ETH**.
- Observa cómo se retiran todos los fondos de `VulnerableBank` en una sola transacción.

---

## 🔍 Qué observar en el ataque

- **Balance inicial** del contrato VulnerableBank.
- **Balance final** después del ataque.
- La transacción en el explorador mostrará **múltiples llamadas internas** (reentradas).
- El estado se actualiza **después** de enviar fondos, permitiendo el exploit.

---

## 🔒 Mitigación

Para evitar este ataque:

1. **Pattern Checks-Effects-Interactions**:
   - Actualizar el estado ANTES de enviar Ether.
2. Usar `transfer()` en lugar de `call` (aunque ahora `call` es recomendado, debe hacerse con cuidado).
3. Usar `ReentrancyGuard` de OpenZeppelin.

---

## ✅ Resultados esperados

- Entiendes cómo un contrato vulnerable puede ser explotado.
- Visualizas cómo un atacante drena fondos con reentrancy.
- Relacionas los **conceptos teóricos de seguridad con la práctica**.

---

## 📎 Relación con seguridad en blockchain

- **Inmutabilidad:** El contrato vulnerable no puede corregirse una vez desplegado.
- **Confianza en el código:** Blockchain elimina intermediarios, pero requiere código seguro.
- **Buenas prácticas:** La lógica del contrato es tan importante como la criptografía.

---

## 📊 Conclusión

Este laboratorio demuestra que **la seguridad en blockchain no depende solo de la criptografía o firmas digitales**, sino también de la **correcta implementación del código**. Una sola vulnerabilidad lógica puede causar pérdidas irreparables.

---

## 📊Entregables:

1. **Contrato inteligente vulnerable** implementado en Solidity (código fuente).
2. **Contrato atacante** y evidencia de explotación de la vulnerabilidad.
3. **Capturas de pruebas** en Remix mostrando el ataque y el efecto (retiro repetido de fondos).
4. **Reporte técnico** en PDF que incluya:
   - Explicación paso a paso del ataque.
   - Análisis de por qué ocurre la vulnerabilidad.
   - Propuesta de soluciones de mitigación (ej. checks-effects-interactions, reentrancyGuard).
5. **Reflexión final:** qué riesgos reales representa esta vulnerabilidad en proyectos DeFi y qué aprendió el estudiante para prevenirla.
