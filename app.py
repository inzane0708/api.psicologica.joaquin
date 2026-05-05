import os
from flask import Flask, request, jsonify
from pymongo import MongoClient
from flask_cors import CORS
from bson import ObjectId

app = Flask(__name__)
CORS(app)

mongo_uri = os.environ.get("MONGO_URI")

if not mongo_uri:
    raise Exception("No se encontró la variable MONGO_URI")

client = MongoClient(mongo_uri)
db = client["clinica"]
pacientes = db["pacientes"]

@app.route("/")
def inicio():
    return "API funcionando"

@app.route("/api/pacientes", methods=["POST"])
def crear_paciente():
    data = request.json
    data["consultas"] = []
    resultado = pacientes.insert_one(data)
    return jsonify({"id": str(resultado.inserted_id)})

@app.route("/api/pacientes", methods=["GET"])
def obtener_pacientes():
    lista = []
    for p in pacientes.find():
        p["_id"] = str(p["_id"])
        lista.append(p)
    return jsonify(lista)

@app.route("/api/pacientes/ansiedad/<nivel>", methods=["GET"])
def filtrar_ansiedad(nivel):
    lista = []
    for p in pacientes.find({"nivel_ansiedad": nivel}):
        p["_id"] = str(p["_id"])
        lista.append(p)
    return jsonify(lista)

@app.route("/api/pacientes/<id>/consulta", methods=["POST"])
def agregar_consulta(id):
    data = request.json
    pacientes.update_one(
        {"_id": ObjectId(id)},
        {"$push": {"consultas": data}}
    )
    return jsonify({"mensaje": "Consulta agregada"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)