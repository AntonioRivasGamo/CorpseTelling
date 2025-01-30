from flask import Flask, request, jsonify
import socket
import json

app = Flask(__name__)

# Configuración de timeouts (en segundos)
SOCKET_TIMEOUT = 5  # Tiempo de espera para conexiones y recepción de datos

# Función para enviar un comando al puerto 5003
@app.route('/enviarComando', methods=['POST'])
def enviar_comando():
    try:
        # Extraer el comando del cuerpo de la solicitud
        data = request.get_json(force=True)  # Forzar conversión a JSON si llega como string
        if not data or "comando" not in data:
            return jsonify({"status": "error", "message": "El campo 'comando' es obligatorio"}), 400

        comando = data["comando"]

        # Crear conexión de socket
        sender = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sender.settimeout(SOCKET_TIMEOUT)
        sender.connect(("localhost", 5003))

        # Enviar el comando
        sender.sendall(comando.encode("utf-8"))
        sender.close()

        return jsonify({"status": "success", "message": "Comando enviado correctamente"}), 200
    except Exception as e:
        print(f"Error al enviar comando: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

# Función para escuchar el JSON en el puerto 5002
def escuchar_json():
    try:
        receiver = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        receiver.settimeout(SOCKET_TIMEOUT)  # Establecer timeout
        receiver.connect(("localhost", 5002))

        # Recibir datos en bloques de 4096 bytes
        json_data = ""
        while True:
            chunk = receiver.recv(4096).decode("utf-8")
            if not chunk:
                break
            json_data += chunk

        receiver.close()
        return json_data
    except Exception as e:
        print(f"Error al escuchar JSON: {e}")
        return None

# Endpoint para obtener las muertes
@app.route('/obtenerMuertes', methods=['GET'])
def obtener_muertes():
    json_data = escuchar_json()  # Obtener el JSON del servidor de sockets
    if json_data:
        try:
            # Convertir el JSON a un diccionario
            json_dict = json.loads(json_data)

            # Extraer la lista de muertes
            if "muertes" in json_dict:
                muertes = json_dict["muertes"]
                # Verificar si hay una muerte en el JSON
                if "muerte" in muertes:
                    # Crear una lista con la muerte encontrada
                    muertes_simplificadas = [muertes["muerte"]]
                    return jsonify({"status": "success", "muertes": muertes_simplificadas}), 200
                else:
                    return jsonify({"status": "error", "message": "No se encontró la clave 'muerte' en el JSON"}), 500
            else:
                return jsonify({"status": "error", "message": "No se encontró la clave 'muertes' en el JSON"}), 500
        except json.JSONDecodeError as e:
            return jsonify({"status": "error", "message": "El JSON recibido no está bien formado"}), 500
    else:
        return jsonify({"status": "error", "message": "Error al obtener las muertes"}), 500

if __name__ == "__main__":
    # Iniciar el servidor Flask en el puerto 5005
    app.run(port=5005, debug=True)
