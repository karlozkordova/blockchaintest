
 // SPDX-License-Identifier: MIT

// Indica la versión mínima del compilador Solidity.
// Se permite utilizar la versión 0.8.20 o superior,
// siempre que sea compatible con la versión 0.8.x.
pragma solidity ^0.8.20;

/**
 * @title RegistroAcademico
 * @author Laboratorio Blockchain
 * @notice Contrato inteligente para almacenar y actualizar
 *         un mensaje dentro de una blockchain Ethereum.
 *
 * @dev Ejemplo educativo para comprender:
 *      - Variables de estado.
 *      - Direcciones Ethereum.
 *      - Constructores.
 *      - Funciones de lectura y escritura.
 *      - Control de acceso mediante msg.sender.
 *      - Eventos y registros de transacciones.
 *      - Persistencia de datos en blockchain.
 */
contract RegistroAcademico {

    // =====================================================
    // 1. VARIABLES DE ESTADO
    // =====================================================

    /**
     * @notice Dirección Ethereum del propietario.
     * @dev Se establece al desplegar el contrato.
     *
     * address: tipo de dato que representa una dirección
     * Ethereum de 20 bytes.
     *
     * public: Solidity genera automáticamente una función
     * de consulta llamada propietario().
     */
    address public propietario;

    /**
     * @notice Mensaje almacenado en el contrato.
     * @dev El contenido se guarda en el estado de Ethereum.
     *
     * string: representa una cadena de caracteres.
     *
     * public: permite consultar su valor mediante mensaje().
     */
    string public mensaje;

    /**
     * @notice Número de veces que se ha actualizado el mensaje.
     *
     * uint256: número entero sin signo de 256 bits.
     * No admite valores negativos.
     *
     * Su valor inicial es 0.
     */
    uint256 public contador;


    // =====================================================
    // 2. EVENTOS
    // =====================================================

    /**
     * @notice Evento emitido al modificar el mensaje.
     *
     * @param usuario Dirección que ejecutó la operación.
     * @param nuevoMensaje Nuevo texto almacenado.
     * @param contador Número total de actualizaciones.
     *
     * Los eventos permiten que aplicaciones externas,
     * como nuestro explorador web, conozcan las acciones
     * realizadas por el contrato.
     *
     * indexed permite filtrar registros por usuario.
     */
    event MensajeActualizado(
        address indexed usuario,
        string nuevoMensaje,
        uint256 contador
    );


    // =====================================================
    // 3. CONSTRUCTOR
    // =====================================================

    /**
     * @notice Inicializa el contrato inteligente.
     *
     * @dev El constructor se ejecuta una sola vez:
     * durante el despliegue del contrato.
     *
     * msg.sender identifica la cuenta que ejecuta
     * la creación del contrato.
     *
     * Esa cuenta se convierte en su propietario.
     */
    constructor() {

        // Registrar como propietario a quien despliega
        // el contrato inteligente.
        propietario = msg.sender;

        // Establecer el mensaje inicial del contrato.
        mensaje = "Test Blockchain UTPL";

        // No es necesario inicializar contador porque
        // los uint256 tienen como valor inicial 0.
    }


    // =====================================================
    // 4. FUNCIÓN PARA ACTUALIZAR EL MENSAJE
    // =====================================================

    /**
     * @notice Permite modificar el mensaje almacenado.
     *
     * @param nuevoMensaje Texto que reemplazará al actual.
     *
     * @dev Esta función modifica variables de estado,
     * por lo que requiere una transacción para ejecutarse.
     *
     * external:
     *   Indica que puede llamarse externamente.
     *
     * calldata:
     *   Indica que el argumento utiliza una región
     *   de datos de solo lectura durante la ejecución.
     *
     * require:
     *   Comprueba una condición. Si no se cumple,
     *   la ejecución se revierte.
     *
     * emit:
     *   Genera un registro del evento indicado.
     */
    function actualizarMensaje(
        string calldata nuevoMensaje
    ) external {

        // ---------------------------------------------
        // PASO 1. VALIDACIÓN DEL USUARIO
        // ---------------------------------------------

        // Solo el propietario puede modificar el mensaje.
        // Si otra cuenta intenta ejecutar esta función,
        // la transacción será revertida.
        require(
            msg.sender == propietario,
            "No autorizado"
        );


        // ---------------------------------------------
        // PASO 2. ACTUALIZACIÓN DEL ESTADO
        // ---------------------------------------------

        // Reemplazar el mensaje existente por el nuevo.
        mensaje = nuevoMensaje;

        // Incrementar en una unidad el contador.
        // Es equivalente a: contador = contador + 1;
        contador++;


        // ---------------------------------------------
        // PASO 3. REGISTRO DEL EVENTO
        // ---------------------------------------------

        // Emitir un evento para registrar:
        // 1. Dirección que realizó la actualización.
        // 2. Nuevo mensaje.
        // 3. Número acumulado de actualizaciones.
        emit MensajeActualizado(
            msg.sender,
            nuevoMensaje,
            contador
        );
    }
}

