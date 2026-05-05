import os
from flask import Flask, request, jsonify
from pymongo import MongoClient
from flask_cors import CORS
from bson import ObjectId
from flasgger import Swagger

app = Flask(__name__)
CORS(app)

# Swagger config
swagger = Swagger(app)

# MongoDB conexión desde Render
mongo_uri = os.environ.get("MONGO_URI")

if not mongo_uri:
    raise Exception("Falta MONGO_URI")

client = MongoClient(mongo_uri)
db = client["clinica"]
pacientes = db["pacientes"]

# ---------------------- RUTAS ----------------------

@app.route("/")
def inicio():
    """
    Estado de la API
    ---
    responses:
      200:
        description: API funcionando
    """
    return "API funcionando"


@app.route("/api/pacientes", methods=["POST"])
def crear_paciente():
    """
    Crear un nuevo paciente
    ---
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - nombre
            - edad
            - nivel_ansiedad
          properties:
            nombre:
              type: string
              example: "Joaquin"
            edad:
              type: integer
              example: 22
            nivel_ansiedad:
              type: string
              example: "alto"
    responses:
      200:
        description: Paciente creado
    """
    data = request.json
    data["consultas"] = []
    resultado = pacientes.insert_one(data)
    return jsonify({"id": str(resultado.inserted_id)})


@app.route("/api/pacientes", methods=["GET"])
def obtener_pacientes():
    """
    Obtener todos los pacientes
    ---
    responses:
      200:
        description: Lista de pacientes
    """
    lista = []
    for p in pacientes.find():
        p["_id"] = str(p["_id"])
        lista.append(p)
    return jsonify(lista)


@app.route("/api/pacientes/ansiedad/<nivel>", methods=["GET"])
def filtrar_ansiedad(nivel):
    """
    Filtrar pacientes por nivel de ansiedad
    ---
    parameters:
      - name: nivel
        in: path
        type: string
        required: true
        example: alto
    responses:
      200:
        description: Lista filtrada
    """
    lista = []
    for p in pacientes.find({"nivel_ansiedad": nivel}):
        p["_id"] = str(p["_id"])
        lista.append(p)
    return jsonify(lista)


@app.route("/api/pacientes/<id>/consulta", methods=["POST"])
def agregar_consulta(id):
    """
    Agregar consulta a un paciente
    ---
    parameters:
      - name: id
        in: path
        type: string
        required: true
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            fecha:
              type: string
              example: "2026-05-05"
            notas:
              type: string
              example: "Evaluación inicial"
    responses:
      200:
        description: Consulta agregada
    """
    data = request.json
    pacientes.update_one(
        {"_id": ObjectId(id)},
        {"$push": {"consultas": data}}
    )
    return jsonify({"mensaje": "Consulta agregada"})


# ---------------------- RUN ----------------------

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)