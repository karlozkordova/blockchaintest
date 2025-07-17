// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/**
 * @title VulnerableBank
 * @dev Contrato que permite depósitos y retiros, pero tiene
 *      una vulnerabilidad de reentrancy porque actualiza el estado
 *      después de enviar Ether.
 */
contract VulnerableBank {
    // Mapeo de balances de cada usuario
    mapping(address => uint256) public balances;

    /**
     * @dev Permite que cualquier usuario deposite Ether
     * El balance se almacena en el mapping 'balances'
     */
    function deposit() public payable {
        balances[msg.sender] += msg.value;
    }

    /**
     * @dev Retiro vulnerable:
     *  - Obtiene el balance del usuario
     *  - ENVÍA ETHER antes de actualizar el balance
     *  - Esto permite que un contrato atacante reingrese
     */
    function withdraw() public {
        uint256 bal = balances[msg.sender];
        require(bal > 0, "No balance to withdraw");

        // ⚠️ VULNERABILIDAD:
        // Se llama a msg.sender (contrato externo) antes de actualizar balance
        (bool success,) = msg.sender.call{value: bal}("");
        require(success, "Transfer failed");

        // Actualización de estado después -> permite reentrancy
        balances[msg.sender] = 0;
    }

    /**
     * @dev Consulta el balance del contrato
     */
    function getBalance() public view returns (uint256) {
        return address(this).balance;
    }
}
