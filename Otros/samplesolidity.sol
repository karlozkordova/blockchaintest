// Declaración de  la versión del compilador Solidity que se usará.
pragma solidity ^0.8.0;

// Definición del nombre del contrato, en este caso"Almacenamiento".
contract Almacenamiento {

    // Variable de estado privada que almacenará un número entero sin signo.
    // Se guarda en el almacenamiento persistente de la blockchain.
    uint private dato;

    // Función pública que permite guardar un nuevo valor.
    // "_nuevoDato" es el parámetro recibido, tipo uint (número entero positivo).
    function guardar(uint _nuevoDato) public {
        dato = _nuevoDato;  // Asigna el valor recibido a la variable "dato".
    }

    // Función pública de solo lectura que devuelve el valor almacenado.
    // "view" indica que no modifica el estado del contrato.
    function leer() public view returns (uint) {
        return dato;  // Devuelve el valor actual de "dato".
    }
}