// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/**
 * @title RegistroAcademicoVulnerable
 * @notice Ejemplo educativo de control de acceso ausente.
 * @dev USAR SOLO EN HARDHAT LOCAL. Cualquier cuenta puede escribir.
 */
contract RegistroAcademicoVulnerable {
    address public propietario;
    string public mensaje;
    uint256 public contador;

    event MensajeActualizado(address indexed usuario, string nuevoMensaje, uint256 contador);

    constructor() {
        propietario = msg.sender;
        mensaje = "Registro academico sin control de acceso";
    }

    // VULNERABILIDAD INTENCIONAL: NO comprueba msg.sender == propietario.
    function actualizarMensaje(string calldata nuevoMensaje) external {
        mensaje = nuevoMensaje;
        contador++;
        emit MensajeActualizado(msg.sender, nuevoMensaje, contador);
    }
}
