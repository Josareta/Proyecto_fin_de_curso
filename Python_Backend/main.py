from PrestamoDefi import PrestamoDeFiInteractor
from web3 import Web3
from config import contract_address, contract_abi


ganache_url = "http://127.0.0.1:7545"

# Instanciar Web3
web3_instance = Web3(Web3.HTTPProvider(ganache_url))
contract = web3_instance.eth.contract(address=contract_address, abi=contract_abi)


address_owner = web3_instance.eth.accounts[0]



def mostrar_menu():
    print("Bienvenido al sistema de préstamos DeFi")
    print("1. Dar de alta un prestamista")
    print("2. Dar de alta un cliente")
    print("3. Depositar garantía")
    print("4. Solicitar un préstamo")
    print("5. Aprobar un préstamo")
    print("6. Reembolsar un préstamo")
    print("7. Liquidar garantía")
    print("8. Obtener préstamos por prestatario")
    print("9. Obtener detalle de préstamo")
    print("0. Salir")

def obtener_cuenta_conectada():
    try:
       
        # Intentar acceder a una propiedad o método para verificar la conexión
        cuentas = web3_instance.eth.accounts

        # Si se obtienen las cuentas, la conexión se ha establecido correctamente
        if cuentas:
            print("Conexión exitosa a Ganache")
            return cuentas[0]  # Devolver la primera cuenta conectada
        else:
            print("No se encontraron cuentas conectadas.")
            return None
    except Exception as e:
        print("Error al conectar a Ganache:", e)
        return None

    
def main():
    account = obtener_cuenta_conectada()  # Llamar a obtener_cuenta_conectada() para definir 'account'
    
    if account:
        web3_instance = Web3(Web3.HTTPProvider('http://localhost:7545'))

     
        interactor = PrestamoDeFiInteractor(web3_instance, contract_address, contract_abi, account)
       
        
        while True:
            mostrar_menu()
            opcion = input("Seleccione una opción: ")

            if opcion == "1":
                print("Propietario",address_owner)
                nuevo_prestamista_address = input("Ingrese la dirección del nuevo prestamista: ")
               
                # Validación de address
                resultado = PrestamoDeFiInteractor.validar_address(nuevo_prestamista_address)
                if resultado:
                        print(resultado)
                        continue
                
                # Verificar si el prestamista está dado de alta
                if interactor.esPrestamistaDadoDeAlta(nuevo_prestamista_address):
                    print("El prestamista ya está dado de alta.")
                    continue  # Regresar al inicio del bucle para mostrar el menú nuevamente
                
                clave_privada_owner = input("Introduzca su clave privada: ")
                
                # Validar formato clave privada
                if not PrestamoDeFiInteractor.validar_clave_privada(clave_privada_owner):
                    print("Formato no válido")
                    continue

                # firmar transacción
                try:

                    if not interactor.enviar_transaccion_firmada(address_owner,clave_privada_owner):
                         
                        print("Clave privada no válida")
                        continue

                except Exception as e:
                        print("Hubo un problema en la conexión con la Blockchain: ", e)
                        continue
                
                # Enviar transacción llamando a la función
                try:
                    respuesta = interactor.altaPrestamista(nuevo_prestamista_address)
                    print(respuesta)

            
                except Exception as e:
                    print("Ocurrió una excepción en la respuesta del contrato: ",e)
            

            elif opcion == "2":
                print("Propietario",address_owner)
                nuevo_cliente_address = input("Ingrese la dirección del nuevo cliente: ")

                # Validación de address
                resultado = PrestamoDeFiInteractor.validar_address(nuevo_cliente_address)
                if resultado:
                        print(resultado)
                        continue

                # Verificar si el cliente está dado de alta
                if interactor.esClienteDadoDeAlta(nuevo_cliente_address):
                    print("El cliente ya está dado de alta.")
                    continue
                
                prestamista_address = input("Ingrese la dirección del prestamista que registra al cliente: ")

                 # Validación de address
                resultado = PrestamoDeFiInteractor.validar_address(prestamista_address)
                if resultado:
                        print(resultado)
                        continue
        
                # Verificar si el prestamista está dado de alta
                if not interactor.esPrestamistaDadoDeAlta(prestamista_address):
                    print("El prestamista no está dado de alta.")
                    continue  # Regresar al inicio del bucle para mostrar el menú nuevamente

                prestamista_private_key = input("Ingrese la clave privada del prestamista: ")

                # Validar formato clave privada
                if not PrestamoDeFiInteractor.validar_clave_privada(prestamista_private_key):
                    print("Formato no válido")
                    continue

                # firmar transacción
                try:

                    if not interactor.enviar_transaccion_firmada(prestamista_address,prestamista_private_key):
                        print("Clave privada no válida")
                        continue

                except Exception as e:
                        print("Hubo un problema al conectar con la blockchain: ",e)
                        continue
                
                 # Enviar transacción llamando a la función
                try:
                    respuesta = interactor.altaCliente(nuevo_cliente_address,prestamista_address)
                    print(respuesta)

                except Exception as e:
                    print("Ocurrió una excepción al dar de alta al nuevo prestamista: ",e)
                

            elif opcion == "3":
                direccion_cliente = input("Ingrese la dirección del cliente: ")

                # Validación de address
                resultado = PrestamoDeFiInteractor.validar_address(direccion_cliente)
                if resultado:
                        print(resultado)
                        continue
                
                # Verificar si el cliente está dado de alta
                if not interactor.esClienteDadoDeAlta(direccion_cliente):
                    print("El cliente no está dado de alta.")
                    continue


                valor = int(input("Ingrese el monto de la garantía a depositar, en Ether: "))
                saldo_wei =  web3_instance.eth.get_balance(direccion_cliente)
                saldo_ether= web3_instance.from_wei(saldo_wei, "ether")

                if valor > saldo_ether:
                    print("Su saldo es: ", saldo_ether, " Ether. No tiene saldo suficiente") 
                    continue
                     
                clave_privada_cliente = input("Ingrese la clave privada del cliente: ")

                # Validar formato clave privada
                if not PrestamoDeFiInteractor.validar_clave_privada(clave_privada_cliente):
                    print("Formato no válido")
                    continue

                 # firmar transacción
                try:

                    if not interactor.enviar_transaccion_firmada(direccion_cliente,clave_privada_cliente):
                         
                        print("Clave privada no válida")
                        continue

                except Exception as e:
                        print("Hubo un problema al conectar con la blockchain: ", e)
                        continue


                 # Enviar transacción llamando a la función
                try:
                    respuesta = interactor.depositarGarantia(direccion_cliente,valor)
                    print(respuesta)

                except Exception as e:
                    print("Ocurrió una excepción al depositar la garantía: ", e)

            elif opcion == "4":
                direccion_cliente = input("Ingrese la dirección del cliente: ")


                # Validación de address
                resultado = PrestamoDeFiInteractor.validar_address(direccion_cliente)
                if resultado:
                        print(resultado)
                        continue
                
                # Verificar si el cliente está dado de alta
                if not interactor.esClienteDadoDeAlta(direccion_cliente):
                    print("El cliente no está dado de alta.")
                    continue

                
                monto = int(input("Ingrese el monto del préstamo solicitado, en ether: "))
                

                plazo_segundos = int(input("Ingrese el plazo del préstamo en segundos: "))
               
                clave_privada_cliente = input("Ingrese la clave privada del cliente: ")
                
                # Validar formato clave privada
                if not PrestamoDeFiInteractor.validar_clave_privada(clave_privada_cliente):
                    print("Formato no válido")
                    continue

                 # firmar transacción
                try:

                    if not interactor.enviar_transaccion_firmada(direccion_cliente,clave_privada_cliente):
                         
                        print("Clave privada no válida")
                        continue

                except Exception as e:
                        print("Hubo un problema al conectar con la blockchain: ",e)
                        continue
                
                # Enviar transacción llamando a la función
                try:
                    resultado = interactor.solicitarPrestamo(direccion_cliente, monto, plazo_segundos)
                    print(resultado)

                except Exception as e:
                    print("Ocurrió una excepción al solicitar el préstamo: ",e)

            elif opcion == "5":
                prestatario_address = input("Ingrese la dirección del prestatario: ")

                # Validación de address
                resultado = PrestamoDeFiInteractor.validar_address(prestatario_address)
                if resultado:
                        print(resultado)
                        continue
                
                # Verificar si el cliente está dado de alta
                if not interactor.esClienteDadoDeAlta(prestatario_address):
                    print("El cliente no está dado de alta.")
                    continue
                
                prestamo_id = int(input("Ingrese el ID del préstamo a aprobar: "))
                

                prestamista_address = input("Ingrese la dirección del prestamista: ")

                # Validación de address
                resultado = PrestamoDeFiInteractor.validar_address(prestamista_address)
                if resultado:
                        print(resultado)
                        continue
                
                # Verificar si el prestamista está dado de alta
                if not interactor.esPrestamistaDadoDeAlta(prestamista_address):
                    print("El prestamista no está dado de alta.")
                    continue  

                prestamista_private_key = input("Ingrese la clave privada del prestamista: ")

                # Validar formato clave privada
                if not PrestamoDeFiInteractor.validar_clave_privada(prestamista_private_key):
                    print("Formato no válido")
                    continue

                 # firmar transacción
                try:

                    if not interactor.enviar_transaccion_firmada(prestamista_address,prestamista_private_key):
                        print("Clave privada no válida")
                        continue
                except Exception as e:
                        print("Hubo un problema al conectar con la blockchain: ",e)
                        continue
                
                
                # Enviar transacción llamando a la función
                try:
                    respuesta = interactor.aprobarPrestamo(prestatario_address,prestamo_id,prestamista_address)
                    print(respuesta)

                except Exception as e:
                    print("Ocurrió una excepción al aprobar el préstamo: ",e)


            elif opcion == "6":
                while True:
                    try:
                        prestamo_id = int(input("Ingrese el ID del préstamo a reembolsar: "))
                        break  # Salir del bucle si la conversión a entero fue exitosa
                    except ValueError:
                        print("Error: Por favor, ingrese un número entero válido.")
                     
                cliente_address = input("Ingrese la dirección del cliente: ")

                # Validación de address
                resultado = PrestamoDeFiInteractor.validar_address(cliente_address)
                if resultado:
                        print(resultado)
                        continue
                
                # Verificar si el cliente está dado de alta
                if not interactor.esClienteDadoDeAlta(cliente_address):
                    print("El cliente no está dado de alta.")
                    continue
                
                cliente_private_key = input("Ingrese la clave privada del cliente: ")

                # Validar formato clave privada
                if not PrestamoDeFiInteractor.validar_clave_privada(cliente_private_key):
                    print("Formato no válido")
                    continue

                 # firmar transacción
                try:

                    if not interactor.enviar_transaccion_firmada(cliente_address,cliente_private_key):
                        print("Clave privada no válida")
                        continue
                except Exception as e:
                        print("Hubo un problema al conectar con la blockchain: ",e)
                        continue
                
                # Enviar transacción llamando a la función
                try:
                    respuesta = interactor.reembolsarPrestamo(prestamo_id,cliente_address)
                    print(respuesta)

                except Exception as e:
                    print("Ocurrió una excepción al reembolsar el préstamo: ",e)


            elif opcion == "7":
                while True:
                        try:
                            prestamo_id = int(input("Ingrese el ID del préstamo a liquidar la garantía: "))
                            break  # Salir del bucle si la conversión a entero fue exitosa
                        except ValueError:
                            print("Error: Por favor, ingrese un número entero válido.")

                prestamista_address = input("Ingrese la dirección del prestamista: ")

                # Validación de address
                resultado = PrestamoDeFiInteractor.validar_address(prestamista_address)
                if resultado:
                        print(resultado)
                        continue
                
                # Verificar si el prestamista está dado de alta
                if not interactor.esPrestamistaDadoDeAlta(prestamista_address):
                    print("El prestamista no está dado de alta.")
                    continue 

                cliente_address = input("Ingrese la dirección del cliente: ")

                 # Validación de address
                resultado = PrestamoDeFiInteractor.validar_address(cliente_address)
                if resultado:
                        print(resultado)
                        continue
                
                # Verificar si el cliente está dado de alta
                if not interactor.esClienteDadoDeAlta(cliente_address):
                    print("El cliente no está dado de alta.")
                    continue 
                
                prestamista_private_key = input("Ingrese la clave privada del prestamista: ")

                # Validar formato clave privada
                if not PrestamoDeFiInteractor.validar_clave_privada(prestamista_private_key):
                    print("Formato no válido")
                    continue

                 # firmar transacción
                try:

                    if not interactor.enviar_transaccion_firmada(prestamista_address,prestamista_private_key):
                        print("Clave privada no válida")
                        continue
                except Exception as e:
                        print("Hubo un problema al conectar con la blockchain: ",e)
                        continue
                
                 # Enviar transacción llamando a la función
                try:
                    respuesta = interactor.liquidarGarantia(prestamo_id,cliente_address ,prestamista_address)
                    print(respuesta)

                except Exception as e:
                    print("Ocurrió una excepción al reembolsar el préstamo: ",e)

                

            elif opcion == "8":

                prestatario_address = input("Ingrese la dirección del prestatario: ")
                
                # Validación de address
                resultado = PrestamoDeFiInteractor.validar_address(prestatario_address)
                if resultado:
                        print(resultado)
                        continue
                
                # Verificar si el cliente está dado de alta
                if not interactor.esClienteDadoDeAlta(prestatario_address):
                    print("Este prestatario, no está dado de alta.")
                    continue

                address_consult = input("Introduzca su address para hacer la consulta: ")
                
                 # Validación de address
                resultado = PrestamoDeFiInteractor.validar_address(address_consult)
                if resultado:
                        print(resultado)
                        continue
                
                consult_private_key = input ("Introduzca su clave privada: ")

                # Validar formato clave privada
                if not PrestamoDeFiInteractor.validar_clave_privada(consult_private_key):
                    print("Formato no válido")
                    continue

                 # firmar transacción
                try:

                    if not interactor.enviar_transaccion_firmada(address_consult,consult_private_key):
                        print("Clave privada no válida")
                        continue
                except Exception as e:
                        print("Hubo un problema al conectar con la blockchain: ",e)
                        continue

               
                 # Obtener los datos llamando a la función
                try:
                    respuesta = interactor.obtenerPrestamosPorPrestatario(prestatario_address)
                    print(respuesta)

                except Exception as e:
                    print("Ocurrió una excepción al obtener la información: ",e)

            elif opcion == "9":
                prestatario_address = input("Ingrese la dirección del prestatario: ")

                 # Validación de address
                resultado = PrestamoDeFiInteractor.validar_address(prestatario_address)
                if resultado:
                        print(resultado)
                        continue
                
                # Verificar si el cliente está dado de alta
                if not interactor.esClienteDadoDeAlta(prestatario_address):
                    print("Este prestatario, no está dado de alta.")
                    continue

                while True:
                        try:
                            prestamo_id = int(input("Ingrese el ID del préstamo que desea consultar: "))
                            break  # Salir del bucle si la conversión a entero fue exitosa
                        except ValueError:
                            print("Error: Por favor, ingrese un número entero válido.")
                
                address_consult = input("Introduzca su address para hacer la consulta: ")
                
                 # Validación de address
                resultado = PrestamoDeFiInteractor.validar_address(address_consult)
                if resultado:
                        print(resultado)
                        continue
                
                consult_private_key = input ("Introduzca su clave privada: ")

                # Validar formato clave privada
                if not PrestamoDeFiInteractor.validar_clave_privada(consult_private_key):
                    print("Formato no válido")
                    continue

                 # firmar transacción
                try:

                    if not interactor.enviar_transaccion_firmada(address_consult,consult_private_key):
                        print("Clave privada no válida")
                        continue
                except Exception as e:
                        print("Hubo un problema al conectar con la blockchain: ",e)
                        continue

                 # Obtener los datos llamando a la función
                try:
                    respuesta = interactor.obtenerDetalleDePrestamo(prestatario_address, prestamo_id)
                    print(respuesta)

                except Exception as e:
                    print("Ocurrió una excepción al obtener la información: ",e)

            elif opcion == "0":
                print("Gracias por usar nuestro sistema de préstamos DeFi")
                break

            else:
                print("Opción inválida. Por favor, introduzca un número del 1 al 9.")

    else:
        print("No se pudo obtener una cuenta conectada.")


if __name__ == "__main__":
    main()