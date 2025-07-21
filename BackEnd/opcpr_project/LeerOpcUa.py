from opcua import Client

def leer_dato_opcua(url, node_id):
    try:
        client = Client(url)
        client.connect()
        valor = client.get_node(node_id).get_value()
        client.disconnect()
        return valor
    except Exception as e:
        return f"Error: {str(e)}"