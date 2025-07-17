// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/**
 * @title SafeBank
 * @dev Contrato seguro contra ataques de reentrancy
 *      gracias a que actualiza el estado ANTES de enviar Ether.
 */
contract SafeBank {
    // Mapeo de balances
    mapping(address => uint256) public balances;

    /**
     * @dev Permite depositar Ether
     */
    function deposit() public payable {
        balances[msg.sender] += msg.value;
    }

    /**
     * @dev Retiro SEGURO:
     *  - Actualiza balance antes de enviar Ether
     *  - Esto bloquea reentrancy porque el balance queda en 0
     */
    function withdraw() public {
        uint256 bal = balances[msg.sender];
        require(bal > 0, "No balance to withdraw");

        // ✅ MITIGACIÓN: actualizamos el estado primero
        balances[msg.sender] = 0;

        // Luego enviamos fondos
        (bool success,) = msg.sender.call{value: bal}("");
        require(success, "Transfer failed");
    }

    /**
     * @dev Consulta el balance del contrato
     */
    function getBalance() public view returns (uint256) {
        return address(this).balance;
    }
}
