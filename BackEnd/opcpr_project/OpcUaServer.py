# backend/app/opcua_server.py
from opcua import Server
from datetime import datetime
def iniciar_servidor_opcua(url, node_id):
    try:
        server = Server()
        server.set_endpoint(url)
        uri = "http://example.org"
        server.register_namespace(uri)

        # Crear un nodo
        objeto = server.nodes.objects.add_object(uri, "MyObject")
        variable = objeto.add_variable(uri, "MyVariable", 0.0)
        variable.set_writable()  # Hacer la variable escribible

        # Iniciar el servidor
        server.start()
        print(f"Servidor OPC UA iniciado en {url}")

        try:
            while True:
                # Actualizar el valor de la variable cada segundo
                variable.set_value(datetime.now().timestamp())
                time.sleep(1)
        finally:
            server.stop()
            print("Servidor OPC UA detenido")
    except Exception as e:
        print(f"Error: {str(e)}")