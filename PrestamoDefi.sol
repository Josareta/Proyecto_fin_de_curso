git push// SPDX-License-Identifier: MIT

pragma solidity ^0.8.0;

contract prestamoDefi {

    address payable public socioPrincipal;

    struct Prestamo {
        uint256 id;
        address prestatario;
        uint256 monto;
        uint256 plazo;
        uint256 tiempoSolicitud;
        uint256 tiempoLimite;
        bool aprobado;
        bool reembolsado;
        bool liquidado;
    }

   struct Cliente {
        bool activado;
        uint256 saldoGarantia;
        mapping(uint256 => Prestamo) prestamos;
        uint256[]prestamoIds;
    }

    mapping(address=> Cliente) clientes;
    mapping(address=> bool) empleadosPrestamista;

    event SolicitudPrestamo (address prestatario, uint256 monto, uint256 plazo);
    event PrestamoAprobado(address indexed prestamista, address indexed prestatario, uint256 indexed id, uint256 monto);
    event PrestamoReembolsado(address indexed prestatario, uint256 indexed id, uint256 monto);
    event GarantiaLiquidada(address prestatario, uint256 id, uint256 monto);
    event EventoAltaCliente(address nuevoCliente);
    event EventoDepositoGarantia(address depositario, uint256 depositoGarantia);
    event EventoAltaPrestamista(address nuevoPrestamista);
   

     modifier soloSocioPrincipal() {
        require(msg.sender == socioPrincipal, "No eres el Socio principal");
        _;
    }

     modifier soloEmpleadoPrestamista() {
        require(empleadosPrestamista[msg.sender], "No tienes derechos de empleado prestamista");
        _;
    }

     modifier soloClienteRegistrado() {
        require (clientes[msg.sender].activado, "No estas registrado");
        _;
    }

     constructor() {
        socioPrincipal = payable(msg.sender);
        empleadosPrestamista[socioPrincipal]= true;
    }


    function altaPrestamista(address nuevoPrestamista) public soloSocioPrincipal() {
        require(!empleadosPrestamista[nuevoPrestamista], "Este prestamista ya esta dado de alta como prestamista");
        empleadosPrestamista[nuevoPrestamista] = true;

        //emito un evento de nuevo prestamista
        emit EventoAltaPrestamista(nuevoPrestamista);
    }


    function altaCliente(address nuevoCliente) public soloEmpleadoPrestamista() {
        require(!clientes[nuevoCliente].activado, "Este cliente ya esta dado de alta");

        // Crear una instancia del struct Cliente en storage
        Cliente storage structNuevoCliente = clientes[nuevoCliente];

        // Inicializar los valores
        structNuevoCliente.saldoGarantia = 0;
        structNuevoCliente.activado = true;

        //emito un evento de nuevo cliente
        emit EventoAltaCliente(nuevoCliente);
    }
    

    function depositarGarantia() public payable soloClienteRegistrado() {
        // Asegurar que se haya enviado al menos una cantidad mayor a 0
        require(msg.value > 0, "Debe enviar una cantidad mayor a 0");

        // Actualizar el saldoGarantia del cliente
        clientes[msg.sender].saldoGarantia += msg.value;

         // Emito un evento del depositario y su valor
        emit EventoDepositoGarantia(msg.sender, msg.value);
    }

    function solicitarPrestamo(uint256 monto_, uint256 plazo_) public soloClienteRegistrado() returns (uint256) {
        // Comprobar si el cliente tiene suficiente saldoGarantia
        require(clientes[msg.sender].saldoGarantia >= monto_, "Saldo de garantia insuficiente");

        // Calcular el nuevoId
        uint256 nuevoId = clientes[msg.sender].prestamoIds.length + 1;

        // Instanciar el struct Prestamo y asignar los datos
        Prestamo storage nuevoPrestamo = clientes[msg.sender].prestamos[nuevoId];
        nuevoPrestamo.id = nuevoId;
        nuevoPrestamo.prestatario = msg.sender;
        nuevoPrestamo.monto = monto_;
        nuevoPrestamo.plazo = plazo_;
        nuevoPrestamo.tiempoSolicitud = block.timestamp;
        nuevoPrestamo.tiempoLimite = 0;
        nuevoPrestamo.aprobado = false;
        nuevoPrestamo.reembolsado = false;
        nuevoPrestamo.liquidado = false;

        // Añadir el nuevoId al array prestamoIds
        clientes[msg.sender].prestamoIds.push(nuevoId);

        // Emitir el evento SolicitudPrestamo
        emit SolicitudPrestamo(msg.sender, monto_, plazo_);

        // Devolver el nuevoId como parámetro de salida
        return nuevoId;
    }

    function aprobarPrestamo(address prestatario_, uint256 id_) public soloEmpleadoPrestamista() {
        // Instanciar una variable de tipo struct Cliente storage llamada prestatario
        Cliente storage prestatario = clientes[prestatario_];

        // Comprobar si el id_ del préstamo existe para el prestatario
        require(id_ > 0 && id_ <= prestatario.prestamoIds.length, "Id de prestamo no valido");

        // Instanciar una variable de tipo struct Prestamo storage llamada prestamo
        Prestamo storage prestamo = prestatario.prestamos[id_];

        // Comprobar si el préstamo no está aprobado, no reembolsado y no liquidado
        require(!prestamo.aprobado, "El prestamo ya esta aprobado");
        require(!prestamo.reembolsado, "El prestamo ya esta reembolsado");
        require(!prestamo.liquidado, "El prestamo ya esta liquidado");

        // Aprobar el préstamo y establecer el tiempoLimite
        prestamo.aprobado = true;
        prestamo.tiempoLimite = block.timestamp + prestamo.plazo;

        // Emitir el evento PrestamoAprobado
        emit PrestamoAprobado(msg.sender, prestatario_, id_, prestamo.monto);

    }

 

    function reembolsarPrestamo(uint256 id_) public soloClienteRegistrado() {
        // Instanciar una variable de tipo struct Cliente storage llamada prestatario
        Cliente storage prestatario = clientes[msg.sender];

        // Comprobar si el id_ del préstamo existe para el prestatario
        require(id_ > 0 && id_ <= prestatario.prestamoIds.length, "Id de prestamo no valido");

        // Instanciar una variable de tipo struct Prestamo storage llamada prestamo
        Prestamo storage prestamo = prestatario.prestamos[id_];

        // Comprobar si el prestatario es el emisor de la petición
        require(prestamo.prestatario == msg.sender, "El prestamo no pertenece al prestatario");

        // Comprobar si el préstamo está aprobado, no reembolsado, no liquidado y el tiempo límite no ha vencido
        require(prestamo.aprobado, "El prestamo no esta aprobado");
        require(!prestamo.reembolsado, "El prestamo ya esta reembolsado");
        require(!prestamo.liquidado, "El prestamo ya esta liquidado");
        require(prestamo.tiempoLimite >= block.timestamp, "El tiempo limite ha vencido");

        // Transferir el monto del préstamo al socioPrincipal
        socioPrincipal.transfer(prestamo.monto);

        // Actualizar los campos del préstamo
        prestamo.reembolsado = true;

        // Restar al saldoGarantia del prestatario el monto del préstamo
        prestatario.saldoGarantia -= prestamo.monto;

        // Emitir el evento PrestamoReembolsado
        emit PrestamoReembolsado(msg.sender, id_, prestamo.monto);
    }


    function liquidarGarantia(address prestatario_, uint256 id_) public soloEmpleadoPrestamista() {
        // Instanciar una variable de tipo struct Cliente storage llamada prestatario
        Cliente storage prestatario = clientes[prestatario_];

        // Comprobar si el id_ del préstamo existe para el prestatario
        require(id_ > 0 && id_ <= prestatario.prestamoIds.length, "Id de prestamo no valido");

        // Instanciar una variable de tipo struct Prestamo storage llamada prestamo
        Prestamo storage prestamo = prestatario.prestamos[id_];

        // Comprobar si el préstamo está aprobado, no reembolsado, no liquidado y el tiempo límite ha vencido
        require(prestamo.aprobado, "El prestamo no esta aprobado");
        require(!prestamo.reembolsado, "El prestamo ya esta reembolsado");
        require(!prestamo.liquidado, "El prestamo ya esta liquidado");
        require(prestamo.tiempoLimite < block.timestamp, "El tiempo limite no ha vencido");

        // Transferir el monto de garantía del prestatario al socioPrincipal
        socioPrincipal.transfer(prestatario.saldoGarantia);

        // Actualizar los campos del préstamo
        prestamo.liquidado = true;

        // Restar al saldoGarantia del prestatario el monto de la garantía
        prestatario.saldoGarantia -= prestamo.monto;

        // Emitir el evento GarantiaLiquidada
        emit GarantiaLiquidada(prestatario_, id_, prestamo.monto);
    }

    function obtenerPrestamosPorPrestatario(address prestatario_) public view returns (uint256[] memory) {
        // Obtener los identificadores de todos los préstamos solicitados por el prestatario
        return clientes[prestatario_].prestamoIds;
    }

    function obtenerDetalleDePrestamo(address prestatario_, uint256 id_) public view returns (Prestamo memory) {
        // Obtener los detalles del préstamo
        return clientes[prestatario_].prestamos[id_];
    }

}