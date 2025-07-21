from opcua import Client
def escribir_dato_opcua(url, node_id, valor):
    try:
        client = Client(url)
        client.connect()
        client.get_node(node_id).set_value(valor)
        client.disconnect()
        return "Valor escrito correctamente"
    except Exception as e:
        return f"Error: {str(e)}"
