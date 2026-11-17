// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "./VulnerableBank.sol";

/// @notice Actor controlado por el harness. Solo laboratorio local.
contract ActorPruebaBank {
    VulnerableBank public immutable banco;
    address public immutable controlador;
    bool private atacando;
    bool private reentro;
    uint256 private cantidad;
    uint256 public pagosUltimoRetiro;

    constructor(VulnerableBank _banco) {
        banco = _banco;
        controlador = msg.sender;
    }

    modifier soloControlador() {
        require(msg.sender == controlador, "Sin autorizacion");
        _;
    }

    function depositar() external payable soloControlador {
        banco.deposit{value: msg.value}();
    }

    function retirarConReentrada(uint256 monto) external soloControlador {
        pagosUltimoRetiro = 0;
        reentro = false;
        cantidad = monto;
        atacando = true;
        banco.withdraw(monto);
        atacando = false;
    }

    receive() external payable {
        if (atacando) {
            pagosUltimoRetiro += 1;
            if (!reentro) {
                reentro = true;
                banco.withdraw(cantidad);
            }
        }
    }
}

/// @notice Harness de invariantes: no modifica VulnerableBank.sol.
contract VulnerableBankEchidna {
    VulnerableBank public banco;
    ActorPruebaBank public actor;
    ActorPruebaBank public victima;

    constructor() {
        banco = new VulnerableBank();
        actor = new ActorPruebaBank(banco);
        victima = new ActorPruebaBank(banco);
    }

    // Echidna puede enviar ETH a funciones payable, que se deposita en el banco.
    function depositarActor() external payable {
        actor.depositar{value: msg.value}();
    }

    function depositarVictima() external payable {
        victima.depositar{value: msg.value}();
    }

    // Restringimos a montos > 0 y <= saldo / 2 para evitar que un
    // subdesbordamiento de Solidity 0.8 revierta la reentrada completa.
    function intentarReentrada(uint256 semilla) external {
        uint256 saldo = banco.balances(address(actor));
        if (saldo < 2) return;
        uint256 monto = 1 + (semilla % (saldo / 2));
        actor.retirarConReentrada(monto);
    }

    // Debe FALLAR si un unico retiro produce dos pagos por reentrada.
    function echidna_un_pago_por_retiro() public view returns (bool) {
        return actor.pagosUltimoRetiro() <= 1;
    }

    // Control complementario: la reentrada con montos acotados no implica
    // automaticamente extraer fondos no respaldados por saldos.
    function echidna_fondos_cubren_saldos() public view returns (bool) {
        uint256 pasivos = banco.balances(address(actor)) +
            banco.balances(address(victima));
        return address(banco).balance >= pasivos;
    }
}
