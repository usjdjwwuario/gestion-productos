from flask import Flask
from pymongo import MongoClient

app = Flask(__name__)
app.config["UPLOAD_FOLDER"]="./static/imagenes"



conexion = MongoClient("mongodb://localhost:27017")

db = conexion["Datosss"]

categorias = db["Categorias"]
productos = db["productos"]
usuarios = db["usuarios"]


from controlador.productoController import *
from controlador.categoriaController import *
from controlador.usuarioContoller import *

if __name__=="__main__":
    app.run(port=5000, host="0.0.0.0", debug=True)
