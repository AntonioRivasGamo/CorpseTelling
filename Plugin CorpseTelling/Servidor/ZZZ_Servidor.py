import socket
import threading
import os
import xmltodict
import json

# Función para enviar un archivo XML por el puerto 5002
def enviar_xml():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("localhost", 5002))
    server.listen(1)
    print("Servidor enviando XML en puerto 5002...")

    while True:
        try:
            # Esperar a que un cliente se conecte
            conn, addr = server.accept()
            print(f"Conexión establecida con {addr}")

            ruta_xml = os.path.join("plugins", "CorpseTelling", "muertes.xml")

            # Leer el archivo XML
            with open(ruta_xml, "r", encoding="utf-8") as archivo:
                xml_data = archivo.read()

            # Convertir el XML a un diccionario
            xml_dict = xmltodict.parse(xml_data)

            # Convertir el diccionario a JSON
            json_data = json.dumps(xml_dict, indent=4, ensure_ascii=False)

            # Enviar el JSON al cliente
            conn.sendall(json_data.encode("utf-8"))
            print(f"Archivo XML convertido a JSON y enviado desde {ruta_xml}")

        except FileNotFoundError:
            print(f"Error: El archivo {ruta_xml} no se encontró.")
            conn.sendall(b"Error: Archivo no encontrado.")
        except Exception as e:
            print(f"Error al enviar el archivo XML: {e}")

        # Cerrar la conexión después de enviar el archivo
        conn.close()

# Función para recibir un String por el puerto 5003 y reenviarlo al puerto 5000
def recibir_y_reenviar():
    receiver = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    receiver.bind(("localhost", 5003))
    receiver.listen(1)
    print("Servidor escuchando en puerto 5003...")

    while True:
        try:
            conn, addr = receiver.accept()  # No hay timeout, espera indefinidamente
            print(f"Conexión establecida con {addr}")

            data = conn.recv(1024).decode("utf-8")
            print(f"Recibido en 5003: {data}")

            # Crear un nuevo socket en cada iteración
            sender = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sender.connect(("localhost", 5000))
            sender.sendall(data.encode("utf-8"))
            print(f"Reenviado a 5000: {data}")

            conn.close()
            sender.close()  # Cerrar el socket después de usarlo
        except Exception as e:
            print(f"Error al recibir y reenviar datos: {e}")


# Función para escuchar en el puerto 5001 y enviar lo escuchado al puerto 5004
def escuchar_y_enviar():
    receiver = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    receiver.bind(("localhost", 5001))
    receiver.listen(1)
    print("Servidor escuchando en puerto 5001...")

    sender = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    while True:
        try:
            conn, addr = receiver.accept()  # No hay timeout, espera indefinidamente
            print(f"Conexión establecida con {addr}")

            data = conn.recv(1024).decode("utf-8")
            print(f"Recibido en 5001: {data}")

            sender.connect(("localhost", 5004))
            sender.sendall(data.encode("utf-8"))
            print(f"Enviado a 5004: {data}")

            conn.close()
            sender.close()
        except Exception as e:
            print(f"Error al escuchar y enviar datos: {e}")

# Crear y ejecutar los hilos para las diferentes tareas
if __name__ == "__main__":
    threading.Thread(target=enviar_xml).start()
    threading.Thread(target=recibir_y_reenviar).start()
    threading.Thread(target=escuchar_y_enviar).start()