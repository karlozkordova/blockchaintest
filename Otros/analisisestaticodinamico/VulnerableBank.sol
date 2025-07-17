pragma solidity ^0.8.0;

// Este contrato implementa un banco simple que permite depositar y retirar fondos.
// Sin embargo, contiene una vulnerabilidad crítica de reentrancy.

contract VulnerableBank {
    // Mapeo de direcciones a su balance en el contrato
    mapping(address => uint) public balances;

    // Función para depositar fondos en el contrato
    // msg.value se suma al balance del remitente
    function deposit() public payable {
        balances[msg.sender] += msg.value;
    }

    // Función para retirar una cantidad específica del balance del usuario
    // VULNERABILIDAD: Actualiza el saldo DESPUÉS de enviar los fondos, permitiendo reentrancy
    function withdraw(uint _amount) public {
        // Verifica que el usuario tenga saldo suficiente
        require(balances[msg.sender] >= _amount, "Saldo insuficiente");

        // Envía los fondos solicitados al remitente
        // Aquí se produce una llamada externa que puede disparar código malicioso
        (bool sent, ) = msg.sender.call{value: _amount}("");
        require(sent, "Error al enviar");

        // Actualiza el balance solo después de la llamada externa
        // Un atacante puede reentrar antes de que esta línea se ejecute
        balances[msg.sender] -= _amount;
    }
}

