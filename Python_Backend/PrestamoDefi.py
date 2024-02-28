import json
import re
from config import contract_address


class PrestamoDeFiInteractor:
   

    def __init__(self, web3_instance, contract_address, contract_abi, account):
        self.web3 = web3_instance
        self.contract = self.web3.eth.contract(address=contract_address, abi=json.loads(contract_abi))
        self.account = account
        

    def validar_clave_privada(clave):

        # Validación de longitud
        longitud_bytes = len(clave.encode())
        if  longitud_bytes in [256, 512, 1024, 2048, 4096]:
            return True   
        elif longitud_bytes == 64:
            return True
        elif longitud_bytes == 32:
            return True
        
        # Validación de caracteres
        patron = re.compile(r'^0x[a-fA-F0-9+/=]{64}$')
        if not patron.match(clave):
            return False
        
        return True
        
    def validar_address (address):
        if not address:
            return "El campo no puede estar vacío"
        if not re.match("^0x[a-fA-F0-9]{40}$", address):
            return "Error: Introduzca una dirección válida."
        return None
                  
        
    def esPrestamistaDadoDeAlta(self, prestamista_address):
        try:
            #prestamista del mapping empleadosPrestamista
            dado_de_alta = self.contract.functions.esPrestamistaDadoDeAlta(prestamista_address).call()
            
            return dado_de_alta
        except AttributeError:
            print("La función 'empleadosPrestamista' no está definida en el contrato.")
            
        except Exception as e:
            print("Error al verificar si el prestamista está dado de alta:", e)
        return False
    
    def esClienteDadoDeAlta(self, nuevo_cliente_address):
        try:
            #cliente del mapping clientes
            dado_de_alta = self.contract.functions.esClienteDadoDeAlta(nuevo_cliente_address).call()
          
            return dado_de_alta
        except AttributeError:
            print("La función 'clientes' no está definida en el contrato.")
            
        except Exception as e:
            print("Error al verificar si el prestamista está dado de alta:", e)
        return False

    def enviar_transaccion_firmada(self,address_sign,private_key):
        
        try:
            # Obtener el nonce para la transacción
            nonce = self.web3.eth.get_transaction_count(address_sign)
            
        except Exception as e:
            print("No se pudo obtener el Nonce",e)

        try:
            # Construir la transacción
            transaction = {
                'from':  address_sign,
                'nonce': nonce,
                'to': contract_address,
                'value': self.web3.to_wei(0, 'ether'),
                "gas": 4000000,
                'gasPrice': self.web3.to_wei('100', 'gwei')       
            }
        
        except Exception as e:
            print("No se pudo construir la transacción", e)
 
        try:
            # Firmar la transacción
            self.web3.eth.account.sign_transaction(transaction,private_key)
            return True
               
        except ValueError as e:
            print("Clave privada incorrecta: ",e)
        except Exception as e:
            print("La transacción no es válida: ",e)
         
 
    def altaPrestamista(self,address_prestamista):
          
        try:
            tx_hash = self.contract.functions.altaPrestamista(address_prestamista).transact({'from': self.web3.eth.accounts[0]})
            self.web3.eth.wait_for_transaction_receipt(tx_hash)
           
            mensaje_exito = f"\nNuevo prestamista dado de alta con éxito\nHash: {tx_hash.hex()}\n\n"

            return mensaje_exito
        
        except Exception as e:
            return "No se cumplen los requisitos necesarios para completar la transacción: ",str(e)
        
    
    def altaCliente(self, nuevo_cliente_address, prestamista_address):       
        try:
            tx_hash = self.contract.functions.altaCliente(nuevo_cliente_address).transact({'from': prestamista_address})
            self.web3.eth.wait_for_transaction_receipt(tx_hash)
            
            mensaje_exito = f"\nNuevo cliente dado de alta con éxito\nHash: {tx_hash.hex()}\n\n"

            return mensaje_exito
        
        except Exception as e:
            return "No se cumplen los requisitos necesarios para completar la transacción: ",str(e)
        
               
            
    def depositarGarantia(self, direccion_cliente, valor):
        try:
            tx_hash = self.contract.functions.depositarGarantia().transact({'from': direccion_cliente, "value":self.web3.to_wei(valor,"ether")})
            self.web3.eth.wait_for_transaction_receipt(tx_hash)
            
            mensaje_exito = f"\nGarantía depositada con éxito\n El address: {direccion_cliente}, ha depositado: {valor} Ether\nHash: {tx_hash.hex()}\n\n"
            
            return mensaje_exito
        
        except Exception as e:
            return "No se cumplen los requisitos necesarios para completar la transacción: ",str(e)

    def solicitarPrestamo(self, direccion_cliente, monto, plazo):
        try:
            monto_wey = self.web3.to_wei(monto,"ether")
            tx_hash = self.contract.functions.solicitarPrestamo(monto_wey, plazo).transact({'from': direccion_cliente})
            self.web3.eth.wait_for_transaction_receipt(tx_hash)

            mensaje_exito = f"\nEl préstamo se ha solicitado con éxito\nAddress solicitante: {direccion_cliente} \nMonto solicitado: {monto} Ether\nPlazo: {plazo} segundos\n Hash: {tx_hash.hex()}\n\n"

            return mensaje_exito
        
        except Exception as e:
            return "No se cumplen los requisitos necesarios para completar la transacción: ",str(e)
       

    def aprobarPrestamo(self, prestatario_address, prestamo_id,prestamista_address):
        try:
            tx_hash = self.contract.functions.aprobarPrestamo(prestatario_address, prestamo_id).transact({'from': prestamista_address})
            self.web3.eth.wait_for_transaction_receipt(tx_hash)

            mensaje_exito = f"\nSe ha aprobado su préstamo\nHash: {tx_hash.hex()}\n\n" 
            return mensaje_exito
       
        except Exception as e:
            return "No se cumplen los requisitos necesarios para completar la transacción: ",str(e)
       

    def reembolsarPrestamo(self, prestamo_id, cliente_address):

        try:
            tx_hash = self.contract.functions.reembolsarPrestamo(prestamo_id).transact({'from': cliente_address})
            self.web3.eth.wait_for_transaction_receipt(tx_hash)

            mensaje_exito = f"\nSe ha reembolsado su préstamo, con ID: {prestamo_id}\nHash: {tx_hash.hex()}\n\n"
        
            return mensaje_exito
       
        except Exception as e:
            return "No se puede reembolsar el préstamo, porque no cumple algunos requisitos: ",str(e)

    def liquidarGarantia(self, prestamo_id,cliente_address, prestamista_address):
        try:
            tx_hash = self.contract.functions.liquidarGarantia(cliente_address,prestamo_id).transact({'from': prestamista_address})
            self.web3.eth.wait_for_transaction_receipt(tx_hash)

            mensaje_exito = f"\nGarantía liquidada con éxito\nHash: {tx_hash.hex()}\n\n"
            return mensaje_exito
       
        except Exception as e:
            return "No se puede liquidar la garantía, porque no cumple algunos requisitos: ",str(e)

        

    def obtenerPrestamosPorPrestatario(self, prestatario_address):
        try:
            prestamo_ids = self.contract.functions.obtenerPrestamosPorPrestatario(prestatario_address).call()

            mensaje_exito = f"\nAquí tiene la información solicitada:\nID Préstamo: {prestamo_ids}\n\n"
            
            return mensaje_exito
       
        except Exception as e:
            return "Ha habido una excepción en la llamada al contrato: ",str(e)

    def obtenerDetalleDePrestamo(self, prestatario_address, prestamo_id):
        try:
            detalle_prestamo = self.contract.functions.obtenerDetalleDePrestamo(prestatario_address, prestamo_id).call()
            mensaje_exito = f"\nAquí tiene la información solicitada:\nDetalles del préstamo: {detalle_prestamo}\n\n"

            return mensaje_exito
        
        except Exception as e:
            return "Ha habido una excepción en la llamada al contrato: ",str(e)
        

